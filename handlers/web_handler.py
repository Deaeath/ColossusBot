# File: handlers/web_handler.py

"""
WebHandler: Middleware Between Backend and Dashboard
-----------------------------------------------------
Provides Flask routes to serve the dashboard and backend data for ColossusBot.
"""

import time
import os
import logging
from flask import Flask, jsonify, request
from threading import Thread
from typing import List, Dict, Any
from dashboard.renderer import Renderer
from discord.ext import commands as discord_commands  # Renamed to avoid conflict

# Set up logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class WebHandler:
    """
    A handler for managing the web interface of ColossusBot.
    """

    def __init__(self, client: discord_commands.Bot, console_buffer: List[str], host: str = "0.0.0.0", port: int = 8119) -> None:
        """
        Initializes the WebHandler.

        :param client: The Discord bot client instance.
        :param console_buffer: List to store console output for display on the dashboard.
        :param host: The host address for the Flask app.
        :param port: The port for the Flask app.
        """
        self.client = client
        self.console_buffer = console_buffer
        self.host = host
        self.port = port

        # Determine the absolute paths for templates and static folders
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(current_dir, '..', 'dashboard', 'templates')
        static_dir = os.path.join(current_dir, '..', 'dashboard', 'static')

        # Normalize paths
        template_dir = os.path.normpath(template_dir)
        static_dir = os.path.normpath(static_dir)

        logger.debug(f"Template directory set to: {template_dir}")
        logger.debug(f"Static directory set to: {static_dir}")

        self.latency_history = {
            "labels": [],
            "values": []
        }
        self.start_time = time.time()

        # Initialize Flask app with static and template folders
        self.app = Flask(
            __name__,
            static_folder=static_dir,
            template_folder=template_dir,
        )
        self._setup_routes()

    def _setup_routes(self) -> None:
        """
        Sets up Flask routes for the web interface.
        """
        self._add_route('/', self.index)
        self._add_route('/console', self.console)
        self._add_route('/commands', self.commands)
        self._add_route('/status', self.status)
        self._add_route('/api/console', self.get_console_logs, methods=['GET'])
        self._add_route('/api/commands', self.get_commands, methods=['GET'])
        self._add_route('/api/status', self.get_status_api, methods=['GET'])  # Renamed to avoid duplication
        self._add_route('/api/action/<action>', self.trigger_action, methods=['POST'])

    def _add_route(self, route: str, view_func, methods: List[str] = ['GET']) -> None:
        """
        Helper function to add a route to the Flask app.

        :param route: The route URL.
        :param view_func: The view function to associate with the route.
        :param methods: The HTTP methods allowed for this route.
        """
        self.app.route(route, methods=methods)(view_func)

    def index(self) -> str:
        """
        Renders the dashboard home page.
        """
        logger.debug(f"[{self.__class__.__name__} Accessed '/' route for index.")
        try:
            return Renderer.render_index()
        except Exception as e:
            logger.error(f"Error rendering index page: {e}", exc_info=True)
            return jsonify({"error": "Failed to load index page."}), 500

    def console(self) -> str:
        """
        Renders the console logs page.
        """
        logger.debug(f"[{self.__class__.__name__} Accessed '/console' route for console logs.")
        try:
            return Renderer.render_console()
        except Exception as e:
            logger.error(f"Error rendering console page: {e}", exc_info=True)
            return jsonify({"error": "Failed to load console page."}), 500

    def commands(self) -> str:
        """
        Renders the commands page with dynamic commands data.
        """
        logger.debug(f"[{self.__class__.__name__} Accessed '/commands' route for commands page.")
        try:
            commands_metadata = self._fetch_commands_metadata()
            return Renderer.render_commands(commands_metadata)
        except Exception as e:
            logger.error(f"Error rendering commands page: {e}", exc_info=True)
            return jsonify({"error": "Failed to load commands page."}), 500

    def get_console_logs(self) -> Dict[str, Any]:
        """
        API endpoint to fetch the latest console logs.
        """
        logger.debug(f"[{self.__class__.__name__} Accessed '/api/console' route to fetch console logs.")
        return jsonify({"logs": self.console_buffer[-100:]})  # Return last 100 log entries

    def get_commands(self) -> Dict[str, Any]:
        """
        API endpoint to fetch the list of available commands and their metadata.
        """
        logger.debug(f"[{self.__class__.__name__} Accessed '/api/commands' route to fetch bot commands.")
        commands_metadata = self._fetch_commands_metadata()
        return jsonify(commands_metadata)

    def get_status_api(self) -> Dict[str, Any]:
        """
        API endpoint to fetch the bot's current status.
        """
        logger.debug(f"[{self.__class__.__name__} Accessed '/api/status' route to fetch bot status.")
        return jsonify({
            "status": "online" if self.client.is_ready() else "offline",
            "guilds": len(self.client.guilds),
            "latency": round(self.client.latency * 1000, 2),  # ms
        })

    def status(self) -> str:
        """
        Renders the status page.
        """
        logger.debug(f"[{self.__class__.__name__} Accessed '/status' route for status page.")
        try:
            return Renderer.render_status()
        except Exception as e:
            logger.error(f"Error rendering status page: {e}", exc_info=True)
            return jsonify({"error": "Failed to load status page."}), 500

    def trigger_action(self, action: str) -> Dict[str, Any]:
        """
        API endpoint to trigger specific bot actions.

        :param action: The action to trigger (e.g., restart, reload).
        """
        logger.debug(f"Accessed '/api/action/{action}' route to trigger an action.")
        try:
            if action == "restart":
                logger.info(f"[{self.__class__.__name__} Restart action triggered. Closing client.")
                # Assuming you have a mechanism to restart the bot after closing
                self.client.loop.create_task(self.client.close())
                return jsonify({"success": True, "result": "Client is restarting."})
            elif action == "reload":
                cog_name = request.json.get("cog")
                if cog_name:
                    logger.info(f"Reloading cog: {cog_name}")
                    self.client.reload_extension(cog_name)
                    return jsonify({"success": True, "result": f"Cog {cog_name} reloaded."})
                logger.warning(f"[{self.__class__.__name__} Reload action triggered without specifying a cog.")
                return jsonify({"success": False, "error": "No cog specified for reload."}), 400
            else:
                logger.error(f"Unknown action attempted: {action}")
                raise ValueError(f"Unknown action: {action}")
        except Exception as e:
            logger.error(f"Error performing action '{action}': {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 400

    def _extract_command_permissions(self, command: discord_commands.Command) -> str:
        """
        Extracts the permissions required for a given command based on its decorators.

        :param command: The command to inspect.
        :return: A string listing the required permissions.
        """
        permissions = set()

        for check in command.checks:
            if hasattr(check, 'predicate'):
                predicate = check.predicate
                # Extract permissions from @commands.has_permissions
                if hasattr(predicate, 'permissions'):
                    perms = [
                        perm.replace('_', ' ').title()
                        for perm, value in predicate.permissions.items()
                        if value
                    ]
                    permissions.update(perms)

                # Extract roles from custom @with_roles decorator
                if hasattr(predicate, 'roles'):
                    roles = [
                        role.replace('_', ' ').title() if isinstance(role, str) else str(role)
                        for role in predicate.roles
                    ]
                    permissions.update(roles)

        return ", ".join(sorted(permissions)) if permissions else "Default"

    def _fetch_commands_metadata(self) -> Dict[str, Any]:
        """
        Retrieves the commands metadata from the bot's cogs.

        :return: A dictionary containing commands and their metadata.
        """
        logger.debug(f"[{self.__class__.__name__} Fetching commands metadata from bot's cogs.")
        commands_metadata = {}
        try:
            for cog_name, cog in self.client.cogs.items():
                for command in cog.get_commands():
                    # Pull permissions directly from extras
                    permissions = command.extras.get('permissions', "Default")
                    if isinstance(permissions, list):
                        permissions = ", ".join(sorted(permissions))

                    commands_metadata[command.name] = {
                        "description": command.help or "No description provided.",
                        "usage": command.usage or "No usage provided.",
                        "permissions": permissions,
                    }
            logger.debug(f"[{self.__class__.__name__} Successfully fetched commands metadata.")
        except Exception as e:
            logger.error(f"Error fetching commands metadata: {e}", exc_info=True)
        return commands_metadata

    def run(self) -> None:
        """
        Starts the Flask application.
        """
        logger.info(f"Starting web interface on {self.host}:{self.port}...")
        self.app.run(host=self.host, port=self.port)

    def start(self) -> None:
        """
        Starts the Flask app in a separate thread.
        """
        logger.info(f"[{self.__class__.__name__} Starting web interface in a separate thread.")
        thread = Thread(target=self.run)
        thread.daemon = True
        thread.start()
        logger.info(f"[{self.__class__.__name__} Web interface is now running.")

    def stop(self) -> None:
        """
        Stops the Flask app.
        """
        logger.info(f"[{self.__class__.__name__} Stopping web interface...")
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        logger.info(f"[{self.__class__.__name__} Web interface stopped.")
