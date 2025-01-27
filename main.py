# File: ColossusBot/main.py

"""
ColossusBot: Main Entry Point
-----------------------------
Initializes the bot, sets up handlers, and starts the bot lifecycle.
"""

import logging
import os
import random
import traceback
import asyncio
from typing import Any, Dict, List
from discord import Activity, ActivityType
from discord.ext.commands import Bot
from config import BOT_TOKEN
from handlers.client_handler import ClientHandler
from handlers.database_handler import DatabaseHandler
from handlers.event_handler import EventsHandler
from handlers.commands_handler import CommandsHandler
from handlers.web_handler import WebHandler
from handlers.log_handler import BufferLoggingHandler, SanitizingHandler  # Import the custom handlers
from threading import Lock

# Initialize the shared buffer and lock
console_buffer = []
buffer_lock = Lock()

# Configure Logging
logger = logging.getLogger("ColossusBot")
logger.setLevel(logging.DEBUG)  # Capture all log levels

# Create formatters
file_formatter = logging.Formatter("[%(name)s] %(asctime)s - %(levelname)s - %(message)s")
stream_formatter = logging.Formatter("[%(name)s] %(levelname)s - %(message)s")

# File Handler
file_handler = logging.FileHandler("colossusbot.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Stream Handler (Console)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(stream_formatter)
logger.addHandler(stream_handler)

# Buffer Logging Handler
buffer_handler = BufferLoggingHandler(
    buffer=console_buffer,
    buffer_lock=buffer_lock,
    level=logging.DEBUG  # Capture all levels
)
buffer_formatter = logging.Formatter("[%(name)s] %(message)s")
buffer_handler.setFormatter(buffer_formatter)
logger.addHandler(buffer_handler)

# Define the dynamic status change coroutine
async def change_status(client: Bot) -> None:
    """
    Periodically changes the bot's status to a random activity based on its functionalities.
    
    :param client: The Discord bot client instance.
    """
    statuses: List[Dict[str, Any]] = [
        {"type": ActivityType.playing, "name": "with commands like !active and !catfish"},
        {"type": ActivityType.listening, "name": "to your suggestions with !suggest"},
        {"type": ActivityType.watching, "name": "over server activity"},
        {"type": ActivityType.playing, "name": "Chess with users via !vibecheck"},
        {"type": ActivityType.competing, "name": "in moderating actions"},
        {"type": ActivityType.playing, "name": "with AI-powered chat using !aichatbot"},
        {"type": ActivityType.watching, "name": "over ticket channels with !ticketmonitor"},
        {"type": ActivityType.listening, "name": "to your feedback through !suggest"},
        {"type": ActivityType.playing, "name": "to define words with !define"},
        {"type": ActivityType.watching, "name": "the server's health"},
        {"type": ActivityType.playing, "name": "Google searching with !google"},
        {"type": ActivityType.listening, "name": "to your commands like !purge_user"},
    ]
    
    while True:
        try:
            status = random.choice(statuses)
            activity = Activity(type=status["type"], name=status["name"])
            await client.change_presence(activity=activity)
            logger.debug(f"Status changed to: {status['type'].name} {status['name']}")
        except Exception as e:
            logger.error(f"Failed to change status: {e}")
            traceback.print_exc()
        finally:
            await asyncio.sleep(600)  # Wait for 10 minutes before changing again

async def main() -> None:
    """
    Main entry point for ColossusBot.
    Initializes the client, handlers, and starts the bot application.
    """
    logger.info("[Main] Initializing ColossusBot...")

    # Instantiate Handlers
    client_handler: ClientHandler = ClientHandler()
    client: Bot = client_handler.get_client()

    database_config = client_handler.get_database_config()
    database_handler: DatabaseHandler = DatabaseHandler(database_config)
    web_handler: WebHandler = WebHandler(client, console_buffer, buffer_lock)  # Pass buffer and lock
    event_handler: EventsHandler = EventsHandler(client, database_handler)
    commands_handler: CommandsHandler = CommandsHandler(client, database_handler)

    # Attach database_handler to client
    client.db_handler = database_handler

    # Connect to the database
    logger.info("[Main] Connecting to the database...")
    await database_handler.connect()
    await database_handler.setup()
    logger.info("[Main] Database connected and successfully set up.")

    # Register Handlers as cogs
    await client.add_cog(event_handler)
    await client.add_cog(commands_handler)
    logger.info("[Main] Registered event_handler and commands_handler cogs.")

    # Load cogs
    await load_cogs(client)

    # Start the web interface
    web_handler.start()
    logger.info("[Main] Web interface started.")

    # Define on_ready event
    @client.event
    async def on_ready() -> None:
        """
        Triggered when the bot successfully connects to Discord.
        """
        logger.info(f"{client.user} has connected to Discord!")
        # Start the background task for changing status
        client.loop.create_task(change_status(client))
        logger.debug("Started background task for dynamic status changes.")
        # Additional actions can be performed here if needed

    # Run the client
    try:
        logger.info("[Main] Starting ColossusBot...")
        await client.start(BOT_TOKEN)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        traceback.print_exc()
    finally:
        # Close the database connection gracefully
        logger.info("[Main] Closing ColossusBot...")
        await database_handler.close()
        await client.close()
        web_handler.stop()

async def load_cogs(client: Bot):
    """Load all stand-alone commands from the ./commands directory."""
    logger.info("[Main] [load_cogs] Loading cogs!")
    for root, dirs, files in os.walk('./commands'):
        if 'helpers' in dirs:
            dirs.remove('helpers')  # Prevents walking into 'helpers' directories
        for filename in files:
            if filename.endswith('.py') and not filename.endswith('Config.py'):
                cog_path = f'commands.{filename[:-3]}'
                try:
                    await client.load_extension(cog_path)
                    # logger.info(f'[load_cogs] {filename} loaded successfully.')
                except Exception as e:
                    logger.error(f"[Main] [load_cogs] Failed to load {filename}: {e}")
                    traceback.print_exc()
    logger.info("[Main] [load_cogs] All cogs loaded!\n")

if __name__ == "__main__":
    asyncio.run(main())
