#!/usr/bin/env python3
from pprint import pprint
import os
import re
import sys
import time
import platform

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

def ssh_looper(cmd, dns=None):
    # ssh -N -L {port}:localhost:{port} {user}@{ip_name}
    # ssh {user}@ip_name -N -R {port}:localhost:{port}
    cmd=cmd.strip()
    reg=re.match(r"^ssh\s+-N\s+-L\s+[0-9]+:localhost:[0-9]+\s+.+?@(?P<network>[^ ]+)$", cmd)
    if not reg:
        reg=re.match(r"^ssh\s+.+?@(?P<network>[^ ]+)\s+-N\s+-R\s+[0-9]+:localhost:[0-9]+$", cmd)
        if not reg:
            msg.error("ssh cmd is not supported see readme '{}'".format(cmd), exit=1)

    network=reg.group("network")

    try:
        while True:
            network_to_ping=network
            if dns is not None:
                resolved_network=resolve(network_to_ping, dns)
                if resolved_network is None:
                    time.sleep(5)
                    continue
                else:
                    network_to_ping=resolved_network
            if short_ping(network_to_ping) is True:
                try:
                    print(cmd)
                    os.system(cmd)
                    time.sleep(5)
                except KeyboardInterrupt:
                    break
                except BaseException as e:
                    print(e)
                    continue
            else:
                time.sleep(10)
    except KeyboardInterrupt:
        pass

