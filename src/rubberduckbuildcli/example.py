import typer
from rich import print
from rich.console import Console
from rich.table import Table

console = Console()

def main(app: str, version: str, production: bool= False, output: str = "text"):
    """
    Simple CLI for testing

    """
    if production:
        if output != "text":
            output_table(app, version)
            return
        print("[bold red]Production![/bold red]")
        print(f"Application: {app} \nVersion: {version}")
    else:
        if output != "text":
            output_table(app, version)
            return
        print("[bold green]Development[/bold green]")
        print(f"Application: {app} \nVersion: {version}")

def output_table(app:str, version:str):
    table = Table("Application", "Version")
    table.add_row(app, version)
    console.print(table)


if __name__ == "__main__":
    typer.run(main)