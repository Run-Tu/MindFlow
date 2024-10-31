import argparse
from ..computer import Computer
from ..utils import ROOT_DIR
from pathlib import Path
import subprocess
from rich_argparse import RichHelpFormatter

def main():
    RichHelpFormatter.styles["argparse.groups"] = "bold"
    RichHelpFormatter.styles["argparse.args"] = "#79c0ff"
    RichHelpFormatter.styles["argparse.metavar"] = "#2a6284"

    parser = argparse.ArgumentParser(
        description="[#92c7f5]o[/#92c7f5][#8db9fe]m[/#8db9fe][#9ca4eb]i[/#9ca4eb] is the package manager for mindflow. [dim](0.0.1)[/dim]",
        formatter_class=RichHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Sub-command help')

    install_parser = subparsers.add_parser('install', help='Install a module through `pip` and add it to mindflow path')
    install_parser.add_argument('module_name', metavar='<module_name>', type=str, help='Module name to install')

    add_parser = subparsers.add_parser('add', help='Add extension to `mindflow.extensions` path')
    add_parser.add_argument('module_name', metavar='<module_name>', type=str, help='Module name to add')

    remove_parser = subparsers.add_parser('remove', help='Remove extension from `mindflow.extensions` path')
    remove_parser.add_argument('module_name', metavar='<module_name>', type=str, help='Module name to remove')

    args = parser.parse_args()
    pip = [Computer().supported["python"][0], "-m", "pip", "install"]
    
    if args.command == 'install':
        subprocess.run(pip + [args.module_name])
        with open(Path(ROOT_DIR, "extensions", "extensions.txt"), "a") as f:
            f.write("\n" + args.module_name)
    
    elif args.command == 'add':
        with open(Path(ROOT_DIR, "extensions", "extensions.txt"), "a") as f:
            f.write("\n" + args.module_name)
            
    elif args.command == 'remove':
        with open(Path(ROOT_DIR, "extensions", "extensions.txt"), "r") as f:
            extensions = f.read().splitlines()
        
        extensions = [ext for ext in extensions if ext != args.module_name]
        
        with open(Path(ROOT_DIR, "extensions", "extensions.txt"), "w") as f:
            f.write("\n".join(extensions))

if __name__ == "__main__":
    main()
