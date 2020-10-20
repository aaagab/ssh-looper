# ssh-looper

> follow syntax
```bash
ssh -N -L {port}:localhost:{port} {user}@{ip_name}
ssh {user}@{ip_name} -N -R {port}:localhost:{port}
```

> to test
```bash
# kill connection like that
lsof -i tcp:2222 | grep LISTEN | awk '{print $2}' | xargs kill
```