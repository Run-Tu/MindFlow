import argparse
from .core import MindFlow
from .utils import ROOT_DIR, merge_dicts, load_profile, lazy_import, env_safe_replace
import asyncio
import os

from .cli import main as run_cli

from pathlib import Path
from rich_argparse import RichHelpFormatter

from dotenv import load_dotenv
load_dotenv()

class ArgumentParser(argparse.ArgumentParser):
    def __init__(self,
                 styles: dict,
                 default: dict,
                 *args, **kwargs):
        
        self.default = default
        self.profile = default
        Path(ROOT_DIR, ".env").touch()
        for title, style in styles.items():
            RichHelpFormatter.styles[title] = style
        
        super().__init__(formatter_class=RichHelpFormatter, 
                         *args, **kwargs)
        
        self.add_argument("--profiles", action="store_true", help="List all available `profiles`.")
        self.add_argument("--versions", metavar='<name>', help="List all available `versions` in a certain `profile`.")
        
        self.add_argument("--profile", metavar='<path>', type=str, help="Add custom profile to mindflow.")
        self.add_argument("--update", metavar='<name>', help="Update changes made in profile.")
        self.add_argument("--path", metavar='<path>', help="Add original path to profile for quick updates [BETA].")
        self.add_argument("--switch", metavar='<name>:<version>', type=str, help="Switch to a different profile's custom settings.")
        
        self.add_argument("--default", action="store_true", help="Switch back to default settings.")
        
        self.add_argument("--api_key", metavar='<api_key>', type=str, help="Set your API KEY for SambaNova API.")
        self.add_argument("--verbose", action="store_true", help="Enable verbose mode for debugging.")

    def parse(self) -> dict:
        if os.getenv("PROFILE"):
            self.parse_switch(os.getenv("PROFILE"))

        args = vars(self.parse_args())
        for arg, value in args.items():
            if value:
                getattr(self, "parse_" + arg)(value)
            
        return self.profile
    
    def parse_switch(self, value):
        value = value.split(":")
        name, version = value[0], value[-1]
        
        path = Path(ROOT_DIR, "profiles", name)
        if not path.is_dir():
            raise FileNotFoundError(f"Profile `{value}` does not exist")
        
        if not len(value) == 2:
            versions = [versions.name for versions in Path(ROOT_DIR, "profiles", name).iterdir()]
            version = sorted(versions)[-1]
        
        env_safe_replace(Path(ROOT_DIR, ".env"),
                        {"PROFILE":f"{name}:{version}"})
        
        self.profile = merge_dicts(self.profile, load_profile(Path(path, version, "profile.json")))
        
    def parse_path(self, value):
        name, version = os.getenv("PROFILE", "").split(":") or ("User", "1.0.0")
        env = Path(ROOT_DIR, "profiles", name, ".env")
        env.parent.mkdir(exist_ok=True) 
        env.touch()
        env_safe_replace(env, {"ORIGINAL_PROFILE_PATH": value})
    
    def parse_api_key(self, value):
        self.profile["env"]["api_key"] = value
        
    def parse_verbose(self, value):
        self.profile["config"]["verbose"] = True
    
    def parse_default(self, value):
        self.profile = self.default
    
    def parse_profiles(self, value):
        profiles = set(profiles.name 
                       for profiles in Path(ROOT_DIR, "profiles").iterdir())
        print(f"Profiles Available: {profiles}")
    
    def parse_versions(self, value):
        profiles = set(profiles.name 
                       for profiles in Path(ROOT_DIR, "profiles", value).iterdir()
                       if profiles.is_dir())
        print(f"Versions Available: {profiles}")
        
    def parse_update(self, name):
        toml = lazy_import("toml")
        env = Path(ROOT_DIR, "profiles", name, ".env")
        
        if not env.is_file():
            raise FileNotFoundError("`.env` missing from profile. Add `.env` by calling `macro --path <path>`.")
        
        with open(env, "r") as f:
            args_path = Path(toml.load(f)["ORIGINAL_PROFILE_PATH"])
            
        if not args_path.is_file():
            raise FileNotFoundError(f"Original profile path `{args_path}` has been moved. Update original profile path by calling `macro --path <path>`.")
        
        profile = load_profile(args_path)
        versions = [versions.name
                    for versions in Path(ROOT_DIR, "profiles", name).iterdir()]
        latest = sorted(versions)[-1]

        if latest > (version := profile["user"].get("version", "1.0.0")):
            version = latest
            
        major, minor, patch = map(int, version.split("."))
        profile["user"]["version"] = f"{major}.{minor}.{patch+1}"
        
        self.profile = merge_dicts(self.profile, profile)
        
    def parse_profile(self, path):
        self.profile = merge_dicts(self.profile, load_profile(path))
        self.profile["env"]["path"] = path
    
def main():
    Path(ROOT_DIR, "profiles").mkdir(exist_ok=True) 
    from .profile.template import profile
    
    parser = ArgumentParser(
        styles={
            "argparse.groups":"bold",
            "argparse.args": "#79c0ff",
            "argparse.metavar": "#2a6284"
            },
        default=profile,
        description="[#92c7f5]O[/#92c7f5][#8db9fe]pe[/#8db9fe][#9ca4eb]nm[/#9ca4eb][#bbb2ff]a[/#bbb2ff][#d3aee5]cr[/#d3aee5][#caadea]o[/#caadea] is a multimodal assistant, code interpreter, and human interface for computers. [dim](0.2.8)[/dim]",
        )
    
    profile = parser.parse()
    macro = MindFlow(profile)
    asyncio.run(run_cli(macro))

if __name__ == "__main__":
    main()
