import typer
import json
from typing import List, Optional
from typing_extensions import Annotated
from pathlib import Path

from .configurations import BaseProjectConfiguration
from .exceptions import ProjectBuildError, ProjectRunError
from ..helpers.uv import UVExecution
from ..helpers.git import GitExecution

app = typer.Typer()

@app.command("print")
def testing_cli_function(personal_config: bool = False):
    """
    Display Known Information about the current project
    """
    app_dir = typer.get_app_dir("rubberduckbuildcli")
    config_path: Path = Path(app_dir) / "config.json"
    if personal_config:
        with open(config_path, 'r') as file: 
            personal_config_file = json.load(file)
        print(personal_config_file)
    project_config = BaseProjectConfiguration()
    if project_config.config_exists():
        print("Configuration Exists")
        print(f"Project Path: {project_config.project_config_file_path}")
        project_config.load_config()
        project_config.print_config()
        

@app.command()
def init(app: str = "default", version:str = "0.1.0", skip_init: bool = False):
    """
    Initialize a project
    :param app:
    :param version:
    :return:
    """
    # Create RubberDuckProject.json
    # Initialize Python Project (UV)
    uv = UVExecution()
    git = GitExecution()
    app_dir = typer.get_app_dir("rubberduckbuildcli")
    config_path: Path = Path(app_dir) / "config.json"
    with open(config_path, 'r') as file: 
        user_config = json.load(file)

    if not skip_init:
        print(f"Initialize {app} version {version}")
        project_config = BaseProjectConfiguration()
        if project_config.config_exists(throw_error=False):
            pass
        else: 
            project_config.create_default_config(project_name=app)
        uv.run_command(args=["init"])
    # Add default Packages 
    print("Installing/Updating Default Packages")
    default_packages = ["ruff"]
    uv.install(packages=default_packages, upgrade=True)
    
    # Create the initial Folder Paths
    # Display Information and helpful hints
    # Configure git based on CLI Configs
    print("Configure git local settings.")
    if user_config.get('git'):
        git.set_local_config(username=user_config.get('git').get('username', 'whoops'), 
                             email=user_config.get('git').get('email', 'whoops@rubberduck-labs.com'))

@app.command()
def dependency_add(package: Annotated[Optional[List[str]], typer.Option()] = None ):
    """
    Add dependecy to project.
    """
    uv = UVExecution()
    to_install_packages = []
    if not package:
        raise typer.Abort()
    for p in package:
        print(f"Installing Package {p}")
        to_install_packages.extend([p])
    uv.install(packages=to_install_packages)


@app.command()
def dependency_remove(package: Annotated[Optional[List[str]], typer.Option()] = None ):
    """
    Remove dependecy to project.
    """
    uv = UVExecution()
    to_remove_packages = []
    if not package:
        raise typer.Abort()
    for p in package:
        print(f"Removing Package {p}")
        to_remove_packages.extend([p])
    uv.uninstall(packages=to_remove_packages)

@app.command("build")
def project_build():
    """
    Build the package
    """
    uv = UVExecution()
    print("Checking Formatting and Sytling")
    format_result = uv.run_command(["run", "ruff", "check"])
    if format_result != 0:
        raise ProjectBuildError("Ruff Checks Failed")
    
    print("Building Application")

    uv.run_command(["build"])

@app.command("run")
def run_project():
    """
    Run Project ExtraCommand Run
    """
    project_config = BaseProjectConfiguration()
    if project_config.config_exists():
        print("Configuration Exists")
        print(f"Project Path: {project_config.project_config_file_path}")
        project_config.load_config()
        project_commands = project_config.project_configuration.get("ExtraCommands")
        config_run_command = [cmd for cmd in project_commands if cmd.get('run')]
        if config_run_command:
            run_command = ['run']
            run_command.extend(config_run_command[0].get('run').split(' '))
            uv = UVExecution()
            uv.run_command(run_command)
        else: 
            raise ProjectRunError("No Run Command Found")            


if __name__=="__main__":
    app()