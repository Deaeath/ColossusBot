"""
Renderer: Renders HTML Templates for the Dashboard
--------------------------------------------------
Provides a clean interface for rendering dashboard templates.
"""

import os
from flask import render_template, current_app


class Renderer:
    """
    Handles rendering of dashboard templates.
    """

    @staticmethod
    def log_template_info(template_name: str):
        """
        Logs debugging information about template loading.

        :param template_name: Name of the template being rendered.
        """
        try:
            print(f"Attempting to render template: {template_name}")
            print(f"Current Working Directory: {os.getcwd()}")
            print(f"Configured Template Folder: {current_app.template_folder}")
            print(f"Available Templates: {current_app.jinja_env.list_templates()}")
        except Exception as e:
            print(f"Error while logging template information: {e}")

    @staticmethod
    def render_index() -> str:
        """
        Renders the dashboard index page.

        :return: Rendered HTML for the index page.
        """
        Renderer.log_template_info("index.html")
        return render_template("index.html")

    @staticmethod
    def render_console() -> str:
        """
        Renders the console logs page.

        :return: Rendered HTML for the console logs page.
        """
        Renderer.log_template_info("console.html")
        return render_template("console.html")
