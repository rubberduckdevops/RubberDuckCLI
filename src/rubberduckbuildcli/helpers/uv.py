import subprocess

from rich.console import Console
import sys
import signal

class UVExecution:
    def __init__(self):
        self.console = Console()
        
    def run_command(self, args: list[str]) -> int:
        """
        Run a UV Command with real-time output
        """
        # Store the process globally so signal handlers can access it
        self.process = None
        
        # Define signal handler for Ctrl+C
        def signal_handler(sig, frame):
            if self.process:
                self.console.print("\n[bold yellow]Received interrupt signal. Terminating UV process...[/]")
                self.process.terminate()
                try:
                    # Wait for process to terminate, with timeout
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate gracefully
                    self.console.print("[bold red]Process didn't terminate gracefully. Forcing exit...[/]")
                    self.process.kill()
                self.console.print("[bold yellow]UV process terminated.[/]")
                sys.exit(130)  # 130 is the standard exit code for Ctrl+C
        
        # Set up the signal handler
        original_sigint_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, signal_handler)
        
        try:
            # Create process with pipes for real-time output reading
            self.process = subprocess.Popen(
                ["uv"] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Print header for the command
            self.console.print(f"[bold cyan]======================[/]")
            self.console.print(f"[bold cyan]Running UV command:[/] {' '.join(['uv'] + args)}")
            self.console.print(f"[bold cyan]======================[/]")
            
            # Read stdout and stderr in real-time
            while True:
                stdout_line = self.process.stdout.readline()
                stderr_line = self.process.stderr.readline()
                
                if stdout_line:
                    self.console.print(stdout_line.rstrip())
                if stderr_line:
                    self.console.print(f"[bold red]{stderr_line.rstrip()}[/]")
                    
                # Check if process has terminated
                if self.process.poll() is not None:
                    # Get any remaining output
                    for line in self.process.stdout.readlines():
                        self.console.print(line.rstrip())
                    for line in self.process.stderr.readlines():
                        self.console.print(f"[bold red]{line.rstrip()}[/]")
                    break
            
            # Print footer with return code
            self.console.print(f"[bold cyan]======================[/]")
            self.console.print(f"[bold cyan]Command completed with return code:[/] {self.process.returncode}")
            self.console.print(f"[bold cyan]======================[/]")
            
            return self.process.returncode
            
        except FileNotFoundError:
            self.console.print("[bold red]Error:[/] UV is not installed or not in PATH")
            return 1
        finally:
            # Restore the original signal handler
            signal.signal(signal.SIGINT, original_sigint_handler)
            # Clean up process reference
            self.process = None

    def install(self,
                packages: list[str],
                upgrade: bool = False, 
                ):
        """
        Install Packages with UV
        """
        uv_cmd = ["add"]
        if upgrade: 
            uv_cmd.extend(["--upgrade"])
        if packages: 
            uv_cmd.extend(packages)

        return self.run_command(uv_cmd)


    def uninstall(self,
                  packages: list[str], 
                  yes: bool = True):
        uv_cmd = ["remove"]
        if packages: 
            uv_cmd.extend(packages)
        return self.run_command(uv_cmd)

