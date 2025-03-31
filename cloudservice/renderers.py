import abc
import os


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
