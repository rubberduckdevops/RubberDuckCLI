class ProjectError(Exception):
    """
    Base Project Exception
    """
    pass

class ProjectBuildError(ProjectError):
    """
    Raised when Project Fails Build
    """

class ProjectRunError(ProjectError):
    """
    Error Running the Project
    """