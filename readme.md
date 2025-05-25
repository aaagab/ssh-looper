# ssh-looper

This software reconnect ssh indefinitely.  

- help: `main.py -h`
- examples: `main.py -he`
- full usage: `main.py -uid=-1`

## Accepted ssh cmd syntax
```bash
ssh -N -L {port}:localhost:{port} {user}@{ip_name}
ssh {user}@{ip_name} -N -R {port}:localhost:{port}
```

## check ssh connection
```bash
netstat -tunlp
# kill connection like that
lsof -i tcp:2222 | grep LISTEN | awk '{print $2}' | xargs kill
```