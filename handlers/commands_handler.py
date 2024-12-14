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
        logger.info(f"[{self.__class__.__name__}.__init__] CommandsHandler initialized successfully.")

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
        logger.info(f"[{self.__class__.__name__}.clear_chat] Executing 'clear_chat' command. Args: {args}")
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
        logger.info(f"[{self.__class__.__name__}.ticketmonitor_command] Executing 'ticketmonitor' command with state: {state}")
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
        logger.info(f"[{self.__class__.__name__}.reset_perms] Executing 'reset_perms' command. Args: {args}")
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
        logger.info(f"[{self.__class__.__name__}.view_perms] Executing 'view_perms' command. Args: {args}")
        await self.channel_manager.view_logs(ctx, *args)

    @commands.command(
        name="add_autoresponse",
        help="Adds a new autoresponse.",
        usage="!add_autoresponse <trigger> <response>",
        extras={"permissions": ["Manage Messages"]},
    )
    @commands.has_permissions(manage_messages=True)
    async def add_autoresponse(self, ctx: commands.Context, trigger: str, *, response: str) -> None:
        """
        Adds a new autoresponse to the server.

        :param ctx: The command context.
        :param trigger: The keyword or phrase to trigger the response.
        :param response: The response message to send.
        """
        logger.info(f"[{self.__class__.__name__}.add_autoresponse] Executing 'add_autoresponse' with trigger: {trigger}")
        await self.autoresponder.add_autoresponse(ctx, trigger, response)

    @commands.command(
        name="remove_autoresponse",
        help="Removes an existing autoresponse.",
        usage="!remove_autoresponse <id>",
        extras={"permissions": ["Manage Messages"]},
    )
    @commands.has_permissions(manage_messages=True)
    async def remove_autoresponse(self, ctx: commands.Context, autoresponse_id: int) -> None:
        """
        Removes an existing autoresponse from the server.

        :param ctx: The command context.
        :param autoresponse_id: The unique ID of the autoresponse to remove.
        """
        logger.info(f"[{self.__class__.__name__}.remove_autoresponse] Executing 'remove_autoresponse' for ID: {autoresponse_id}")
        await self.autoresponder.remove_autoresponse(ctx, autoresponse_id)

    @commands.command(
        name="list_autoresponses",
        help="Lists all autoresponses.",
        usage="!list_autoresponses",
        extras={"permissions": ["Manage Messages"]},
    )
    @commands.has_permissions(manage_messages=True)
    async def list_autoresponses(self, ctx: commands.Context) -> None:
        """
        Lists all autoresponses configured in the server.

        :param ctx: The command context.
        """
        logger.info(f"[{self.__class__.__name__}.list_autoresponses] Executing 'list_autoresponses'")
        await self.autoresponder.list_autoresponses(ctx)

    @commands.command(
        name="setprefix",
        help="Change the bot's command prefix for this guild.",
        usage="!setprefix <new_prefix>",
        extras={"permissions": ["Manage Guild"]},
    )
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx: commands.Context, *, new_prefix: str) -> None:
        """
        Change the bot's command prefix for the current guild and persist it to the database.

        :param ctx: The command context.
        :param new_prefix: The new prefix to set for this guild.
        """
        logger.info(f"[{self.__class__.__name__}.setprefix] Executing 'setprefix' with new prefix: {new_prefix}")
        await self.prefix_manager.setprefix(ctx, new_prefix)

    def get_commands_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Gathers all commands along with their descriptions, usage, and permissions.

        :return: A dictionary containing command metadata.
        """
        commands_data = {}
        for command in self.client.commands:
            name = command.name
            description = command.help or "No description provided."
            usage = command.usage or "No usage information provided."
            permissions = command.extras.get('permissions', "Default")
            if isinstance(permissions, list):
                permissions = ", ".join(sorted(permissions))
            commands_data[name] = {
                'description': description,
                'usage': usage,
                'permissions': permissions,
            }
        logger.debug(f"[{self.__class__.__name__}.get_commands_data] Compiled commands metadata.")
        return commands_data

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
