# File: handlers/web_handler.py

import logging
import time
from flask import Flask, jsonify, request
from threading import Thread, Lock
from typing import List, Dict, Any
from dashboard.renderer import Renderer  # Assuming you have a Renderer for HTML templates
from discord.ext import commands as discord_commands
from handlers.log_handler import SanitizingHandler  # If needed
import os
import sys

class WebHandler:
    """
    A handler for managing the web interface of ColossusBot.
    """

    def __init__(
        self,
        client: discord_commands.Bot,
        console_buffer: List[str],
        buffer_lock: Lock,
        host: str = "0.0.0.0",
        port: int = 8119,
    ) -> None:
        """
        Initializes the WebHandler.

        Args:
            client (discord_commands.Bot): The Discord bot client instance.
            console_buffer (List[str]): The shared buffer containing log messages.
            buffer_lock (Lock): A lock to ensure thread-safe access to the buffer.
            host (str): The host address for the Flask app.
            port (int): The port for the Flask app.
        """
        self.client = client
        self.host = host
        self.port = port
        self.console_buffer = console_buffer
        self.buffer_lock = buffer_lock

        # Determine the absolute paths for templates and static folders
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(current_dir, '..', 'dashboard', 'templates')
        static_dir = os.path.join(current_dir, '..', 'dashboard', 'static')

        # Normalize paths
        template_dir = os.path.normpath(template_dir)
        static_dir = os.path.normpath(static_dir)

        logging.getLogger(__name__).debug(f"Template directory set to: {template_dir}")
        logging.getLogger(__name__).debug(f"Static directory set to: {static_dir}")

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

        # Redirect Flask 'werkzeug' logs through SanitizingHandler if needed
        flask_logger = logging.getLogger('werkzeug')
        flask_logger.removeHandler(flask_logger.handlers[0])  # Remove the default Flask handler
        sanitizing_handler = SanitizingHandler(sys.stdout)  # Use sanitized stdout
        sanitizing_handler.setLevel(logging.INFO)
        sanitizing_handler.setFormatter(logging.Formatter('[Werkzeug] %(message)s'))
        flask_logger.addHandler(sanitizing_handler)

    def _setup_routes(self) -> None:
        """
        Sets up Flask routes for the web interface.
        """
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/console', 'console', self.console)
        self.app.add_url_rule('/commands', 'commands', self.commands)
        self.app.add_url_rule('/status', 'status', self.status)
        self.app.add_url_rule('/api/console', 'get_console_logs', self.get_console_logs, methods=['GET'])
        self.app.add_url_rule('/api/commands', 'get_commands', self.get_commands, methods=['GET'])
        self.app.add_url_rule('/api/status', 'get_status_api', self.get_status_api, methods=['GET'])  # Renamed to avoid duplication
        self.app.add_url_rule('/api/action/<action>', 'trigger_action', self.trigger_action, methods=['POST'])

    def index(self) -> str:
        """
        Renders the dashboard home page.
        """
        logging.getLogger(__name__).debug(f"[{self.__class__.__name__}] Accessed '/' route for index.")
        try:
            return Renderer.render_index()
        except Exception as e:
            logging.getLogger(__name__).error(f"Error rendering index page: {e}", exc_info=True)
            return jsonify({"error": "Failed to load index page."}), 500

    def console(self) -> str:
        """
        Renders the console logs page with the latest sanitized logs.
        """
        logging.getLogger(__name__).debug(f"[{self.__class__.__name__}] Accessed '/console' route for console logs.")
        try:
            # Acquire lock to safely access console_buffer
            with self.buffer_lock:
                recent_logs = self.console_buffer[-100:]
            return Renderer.render_console(logs=recent_logs)
        except Exception as e:
            logging.getLogger(__name__).error(f"Error rendering console page: {e}", exc_info=True)
            return jsonify({"error": "Failed to load console page."}), 500

    def commands(self) -> str:
        """
        Renders the commands page with dynamic commands data.
        """
        logging.getLogger(__name__).debug(f"[{self.__class__.__name__}] Accessed '/commands' route for commands page.")
        try:
            commands_metadata = self._fetch_commands_metadata()
            return Renderer.render_commands(commands_metadata)
        except Exception as e:
            logging.getLogger(__name__).error(f"Error rendering commands page: {e}", exc_info=True)
            return jsonify({"error": "Failed to load commands page."}), 500

    def get_console_logs(self) -> Dict[str, Any]:
        """
        API endpoint to fetch the latest console logs.
        """
        logging.getLogger(__name__).debug(f"[{self.__class__.__name__}] Accessed '/api/console' route to fetch console logs.")
        try:
            with self.buffer_lock:
                recent_logs = self.console_buffer[-100:]
            return jsonify({"logs": recent_logs})
        except Exception as e:
            logging.getLogger(__name__).error(f"Error fetching console logs: {e}", exc_info=True)
            return jsonify({"error": "Failed to fetch console logs."}), 500

    def get_commands(self) -> Dict[str, Any]:
        """
        API endpoint to fetch the list of available commands and their metadata.
        """
        logging.getLogger(__name__).debug(f"[{self.__class__.__name__}] Accessed '/api/commands' route to fetch bot commands.")
        try:
            commands_metadata = self._fetch_commands_metadata()
            return jsonify(commands_metadata)
        except Exception as e:
            logging.getLogger(__name__).error(f"Error fetching commands metadata: {e}", exc_info=True)
            return jsonify({"error": "Failed to fetch commands metadata."}), 500

    def get_status_api(self) -> Dict[str, Any]:
        """
        API endpoint to fetch the bot's current status.
        """
        logging.getLogger(__name__).debug(f"[{self.__class__.__name__}] Accessed '/api/status' route to fetch bot status.")
        try:
            status_info = {
                "status": "online" if self.client.is_ready() else "offline",
                "guilds": len(self.client.guilds),
                "latency": round(self.client.latency * 1000, 2),  # ms
            }
            return jsonify(status_info)
        except Exception as e:
            logging.getLogger(__name__).error(f"Error fetching status information: {e}", exc_info=True)
            return jsonify({"error": "Failed to fetch status information."}), 500

    def status(self) -> str:
        """
        Renders the status page with graphical data representations.
        """
        logging.getLogger(__name__).debug(f"[{self.__class__.__name__}] Accessed '/status' route for status page.")
        try:
            return Renderer.render_status(latency_history=self.latency_history)
        except Exception as e:
            logging.getLogger(__name__).error(f"Error rendering status page: {e}", exc_info=True)
            return jsonify({"error": "Failed to load status page."}), 500

    def trigger_action(self, action: str) -> Dict[str, Any]:
        """
        API endpoint to trigger specific bot actions.

        Args:
            action (str): The action to trigger (e.g., restart, reload).
        """
        logging.getLogger(__name__).debug(f"Accessed '/api/action/{action}' route to trigger an action.")
        try:
            if action == "restart":
                logging.getLogger(__name__).info(f"[{self.__class__.__name__}] Restart action triggered. Closing client.")
                # Assuming you have a mechanism to restart the bot after closing
                self.client.loop.create_task(self.client.close())
                return jsonify({"success": True, "result": "Client is restarting."})
            elif action == "reload":
                cog_name = request.json.get("cog")
                if cog_name:
                    logging.getLogger(__name__).info(f"Reloading cog: {cog_name}")
                    self.client.reload_extension(cog_name)
                    return jsonify({"success": True, "result": f"Cog {cog_name} reloaded."})
                logging.getLogger(__name__).warning(f"[{self.__class__.__name__}] Reload action triggered without specifying a cog.")
                return jsonify({"success": False, "error": "No cog specified for reload."}), 400
            else:
                logging.getLogger(__name__).error(f"Unknown action attempted: {action}")
                raise ValueError(f"Unknown action: {action}")
        except Exception as e:
            logging.getLogger(__name__).error(f"Error performing action '{action}': {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 400

    def _fetch_commands_metadata(self) -> Dict[str, Any]:
        """
        Retrieves the commands metadata from the bot's cogs.

        Returns:
            Dict[str, Any]: A dictionary containing commands and their metadata.
        """
        logging.getLogger(__name__).debug(f"[{self.__class__.__name__}] Fetching commands metadata from bot's cogs.")
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
            logging.getLogger(__name__).debug(f"[{self.__class__.__name__}] Successfully fetched commands metadata.")
        except Exception as e:
            logging.getLogger(__name__).error(f"Error fetching commands metadata: {e}", exc_info=True)
        return commands_metadata

    def run(self) -> None:
        """
        Starts the Flask application.
        """
        logging.getLogger(__name__).info(f"Starting web interface on {self.host}:{self.port}...")
        self.app.run(host=self.host, port=self.port, debug=False)  # Set debug=False in production

    def start(self) -> None:
        """
        Starts the Flask app in a separate thread.
        """
        logging.getLogger(__name__).info(f"[{self.__class__.__name__}] Starting web interface in a separate thread.")
  
