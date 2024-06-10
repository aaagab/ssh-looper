#!/usr/bin/env python3
from pprint import pprint
import json
import os
import re
import shlex
import socket
import signal
import subprocess
import sys
import tempfile
import time
import platform
import psutil

from ..gpkgs import message as msg
from ..gpkgs import shell_helpers as shell

def short_ping(network):
        count_arg=""
        null_arg=""
        if platform.system() == "Windows":
            count_arg="-n"
            null_arg="> nul 2>&1"
        elif platform.system() == "Linux":
            count_arg="-c"
            null_arg="> /dev/null 2>&1"

        cmd="ping {} 4 {} {}".format(count_arg, network, null_arg)
        print(cmd)
        if os.system(cmd) == 0:
            return True
        else:
            return False

def resolve(hostname, dns):
    cmd="nslookup {} {}".format(hostname, dns)
    print(cmd)
    ns=shell.cmd_get_value(cmd)
    found=False
    computer_ip=None
    for line in ns.splitlines():
        if re.match(r"^Name:\s+{}$".format(hostname), line):
            found=True
            continue

        if found is True:
            reg=re.match(r"^Address:\s+(.+)$", line)
            if reg:
                computer_ip=reg.group(1)
                break

    return computer_ip

def ssh_looper_clear():
    # lines=shell.cmd_get_value("ps auxfww").splitlines()
    python_cmds=[]
    ssh_cmds=[]

    for proc in psutil.process_iter():
        if proc.name() in ["python", "python.exe", "python3", "python3.exe", "ssh", "ssh.exe"]:
            cmdline=shlex.join(proc.cmdline())
            if "ssh -N -L" in cmdline or "ssh -N -R" in cmdline:
                # elems=line.split()
                # cmd=" ".join(elems[10:])
                if "python" in cmdline:
                    python_cmds.append([proc.pid, cmdline])
                else:
                    ssh_cmds.append([proc.pid, cmdline])    

    # for line in lines:
    #     if "ssh -N -L" in line or "ssh -N -R" in line:
    #         elems=line.split()
    #         pid=int(elems[1])
    #         cmd=" ".join(elems[10:])
    #         if "python" in cmd:
    #             python_cmds.append([pid, cmd])
    #         else:
    #             ssh_cmds.append([pid, cmd])

    for cmds in [python_cmds, ssh_cmds]:
        for pid, cmd in cmds:
            os.kill(pid, signal.SIGTERM)
            msg.success("ssh-looper: cleared: '{}'".format(cmd))

def ssh_looper(cmd, dns=None, unknown_host=False):
    # ssh -N -L {port}:localhost:{port} {user}@{ip_name}
    # ssh -N -R {port}:localhost:{port} {user}@ip_name
    cmd=cmd.strip()
    reg=re.match(r"^(?P<cmd_start>ssh\s+-N\s+-(?P<sshtype>L|R)\s+(?P<leftport>[0-9]+):localhost:(?P<rightport>[0-9]+)\s+.+?@)(?P<network>[^ ]+)(?P<key>\s+-i\s+[^ ]+)?$", cmd)
    if not reg:
        msg.error("ssh-looper: ssh cmd is not supported see readme '{}'".format(cmd), exit=1)

    sshtype=reg.group("sshtype")
    localport=None
    remoteport=None
    pid_script=os.getpid()
    if sshtype == "L":
        localport=int(reg.group("leftport"))
        remoteport=int(reg.group("rightport"))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex(('127.0.0.1', localport))
        is_open=(result == 0)
        s.close()
        if is_open:
            msg.error("ssh-looper: port '{}' is already in use for command '{}'.".format(localport, cmd))
            sys.exit(1)
    else:
        localport=int(reg.group("rightport"))
        remoteport=int(reg.group("leftport"))
        for proc in psutil.process_iter():
            if proc.name() in ["ssh", "ssh.exe"]:
                line=shlex.join(proc.cmdline())
                if ("{}:localhost:{}".format(remoteport, localport) in line and proc.pid != pid_script):
                    msg.error("ssh-looper: port '{}' is already is already forwarded for command '{}'.".format(localport, cmd))
                    sys.exit(1)

    network=reg.group("network")
    cmd_start=reg.group("cmd_start")
    cmd_end=""
    if "cmd_end" in reg.groupdict():
        cmd_end=reg.group("cmd_end")
        if cmd_end is None:
            cmd_end=""

    key=""
    if "key" in reg.groupdict():
        key=reg.group("key")
        if key is None:
            key=""

    pause=10
    try:
        while True:
            network_to_ping=network
            if dns is not None:
                resolved_network=resolve(network_to_ping, dns)
                if resolved_network is None:
                    time.sleep(pause)
                    continue
                else:
                    network_to_ping=resolved_network
            if short_ping(network_to_ping) is True:
                try:
                    # ExitOnForwardFailure allows ssh to fail on forward failure
                    tmp_cmd=cmd_start+network_to_ping+cmd_end+key+" -o ExitOnForwardFailure=yes"

                    if unknown_host is True:
                        tmp_cmd+=" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
                    print(tmp_cmd)
                    proc = subprocess.Popen(shlex.split(tmp_cmd))
                    proc.communicate()
                    time.sleep(pause)
                except KeyboardInterrupt:
                    break
                except BaseException as e:
                    print(e)
                    time.sleep(pause)
                    continue
            else:
                time.sleep(pause)
    except KeyboardInterrupt:
        pass

