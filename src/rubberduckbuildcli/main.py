import json
from pathlib import Path
import typer

import rubberduckbuildcli.projects as projects


class CLIException(Exception):
    pass

class CLINoConfigException(CLIException):
    pass

app = typer.Typer()
app.add_typer(projects.app, name="project")


@app.command("configure")
def configure_cli_options(show: bool = False):
    app_dir = typer.get_app_dir("rubberduckbuildcli")
    config_path: Path = Path(app_dir) / "config.json"
    if not show:
        username = typer.prompt("What is your name?")
        user_email = typer.prompt("What is your email?")
        default_config = {
            "git": {
                "username": username,
                "email": user_email
            },
            "projects": {
                "directory": "~/projects"
            }
        }
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w') as config_file:
            json.dump(default_config, config_file, indent=4)
        print("Configuration Created")
    else:
        if config_path.is_file():
            with open(config_path, 'r') as file: 
                    personal_config_file = json.load(file)
            for key, value in personal_config_file.items(): 
                print(f"{key} Configuration")
                for subkey, subvalue in value.items(): 
                    print(f"    {subkey} = {subvalue}")
        else: 
            print("No Config file found")



@app.callback(invoke_without_command=True)
def check_config_file(ctx: typer.Context):
    if ctx.invoked_subcommand == "configure":
        return

    app_dir = typer.get_app_dir("rubberduckbuildcli")
    config_path: Path = Path(app_dir) / "config.json"
    if not config_path.is_file():
        print(f"Personal Config file doesn't exist yet: {config_path}")
        raise CLINoConfigException("No Personal Configuration... Run rdb configure")


if __name__ == "__main__":
    app()

