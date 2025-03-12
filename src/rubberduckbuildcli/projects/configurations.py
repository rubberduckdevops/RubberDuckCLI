import os
import json

from pydantic import BaseModel

class ProjectConfigurationFile(BaseModel): 
    ProjectName: str
    Language: str
    LanguageVersion: str
    ExtraCommands: list[dict]
    GithubWF: list[dict]

    @classmethod
    def load_config_json(cls, file_path: str) -> 'ProjectConfigurationFile':
        with open(file_path, 'r') as f: 
            return cls.model_validate(json.load(f))
        
    def __str__(self):
        lines = [f"{self.__class__.__name__}:"]
        for field_name, field in self.model_fields.items():
            value = getattr(self, field_name)
            lines.append(f"  {field_name} ({field.annotation.__name__}): {value}")
        return "\n".join(lines)

    def get(self, key, default=None):
        """Get attribute value by name"""
        return getattr(self, key, default)   

class BaseProjectConfiguration:
    def __init__(self):
        self.project_path = os.getcwd()
        self.project_config_file = "RubberDuckProject.json"
        self.project_config_file_path = os.path.join(self.project_path,"RubberDuckProject.json")
        self.project_configuration = None

    def config_exists(self, throw_error: bool = True):
        if not os.path.isfile(self.project_config_file_path) and throw_error:
            raise FileNotFoundError("Config File not found!")
        elif not os.path.isfile(self.project_config_file_path):
            return False
        else:
            return True
    

    def load_config(self):
        if self.config_exists():
            self.project_configuration = ProjectConfigurationFile.load_config_json(self.project_config_file_path)
    
    def print_config(self):
        if self.project_configuration:
            print(self.project_configuration)
        else: 
            self.load_config()
            self.print_config()

    def get(self, key, default=None):
        """
        Get a configuration value by key, similar to dictionary access.
        """
        if not self.project_configuration:
            self.load_config()
            
        if hasattr(self.project_configuration, key):
            return getattr(self.project_configuration, key)
        return default

    def create_default_config(self, project_name="DefaultProject", language="Python", language_version="3.10"):
        """
        Create a default configuration file if one doesn't exist.

        Args:
            project_name (str): Name of the project
            language (str): Programming language for the project
            language_version (str): Version of the language

        Returns:
            bool: True if the config was created, False if it already exists
        """
        if os.path.isfile(self.project_config_file_path):
            print(f"Configuration file already exists at {self.project_config_file_path}")
            return False
            
        default_config = {
            "ProjectName": project_name,
            "Language": language,
            "LanguageVersion": language_version,
            "ExtraCommands": []
        }
        
        # Create the configuration file
        with open(self.project_config_file_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        
        print(f"Created default configuration at {self.project_config_file_path}")
        
        # Load the newly created configuration
        self.load_config()
        return True