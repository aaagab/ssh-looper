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

    # args, dy_app=pkg.Options(filenpa_app="gpm.json", filenpa_args="config/options.json").get_argsns_dy_app()

    def seed(pkg_major, direpas_configuration=dict(), fun_auto_migrate=None):
        fun_auto_migrate()
    etconf=pkg.Etconf(enable_dev_conf=False, tree=dict(), seed=seed)

    nargs=pkg.Nargs(
        metadata=dict(executable="scriptjob"), 
        options_file="config/options.yaml",
        path_etc=etconf.direpa_configuration,
        raise_exc=True,
    )
    args=nargs.get_args()

    # if args.examples._here is True:
    #     print(re.sub(r"\n\s+", "\n",
    #     """
    #         # supported commands are:
    #         ssh -N -L 2222:localhost:2222 user@domain.com
    #         ssh -N -L 2222:localhost:2222 user@domain.com --resolve 123.123.123.123
    #         ssh user@192.168.56.1 -N -R 2222:localhost:22
    #     """).strip())
    # el
    if args.cmd._here:
        pkg.ssh_looper(
            cmd=args.cmd._value,
            dns=args.cmd.resolve._value,
            unknown_host=args.cmd.unknown._here,
        )
    elif args.list._here:
        pkg.ssh_looper_clear(to_list=True)
    elif args.clear._here:
        pkg.ssh_looper_clear()