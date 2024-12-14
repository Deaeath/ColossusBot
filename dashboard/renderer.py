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
from typing import Dict, Any, List

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
                logger.warning(f"No active Flask application context detected.")
        except Exception as e:
            logger.error(f"Error while logging template debug info: {e}", exc_info=True)

    @staticmethod
    def _template_exists(template_name: str) -> bool:
        """
        Verifies if the specified template exists in the Flask app's template folder.

        :param template_name: Name of the template to check.
        :return: True if the template exists, False otherwise.
        """
        if current_app and current_app.jinja_env:
            return template_name in current_app.jinja_env.list_templates()
        logger.warning("No active Flask application context for template check.")
        return False

    @staticmethod
    def render_index() -> str:
        """
        Renders the dashboard index page.

        :return: Rendered HTML for the index page.
        """
        template_name = "index.html"
        if not Renderer._template_exists(template_name):
            logger.error(f"Template '{template_name}' does not exist.")
            raise FileNotFoundError(f"Template '{template_name}' not found.")
        Renderer._log_debug_info(template_name)
        try:
            logger.info(f"Rendering template: {template_name}")
            return render_template(template_name)
        except Exception as e:
            logger.error(f"Failed to render template '{template_name}': {e}", exc_info=True)
            raise

    @staticmethod
    def render_console(logs: List[str]) -> str:
        """
        Renders the console logs page.

        :param logs: A list of console log lines to display.
        :return: Rendered HTML for the console logs page.
        """
        template_name = "console.html"
        if not Renderer._template_exists(template_name):
            logger.error(f"Template '{template_name}' does not exist.")
            raise FileNotFoundError(f"Template '{template_name}' not found.")
        Renderer._log_debug_info(template_name)
        try:
            logger.info(f"Rendering template: {template_name} with console logs.")
            return render_template(template_name, logs=logs)
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
        if not Renderer._template_exists(template_name):
            logger.error(f"Template '{template_name}' does not exist.")
            raise FileNotFoundError(f"Template '{template_name}' not found.")
        Renderer._log_debug_info(template_name)
        try:
            logger.info(f"Rendering template: {template_name} with commands data.")
            return render_template(template_name, commands=commands)
        except Exception as e:
            logger.error(f"Failed to render template '{template_name}': {e}", exc_info=True)
            raise

    @staticmethod
    def render_status(latency_history: Dict[str, Any] = None) -> str:
        """
        Renders the status page with graphical data representations.
        Optionally accepts latency_history for charting.

        :param latency_history: Optional dict containing latency labels and values.
        :return: Rendered HTML for the status page.
        """
        template_name = "status.html"
        if not Renderer._template_exists(template_name):
            logger.error(f"Template '{template_name}' does not exist.")
            raise FileNotFoundError(f"Template '{template_name}' not found.")
        Renderer._log_debug_info(template_name)
        try:
            logger.info(f"Rendering template: {template_name} with latency history.")
            return render_template(template_name, latency_history=latency_history or {})
        except Exception as e:
            logger.error(f"Failed to render template '{template_name}': {e}", exc_info=True)
            raise
