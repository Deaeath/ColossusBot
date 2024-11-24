# File: dashboard/renderer.py

"""
Renderer: Renders HTML Templates for the Dashboard
--------------------------------------------------
Provides a clean interface for rendering dashboard templates.
"""

from flask import render_template


class Renderer:
    """
    Handles rendering of dashboard templates.
    """

    @staticmethod
    def render_index() -> str:
        """
        Renders the dashboard index page.

        :return: Rendered HTML for the index page.
        """
        return render_template("index.html")

    @staticmethod
    def render_console() -> str:
        """
        Renders the console logs page.

        :return: Rendered HTML for the console logs page.
        """
        return render_template("console.html")
