import argparse
from .core import cli
import shutil
from .core.core import MindFlow, Profile
from .core.utils.general import ROOT_DIR
import asyncio
import toml
import os

from pathlib import Path
from rich.console import Console
from rich.text import Text

from rich_argparse import RichHelpFormatter

# Create a console object
console = Console()

def parse_args():
    RichHelpFormatter.styles["argparse.groups"] = "bold"
    RichHelpFormatter.styles["argparse.args"] = "#79c0ff"
    RichHelpFormatter.styles["argparse.metavar"] = "#2a6284"
    

    parser = argparse.ArgumentParser(
        description="[#92c7f5]O[/#92c7f5][#8db9fe]pe[/#8db9fe][#9ca4eb]nm[/#9ca4eb][#bbb2ff]a[/#bbb2ff][#d3aee5]cr[/#d3aee5][#caadea]o[/#caadea] is a multimodal assistant, code interpreter, and human interface for computers. [dim](0.1.17)[/dim]",
        formatter_class=RichHelpFormatter
    )
    
    parser.add_argument("--default", action="store_true", help="Switch back to default settings.")
    parser.add_argument("--api_key", metavar='<api_key>', type=str, help="Set your API KEY for SambaNova API.")
    parser.add_argument("--save", action="store_true", help="Save current `profile.toml` settings for future uses.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose mode for debugging.")
    parser.add_argument("--profile", metavar='<path>', type=str, help="Path to a `profile.toml` file for custom settings.")
    parser.add_argument("--profiles", action="store_true", help="List all available `profiles`.")
    parser.add_argument("--switch", metavar='<name>:<version>', type=str, help="Switch to a different profile's custom settings.")

    args = parser.parse_args()
    kwargs = {}
    path = Path(ROOT_DIR, "profile.template.toml")
    
    
    if args.api_key:
        with open(Path(ROOT_DIR, ".env"), "w") as f:
            f.write(f'API_KEY="{args.api_key}"')
            if profile: f.write(f'\nPROFILE="{profile}"')
        os.environ["API_KEY"] = args.api_key
        
    if args.profiles:
        profiles = set(profiles.name 
                       for profiles in Path(ROOT_DIR, "profiles").iterdir())
        print(f"Profiles Available: {profiles}")
        exit()
        
    if args.verbose:
        kwargs["verbose"] = True
        
    if args.profile:
        # check if file exists
        path = args.profile
        if not Path(path).is_file():
            raise FileNotFoundError(f"Path to `{args.profile}` could not be found")
        
        # check for required fields
        with open(args.profile, "r") as f:
            profile = toml.loads(f.read()).get("profile")
        if not profile:
            raise KeyError(f"`profile` field not found in `{args.profile}`")
        
        # check for duplicates
        name, version = profile.get("name"), profile.get("version", "1.0.0")
        path = Path(ROOT_DIR, "profiles", name, version, "profile.toml")
        
        if args.save:
            override = False
            if Path(path).is_file():
                override = input("""It seems another profile with the same name and version already exists. 
                                    Would you like to override this profile? (y/n)""").startswith("y")
            
                if not override:
                    raise FileExistsError("profile with the same name and version already exists")
            
            shutil.copyfile(path, str(path))   
            
            with open(Path(ROOT_DIR, ".env"), "w") as f:
                f.write(f'API_KEY="{os.environ["API_KEY"]}"')
                f.write(f'\nPROFILE="{name}:{version}"')
                
    if args.default:
        return kwargs
        
    if (profile := args.switch) or (profile := os.environ.get("PROFILE")):
        
        profile = profile.split(":")
        if len(profile) >= 2: name, version = profile[0], profile[-1]
        else: name, version = profile[0], None
        
        profiles = set(profiles.name 
                       for profiles in Path(ROOT_DIR, "profiles").iterdir())
        
        if not name in profiles:
            raise KeyError("Profile does not exist.") 
        
        versions = set(versions.name
                       for versions in Path(ROOT_DIR, "profiles", name).iterdir())
        
        if not version:
            version = sorted(list(versions))[-1]
        elif not version in versions:
            raise KeyError("Version does not exist.") 
        
        path = Path(ROOT_DIR, "profiles", name, version, "profile.toml")
        with open(Path(ROOT_DIR, ".env"), "w") as f:
            f.write(f'API_KEY="{os.environ["API_KEY"]}"')
            f.write(f'\nPROFILE="{name}:{version}"')
        os.environ["PROFILE"] = f"{name}:{version}"
        
    kwargs["profile"] = Profile(path)
    return kwargs

def main():
    args = parse_args()
    macro = MindFlow(**args)
    asyncio.run(cli.main(macro))

if __name__ == "__main__":
    main()
