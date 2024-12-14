# File: dashboard/renderer.py

"""
Renderer: Renders HTML Templates for the Dashboard
--------------------------------------------------
Provides a clean interface for rendering dashboard templates with detailed
debugging and logging capabilities.
"""

import logging
import os
from flask import render_template, current_app
from typing import Dict, Any

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Renderer:
    """
    Handles rendering of dashboard templates.
    """

    @staticmethod
    def _log_debug_info(template_name: str):
        """
        Logs debugging information about the template rendering process.

        :param template_name: Name of the template being rendered.
        """
        try:
            logger.debug(f"Attempting to render template: {template_name}")
            logger.debug(f"Current Working Directory: {os.getcwd()}")
            if current_app:
                logger.debug(f"Configured Template Folder: {current_app.template_folder}")
                logger.debug(f"Available Templates: {current_app.jinja_env.list_templates()}")
            else:
                logger.warning(f"[{self.__class__.__name__}] No active Flask application context detected.")
        except Exception as e:
            logger.error(f"Error while logging template debug info: {e}", exc_info=True)

    @staticmethod
    def render_index() -> str:
        """
        Renders the dashboard index page.

        :return: Rendered HTML for the index page.
        """
        template_name = "index.html"
        Renderer._log_debug_info(template_name)
        try:
            logger.info(f"Rendering template: {template_name}")
            return render_template(template_name)
        except Exception as e:
            logger.error(f"Failed to render template '{template_name}': {e}", exc_info=True)
            raise

    @staticmethod
    def render_console() -> str:
        """
        Renders the console logs page.

        :return: Rendered HTML for the console logs page.
        """
        template_name = "console.html"
        Renderer._log_debug_info(template_name)
        try:
            logger.info(f"Rendering template: {template_name}")
            return render_template(template_name)
        except Exception as e:
            logger.error(f"Failed to render template '{template_name}': {e}", exc_info=True)
            raise

    @staticmethod
    def render_commands(commands: Dict[str, Any]) -> str:
        """
        Renders the commands page with dynamic commands data.

        :param commands: A dictionary containing command metadata.
        :return: Rendered HTML for the commands page.
        """
        template_name = "commands.html"
        Renderer._log_debug_info(template_name)
        try:
            logger.info(f"Rendering template: {template_name} with commands data.")
            return render_template(template_name, commands=commands)
        except Exception as e:
            logger.error(f"Failed to render template '{template_name}': {e}", exc_info=True)
            raise

    @staticmethod
    def render_status() -> str:
        """
        Renders the status page with graphical data representations.

        :return: Rendered HTML for the status page.
        """
        template_name = "status.html"
        Renderer._log_debug_info(template_name)
        try:
            logger.info(f"Rendering template: {template_name}")
            return render_template(template_name)
        except Exception as e:
            logger.error(f"Failed to render template '{template_name}': {e}", exc_info=True)
            raise
