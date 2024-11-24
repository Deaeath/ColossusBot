# File: handlers/web_handler.py

"""
WebHandler: Middleware Between Backend and Dashboard
-----------------------------------------------------
Provides Flask routes to serve the dashboard and backend data for ColossusBot.
"""

from flask import Flask, jsonify, request
from threading import Thread
import logging
from typing import List, Dict, Any
from dashboard.renderer import Renderer

logger = logging.getLogger("ColossusBot")


class WebHandler:
    """
    A handler for managing the web interface of ColossusBot.
    """

    def __init__(self, bot: Any, console_buffer: List[str], host: str = "0.0.0.0", port: int = 8049) -> None:
        """
        Initializes the WebHandler.

        :param bot: The Discord bot instance.
        :param console_buffer: List to store console output for display on the dashboard.
        :param host: The host address for the Flask app.
        :param port: The port for the Flask app.
        """
        self.bot = bot
        self.console_buffer = console_buffer
        self.host = host
        self.port = port
        self.app = Flask(__name__, static_folder="dashboard/static", template_folder="dashboard/templates")
        self._setup_routes()

    def _setup_routes(self) -> None:
        """
        Sets up Flask routes for the web interface.
        """
        @self.app.route('/')
        def index() -> str:
            """
            Renders the dashboard home page.
            """
            return Renderer.render_index()

        @self.app.route('/console')
        def console() -> str:
            """
            Renders the console logs page.
            """
            return Renderer.render_console()

        @self.app.route('/api/console', methods=['GET'])
        def get_console_logs() -> Dict[str, Any]:
            """
            API endpoint to fetch the latest console logs.
            """
            return jsonify({"logs": self.console_buffer[-100:]})  # Return last 100 log entries

        @self.app.route('/api/commands', methods=['GET'])
        def get_commands() -> Dict[str, Any]:
            """
            API endpoint to fetch the list of available commands and their metadata.
            """
            commands_metadata = {}
            for cog_name, cog in self.bot.cogs.items():
                for command in cog.get_commands():
                    commands_metadata[command.name] = {
                        "description": command.help or "No description provided.",
                        "example": command.usage or "No example available.",
                        "arguments": [str(arg) for arg in command.clean_params]
                    }
            return jsonify(commands_metadata)

        @self.app.route('/api/status', methods=['GET'])
        def get_status() -> Dict[str, Any]:
            """
            API endpoint to fetch the bot's current status.
            """
            return jsonify({
                "status": "online",
                "guilds": len(self.bot.guilds),
                "latency": round(self.bot.latency * 1000, 2)  # ms
            })

        @self.app.route('/api/action/<action>', methods=['POST'])
        def trigger_action(action: str) -> Dict[str, Any]:
            """
            API endpoint to trigger specific bot actions.

            :param action: The action to trigger (e.g., restart, reload).
            """
            try:
                if action == "restart":
                    self.bot.loop.create_task(self.bot.close())
                    return jsonify({"success": True, "result": "Bot is restarting."})
                elif action == "reload":
                    cog_name = request.json.get("cog")
                    if cog_name:
                        self.bot.reload_extension(cog_name)
                        return jsonify({"success": True, "result": f"Cog {cog_name} reloaded."})
                    return jsonify({"success": False, "error": "No cog specified for reload."}), 400
                else:
                    raise ValueError(f"Unknown action: {action}")
            except Exception as e:
                logger.error(f"Error performing action '{action}': {e}")
                return jsonify({"success": False, "error": str(e)}), 400

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
        thread = Thread(target=self.run)
        thread.daemon = True
        thread.start()
        logger.info("Web interface running in a separate thread.")
