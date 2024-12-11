# File: dashboard/renderer.py

"""
Renderer: Renders HTML Templates for the Dashboard
--------------------------------------------------
Provides a clean interface for rendering dashboard templates with detailed
debugging and logging capabilities.
"""

import logging
import os
import requests
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
                logger.warning("No active Flask application context detected.")
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
    def render_commands() -> str:
        """
        Renders the commands page with dynamic commands data.

        :return: Rendered HTML for the commands page.
        """
        template_name = "commands.html"
        Renderer._log_debug_info(template_name)
        try:
            logger.info(f"Fetching commands data for template: {template_name}")
            # Fetch commands data from the API endpoint
            response = requests.get('http://localhost:5000/api/commands')  # Adjust the URL and port as needed
            response.raise_for_status()
            commands_data = response.json()
            logger.debug(f"Commands data fetched: {commands_data}")
            return render_template(template_name, commands=commands_data)
        except requests.RequestException as req_err:
            logger.error(f"HTTP error while fetching commands data: {req_err}", exc_info=True)
            return "<p>Error fetching commands data.</p>"
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
