#!/usr/bin/env python3

if __name__ == "__main__":
    import importlib
    import os
    import re
    import sys
    direpa_script_parent=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    module_name=os.path.basename(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, direpa_script_parent)
    pkg = importlib.import_module(module_name)
    del sys.path[0]

    args, dy_app=pkg.Options(filenpa_app="gpm.json", filenpa_args="config/options.json").get_argsns_dy_app()

    if args.examples.here is True:
        print(re.sub(r"\n\s+", "\n",
        """
            # supported commands are:
            ssh -N -L 2222:localhost:2222 user@domain.com
            ssh user@192.168.56.1 -N -R 2222:localhost:22
        """).strip())
    elif args.cmd.here:
        pkg.ssh_looper(
            cmd=args.cmd.value
        )