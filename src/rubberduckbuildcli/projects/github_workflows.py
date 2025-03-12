import json
import os
import yaml
from pathlib import Path


class GithubWorkflows:
    def __init__(self):
        self.workflow_dir = self.create_workflow_directory()
        pass
        
    def create_workflow_directory(self):
        """
        Create .github/workflows directory
        """
        workflows_dir = Path(".github/workflows")
        workflows_dir.mkdir(parents=True, exist_ok=True)
        return workflows_dir
    
    def generate_docker_workflow(self, config):
        """
        Generate Generic Docker Workflow
        """
        workflows_dir = self.workflow_dir
        docker_config = self.config.get("GithubWF", {}).get("Docker", {})
        if not docker_config: 
            print("No Docker Config")
            return
        
        registry = docker_config.get("registery", "ghcr.io")
        image_name = docker_config.get("image_name", config.get("name", "app"))
        workflow = {
            "name": "Docker Build and Push",
            "on": {
                "push": {
                    "branches": ["main"], 
                    "tags": ["v*"]
                }, 
                "pull_request": {
                    "branches": ["main"]
                }
            },
        "jobs": {
            "build": {
                "runs-on": "ubuntu-latest",
                "permissions": {
                    "contents": "read",
                    "packages": "write"
                },
                "steps": [
                    {
                        "name": "Checkout repository",
                        "uses": "actions/checkout@v3"
                    },
                    {
                        "name": "Set up Docker Buildx",
                        "uses": "docker/setup-buildx-action@v2"
                    },
                    {
                        "name": "Login to Container Registry",
                        "uses": "docker/login-action@v2",
                        "with": {
                            "registry": registry,
                            "username": "${{ github.actor }}",
                            "password": "${{ secrets.GITHUB_TOKEN }}"
                        }
                    },
                    {
                        "name": "Extract metadata for Docker",
                        "id": "meta",
                        "uses": "docker/metadata-action@v4",
                        "with": {
                            "images": f"{registry}/{image_name}",
                            "tags": [
                                "type=ref,event=branch",
                                "type=ref,event=pr",
                                "type=semver,pattern={{version}}",
                                "type=sha"
                            ]
                        }
                    },
                    {
                        "name": "Build and push Docker image",
                        "uses": "docker/build-push-action@v4",
                        "with": {
                            "context": ".",
                            "push": "${{ github.event_name != 'pull_request' }}",
                            "tags": "${{ steps.meta.outputs.tags }}",
                            "labels": "${{ steps.meta.outputs.labels }}",
                            "cache-from": "type=gha",
                            "cache-to": "type=gha,mode=max"
                        }
                    }
                ]
            }
        }
        }
        # Add any custom build arguments if specified
        if "build_args" in docker_config:
            build_args = {}
            for arg, value in docker_config["build_args"].items():
                build_args[arg] = value
            workflow["jobs"]["build"]["steps"][-1]["with"]["build-args"] = build_args
        
        with open(workflows_dir / "docker-build.yml", "w") as f:
            yaml.dump(workflow, f, sort_keys=False)
        
        print("Generated Docker workflow: .github/workflows/docker-build.yml")


def generate_artifact_zip_workflow(config, workflows_dir):
    """Generate a workflow to create and upload a zip artifact."""
    artifact_config = config.get("GitHubWF", {}).get("Artifact_zip", {})
    if not artifact_config:
        print("No Artifact_zip workflow configuration found")
        return
    
    artifact_name = artifact_config.get("name", config.get("name", "artifact"))
    paths_to_include = artifact_config.get("include", ["**/*"])
    paths_to_exclude = artifact_config.get("exclude", [])
    
    workflow = {
        "name": "Build and Upload Artifact",
        "on": {
            "push": {
                "branches": ["main", "master"],
                "tags": ["v*"]
            }
        },
        "jobs": {
            "build": {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "name": "Checkout repository",
                        "uses": "actions/checkout@v3"
                    },
                    {
                        "name": "Set up environment",
                        "run": artifact_config.get("setup_commands", "echo 'No setup required'")
                    },
                    {
                        "name": "Build project",
                        "run": artifact_config.get("build_commands", "echo 'No build required'")
                    },
                    {
                        "name": "Create artifact directory",
                        "run": "mkdir -p artifacts"
                    },
                    {
                        "name": "Upload artifact",
                        "uses": "actions/upload-artifact@v3",
                        "with": {
                            "name": artifact_name,
                            "path": paths_to_include,
                            "if-no-files-found": "error"
                        }
                    }
                ]
            }
        }
    }
    
    # Handle path exclusions
    if paths_to_exclude:
        workflow["jobs"]["build"]["steps"][-1]["with"]["exclude"] = paths_to_exclude
    
    with open(workflows_dir / "artifact-upload.yml", "w") as f:
        yaml.dump(workflow, f, sort_keys=False)
    
    print("Generated Artifact workflow: .github/workflows/artifact-upload.yml")

