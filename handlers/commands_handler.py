# File: handlers/commands_handler.py

"""
CommandsHandler: Routes Commands to Cog Implementations
-------------------------------------------------------
Handles user command registration and directly invokes cog methods.
"""

from discord.ext import commands
from discord import abc as discord_abc
from discord import Member
from typing import Any, Dict, Optional, Union
from colossusCogs.aichatbot import AIChatbot
from colossusCogs.channel_access_manager import ChannelAccessManager
from colossusCogs.admin_commands import AdminCommands
from colossusCogs.channel_archiver import ChannelArchiver
from colossusCogs.reaction_role_menu import ReactionRoleMenu
from colossusCogs.autoresponder import Autoresponder
from colossusCogs.ticket_checker import TicketChecker
from colossusCogs.prefix_manager import PrefixManager
from handlers.database_handler import DatabaseHandler
import logging
import discord

# Set up logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class CommandsHandler(commands.Cog):
    """
    A handler for routing commands directly to their respective cog methods.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler) -> None:
        """
        Initializes the CommandsHandler.

        :param client: The Discord bot client instance.
        :param db_handler: The database handler instance.
        """
        self.client = client
        self.db_handler = db_handler
        self.aichatbot = AIChatbot(client, self.db_handler)
        self.channel_manager = ChannelAccessManager(client, self.db_handler)
        self.admin_commands = AdminCommands(client, self.db_handler)
        self.channel_archiver = ChannelArchiver(client, self.db_handler)
        self.reaction_role_menu = ReactionRoleMenu(client, self.db_handler)
        self.autoresponder = Autoresponder(client, self.db_handler)
        self.ticket_checker = TicketChecker(client, self.db_handler)
        self.prefix_manager = PrefixManager(client, self.db_handler)
        logger.info(self.log_message("__init__", "CommandsHandler initialized successfully."))

    def log_message(self, method_name: str, message: str) -> str:
        """
        Helper method to format log messages with class and method names.

        :param method_name: The name of the method calling the logger.
        :param message: The log message.
        :return: Formatted log message.
        """
        return f"[{self.__class__.__name__}.{method_name}] {message}"

    @commands.command(
        name="clear_chat",
        help="Clears the conversation history for the user.",
        usage="!clear_chat",
        extras={"permissions": ["Manage Messages"]},
    )
    @commands.has_permissions(manage_messages=True)
    async def clear_chat(self, ctx: commands.Context, *args) -> None:
        """
        Clears the conversation history for the user by routing to AIChatbot cog.

        :param ctx: The command context.
        :param args: Additional arguments for the clear_chat command.
        """
        logger.info(self.log_message("clear_chat", f"Executing 'clear_chat' command. Routed to 'AIChatbot' cog. Args: {args}"))
        await self.aichatbot.clear_chat(ctx, *args)

    @commands.command(
        name="ticketmonitor",
        help="Enable or disable the ticket monitoring task.",
        usage="!ticketmonitor [on|off]",
        extras={"permissions": ["Manage Channels"]},
    )
    @commands.has_permissions(manage_channels=True)
    async def ticketmonitor_command(self, ctx: commands.Context, state: str = None) -> None:
        """
        Command to enable or disable the ticket checks.

        :param ctx: The command context.
        :param state: The desired state, either "on" or "off".
        """
        logger.info(self.log_message("ticketmonitor_command", f"Executing 'ticketmonitor' command with state: {state}. Routed to 'TicketChecker' cog."))
        await self.ticket_checker.ticketmonitor_command(ctx, state)

    @commands.command(
        name="reset_perms",
        help="Resets custom permissions for users and channels.",
        usage="!reset_perms",
        extras={"permissions": ["Manage Guild"]},
    )
    @commands.has_permissions(manage_guild=True)
    async def reset_perms(self, ctx: commands.Context, *args) -> None:
        """
        Resets custom permissions for users and channels by routing to ChannelAccessManager cog.

        :param ctx: The command context.
        :param args: Additional arguments for the reset_perms command.
        """
        logger.info(self.log_message("reset_perms", f"Executing 'reset_perms' command. Routed to 'ChannelAccessManager' cog. Args: {args}"))
        await self.channel_manager.reset_permissions(ctx, *args)

    @commands.command(
        name="view_perms",
        help="Displays the current database records for custom permissions.",
        usage="!view_perms",
        extras={"permissions": ["Manage Guild"]},
    )
    @commands.has_permissions(manage_guild=True)
    async def view_perms(self, ctx: commands.Context, *args) -> None:
        """
        Displays the current database records for custom permissions by routing to ChannelAccessManager cog.

        :param ctx: The command context.
        :param args: Additional arguments for the view_perms command.
        """
        logger.info(self.log_message("view_perms", f"Executing 'view_perms' command. Routed to 'ChannelAccessManager' cog. Args: {args}"))
        await self.channel_manager.view_logs(ctx, *args)

    # Additional commands here with the same pattern...


async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    """
    Registers the CommandsHandler cog with the bot.

    :param client: The Discord bot client instance.
    :param db_handler: The database handler instance.
    """
    logger.info("[CommandsHandler.setup] Setting up CommandsHandler cog...")
    commands_handler = CommandsHandler(client, db_handler)
    await client.add_cog(commands_handler)
    logger.info("[CommandsHandler.setup] CommandsHandler cog setup complete.")
