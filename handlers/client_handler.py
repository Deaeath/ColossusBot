# File: handlers/client_handler.py

"""
ClientHandler: Manages Client Initialization
--------------------------------------------
Centralized setup for Discord client and related configurations.
Loads per-guild prefixes from the database into memory.
"""

import logging
from typing import Dict, Union, List
import discord
from discord.ext import commands
from config import BOT_PREFIX, DATABASE_CONFIG
from handlers.database_handler import DatabaseHandler

logger = logging.getLogger("ClientHandler")

class ClientHandler:
    """
    Handles initialization and configuration of the Discord client.
    """

    def __init__(self) -> None:
        """
        Initializes the ClientHandler.
        """
        logger.info("Initializing ClientHandler...")
        self.intents = self._setup_intents()

        self.client = commands.Bot(
            command_prefix=self.dynamic_prefix,
            intents=self.intents,
            description="Your Bot Description Here"
        )
        self.console_buffer: List[str] = []  # Buffer to store console logs

        # The guild_prefixes dictionary will be populated from the database on startup
        self.client.guild_prefixes = {}

        logger.info("ClientHandler initialization complete.")

    async def initialize_prefixes(self, db_handler: DatabaseHandler):
        """
        Loads guild prefixes from the database into memory.
        Should be called after the bot is ready and the DB is connected.
        """
        query = "SELECT guild_id, prefix FROM guild_prefixes"
        rows = await db_handler.fetchall(query)
        for row in rows:
            guild_id, prefix = row[0], row[1]
            self.client.guild_prefixes[guild_id] = prefix
        logger.info(f"Loaded {len(rows)} guild prefixes from the database.")

    def dynamic_prefix(self, bot: commands.Bot, message: discord.Message) -> Union[List[str], str]:
        """
        A prefix function that returns the mention prefix and the guild-specific prefix.
        If no custom prefix is set for the guild, it falls back to the default BOT_PREFIX.
        Mentions are always available as a prefix.
        """
        guild_id = message.guild.id if message.guild else None
        prefix = self.client.guild_prefixes.get(guild_id, BOT_PREFIX)
        return commands.when_mentioned_or(prefix)(bot, message)

    @staticmethod
    def _setup_intents() -> discord.Intents:
        """
        Configures Discord intents for the bot.

        :return: Configured intents object.
        """
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True
        intents.members = True
        intents.reactions = True
        # Enable message_content if needed
        intents.message_content = True
        logger.info("Intents configured.")
        return intents

    def get_client(self) -> commands.Bot:
        """
        Returns the Discord client instance.

        :return: The bot client.
        """
        return self.client

    def get_database_config(self) -> Dict[str, str]:
        """
        Returns the database configuration.

        :return: Database configuration dictionary.
        """
        return DATABASE_CONFIG