# def generate_executable_workflow(config, workflows_dir):
#     """Generate a workflow to build and release executables."""
#     executable_config = config.get("GitHubWF", {}).get("executable", {})
#     if not executable_config:
#         print("No executable workflow configuration found")
#         return
    
#     platforms = executable_config.get("platforms", ["linux", "windows", "macos"])
#     app_name = executable_config.get("name", config.get("name", "app"))
    
#     workflow = {
#         "name": "Build Executables",
#         "on": {
#             "push": {
#                 "tags": ["v*"]
#             }
#         },
#         "jobs": {
#             "build": {
#                 "runs-on": "${{ matrix.os }}",
#                 "strategy": {
#                     "matrix": {
#                         "os": []
#                     }
#                 },
#                 "steps": [
#                     {
#                         "name": "Checkout repository",
#                         "uses": "actions/checkout@v3"
#                     },
#                     {
#                         "name": "Set up Python",
#                         "uses": "actions/setup-python@v4",
#                         "with": {
#                             "python-version": "3.10"
#                         }
#                     },
#                     {
#                         "name": "Install dependencies",
#                         "run": "|
#                             python -m pip install --upgrade pip
#                             pip install pyinstaller
#                             pip install -r requirements.txt
#                         "
#                     },
#                     {
#                         "name": "Build executable",
#                         "run": "pyinstaller --onefile --name ${{ matrix.name }} ${{ matrix.entry_point }}"
#                     },
#                     {
#                         "name": "Upload executable artifact",
#                         "uses": "actions/upload-artifact@v3",
#                         "with": {
#                             "name": "${{ matrix.name }}",
#                             "path": "${{ matrix.path }}"
#                         }
#                     }
#                 ]
#             },
#             "release": {
#                 "needs": "build",
#                 "runs-on": "ubuntu-latest",
#                 "if": "startsWith(github.ref, 'refs/tags/')",
#                 "steps": [
#                     {
#                         "name": "Download all artifacts",
#                         "uses": "actions/download-artifact@v3",
#                         "with": {
#                             "path": "artifacts"
#                         }
#                     },
#                     {
#                         "name": "Create Release",
#                         "uses": "softprops/action-gh-release@v1",
#                         "with": {
#                             "files": "artifacts/**/*"
#                         }
#                     }
#                 ]
#             }
#         }
#     }
    
#     matrix_entries = []
#     for platform in platforms:
#         if platform.lower() == "linux":
#             matrix_entries.append({
#                 "os": "ubuntu-latest",
#                 "name": f"{app_name}-linux",
#                 "entry_point": executable_config.get("entry_point", "main.py"),
#                 "path": f"dist/{app_name}-linux"
#             })
#         elif platform.lower() == "windows":
#             matrix_entries.append({
#                 "os": "windows-latest",
#                 "name": f"{app_name}-windows",
#                 "entry_point": executable_config.get("entry_point", "main.py"),
#                 "path": f"dist/{app_name}-windows.exe"
#             })
#         elif platform.lower() == "macos":
#             matrix_entries.append({
#                 "os": "macos-latest",
#                 "name": f"{app_name}-macos",
#                 "entry_point": executable_config.get("entry_point", "main.py"),
#                 "path": f"dist/{app_name}-macos"
#             })
    
#     workflow["jobs"]["build"]["strategy"]["matrix"]["include"] = matrix_entries
    
#     with open(workflows_dir / "executable-build.yml", "w") as f:
#         yaml.dump(workflow, f, sort_keys=False)
    
#     print("Generated Executable workflow: .github/workflows/executable-build.yml")

# def main():
#     """Main function to generate GitHub workflows based on the project configuration."""
#     config = load_project_config()
#     if not config:
#         return
    
#     if "GitHubWF" not in config:
#         print("No GitHubWF configuration found in RubberDuckProject.json")
#         return
    
#     workflows_dir = create_workflow_directory()
    
#     # Generate workflows based on configuration
#     if "Docker" in config["GitHubWF"]:
#         generate_docker_workflow(config, workflows_dir)
    
#     if "Artifact_zip" in config["GitHubWF"]:
#         generate_artifact_zip_workflow(config, workflows_dir)
    
#     if "executable" in config["GitHubWF"]:
#         generate_executable_workflow(config, workflows_dir)
        
#     print("GitHub workflow generation complete!")

# if __name__ == "__main__":
#     main()
