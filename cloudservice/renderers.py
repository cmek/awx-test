import abc
import os
from towerlib import Tower


"""
renderers get template name and variables and 'render' the template
"""

class Renderer(abc.ABC):
    """
    Abstract base class for renderers.
    """

    @abc.abstractmethod
    def render(self, template_name: str, **variables) -> str:
        """
        Render the template with the given name and variables.

        Args:
            template_name (str): The name of the template to render.
            **variables: The variables to use in the template.

        Returns:
            str: The rendered template.
        """
        pass

class JinjaRenderer(Renderer):
    """
    Jinja2 renderer for rendering templates.
    """

    def __init__(self, template_dir: str):
        """
        Initialize the JinjaRenderer with the given template directory.

        Args:
            template_dir (str): The directory containing the templates.
        """
        from jinja2 import Environment, FileSystemLoader
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render(self, template_name: str, **variables) -> str:
        """
        Render the template with the given name and variables.

        Args:
            template_name (str): The name of the template to render.
            **variables: The variables to use in the template.

        Returns:
            str: The rendered template.
        """
        template = self.env.get_template(os.path.join(variables.get("os"), template_name))
        return template.render(**variables)


class AWXRenderer(Renderer):
    """
    AWX renderer for rendering templates using ansible tower (AWX)
    """

    def __init__(self, url, user, password):
        """
        Initialize the AWXRenderer with the given template directory.

        Args:
            template_dir (str): The directory containing the templates.
        """
        self.tower = Tower(url, user, password)

    def render(self, template_name: str, **variables) -> str:
        """
        calls an ansible tower job template with the 'template' attribute set to the template name
        that the job needs to render with the variables and send to the target device

        Assuming here that the job template name will be in the following format:
        "<os>_network_service", where <os> is the os of the device.

        The same with credentials, I'm assuming those will be stored as "<os>_machine"
        """
        
        # make sure we have the os
        os = variables.get("os", None)
        target = variables.get("hostname", None)
        assert(os), "os is required in the variables"
        assert(target), "target (hostname) is required in the variables"
       
        template = self.tower.get_job_template_by_name(f"{os}_network_service")
        creds = list(map(lambda x: x.id, self.tower.get_credentials_by_name(f"{os}_machine")))

        task = template.launch(diff_mode=True, limit=target,
                        credentials=creds,
                        credential=creds[0],
                        extra_vars=variables)

        return task
