# File: handlers/client_handler.py

"""
ClientHandler: Manages Client Initialization
--------------------------------------------
Centralized setup for Discord client and related configurations.
"""

import logging
from typing import Dict
import discord
from discord.ext import commands
from config import BOT_PREFIX, DATABASE_CONFIG

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
            command_prefix=commands.when_mentioned_or(BOT_PREFIX),
            intents=self.intents,
            description="Your Bot Description Here"
        )
        self.console_buffer: list[str] = []  # Buffer to store console logs
        logger.info("ClientHandler initialization complete.")

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
        intents.reactions = True  # Enable if your bot handles reactions
        # If your bot needs to read message content, enable the following intent
        # Note: As of August 2022, the `message_content` intent is privileged
        # and must be enabled in the Discord Developer Portal.
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
