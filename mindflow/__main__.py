import argparse
from .core import MindFlow
from .utils import ROOT_DIR, merge_dicts, load_profile, lazy_import
import asyncio
import os

from .cli import main as run_cli

from pathlib import Path
from rich_argparse import RichHelpFormatter

def parse_args():
    from .profile.template import profile
    
    RichHelpFormatter.styles["argparse.groups"] = "bold"
    RichHelpFormatter.styles["argparse.args"] = "#79c0ff"
    RichHelpFormatter.styles["argparse.metavar"] = "#2a6284"

    parser = argparse.ArgumentParser(
        description="[#92c7f5]O[/#92c7f5][#8db9fe]pe[/#8db9fe][#9ca4eb]nm[/#9ca4eb][#bbb2ff]a[/#bbb2ff][#d3aee5]cr[/#d3aee5][#caadea]o[/#caadea] is a multimodal assistant, code interpreter, and human interface for computers. [dim](0.2.8)[/dim]",
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
    Path(ROOT_DIR, "profiles").mkdir(exist_ok=True) 
    path: Path | str = ""
    
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
        profile["config"]["verbose"] = True
        
    if args.profile:
        # check if file exists
        args_path = Path(args.profile)
        if not args_path.is_file():
            raise FileNotFoundError(f"Path to `{args.profile}` could not be found")
        
        # check for required fields
        args_profile = load_profile(args.profile)
        user_profile = args_profile.get("user")
        
        if not user_profile:
            raise KeyError(f"`profile` field not found in `{args.profile}`")
        
        # check for duplicates
        name, version = user_profile.get("name"), user_profile.get("version", "1.0.0")
        path = Path(ROOT_DIR, "profiles", name, version, "profile.json")
        
        if args.save:
            override = False
            if Path(path).is_file():
                override = input("""It seems another profile with the same name and version already exists. Would you like to override this profile? (y/n)""").startswith("y")
            
                if not override:
                    raise FileExistsError("profile with the same name and version already exists")
            
            # copy file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
            json = lazy_import("json", optional=False)
            with open(path, "w") as f: 
                f.write(json.dumps(args_profile)) 
            
            with open(Path(ROOT_DIR, ".env"), "w") as f:
                f.write(f'API_KEY="{os.environ["API_KEY"]}"')
                f.write(f'\nPROFILE="{name}:{version}"')
            os.environ["PROFILE"] = f"{name}:{version}"
                
    if args.default:
        return profile | {"path": Path(ROOT_DIR, "profile", "template.py")}
        
    if (args_profile := args.switch) or (args_profile := os.environ.get("PROFILE")):
        
        args_profile = args_profile.split(":")
        if len(args_profile) >= 2: name, version = args_profile[0], args_profile[-1]
        else: name, version = args_profile[0], None
          
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
        
        path = Path(ROOT_DIR, "profiles", name, version, "profile.json")
        
        with open(Path(ROOT_DIR, ".env"), "w") as f:
            f.write(f'API_KEY="{os.environ["API_KEY"]}"')
            f.write(f'\nPROFILE="{name}:{version}"')
        os.environ["PROFILE"] = f"{name}:{version}"
    
    if path:
        return merge_dicts(profile, load_profile(path)) | {"path": path}
    return profile | {"path": Path(ROOT_DIR, "profile", "template.py")}

def main():
    profile = parse_args()
    macro = MindFlow(profile)
    asyncio.run(run_cli(macro))

if __name__ == "__main__":
    main()
