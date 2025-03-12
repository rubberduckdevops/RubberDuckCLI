import subprocess



class GitExecution: 
    def __init__(self):
        pass
    
    def run_command(self, args: list[str]) -> int:
        """
        Run a git Command
        """
        try:
            result = subprocess.run(
                ["git"] + args, 
                capture_output=True, 
                text=True, 
                check=True
            )
            print(result.stdout)

            return 0
        except subprocess.CalledProcessError as e:
            self.console.print(f"[bold red]Error:[/] {e.stderr}", err=True)
            return e.returncode
        except FileNotFoundError:
            self.console.print("[bold red]Error:[/] GIT is not installed or not in PATH", err=True)
            return 1
    
    def set_local_config(self, 
                        username: str, 
                        email: str):
        if username:
            self.run_command(["config", "user.name", username, "--local"])
        if email:
            self.run_command(["config", "user.email", email, "--local"])