import argparse
from .core import cli
import shutil
from .core.core import MindFlow, Profile
from .core.utils.general import ROOT_DIR

from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Description of your script.")
    
    parser.add_argument('--default', action='store_true', help='Switch back to default settings.')
    parser.add_argument('--save', action='store_true', help='Save current `config.toml` settings for future uses.')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose mode for debugging.')
    parser.add_argument('--config', type=str, help='Path to a `config.toml` file for custom settings.')

    args = parser.parse_args()
    kwargs = {'verbose': args.verbose}
    
    if args.default:
        return kwargs
    
    path = args.config if args.config else 'config.toml'
    root = Path(ROOT_DIR, 'config.toml')
    
    if not Path(path).is_file():
        path = root
        
    if not root.is_file():
        root.touch()
            
    kwargs['profile'] = Profile(root)
    
    if args.save and args.config:
        shutil.copyfile(args.config, str(root))
    return kwargs


def main():
    args = parse_args()
    macro = MindFlow(**args)
    cli.main(macro)

if __name__ == "__main__":
    main()
