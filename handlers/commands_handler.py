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
        logger.info("CommandsHandler initialized successfully.")

    # Existing Command Methods
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
        logger.info(f"Executing 'clear_chat' command with args: {args}")
        await self.aichatbot.clear_chat(ctx, *args)

    @commands.command(
        name="show_history",
        help="Displays the conversation history for a user.",
        usage="!show_history",
        extras={"permissions": ["Manage Messages"]},
    )
    @commands.has_permissions(manage_messages=True)
    async def show_history(self, ctx: commands.Context, *args) -> None:
        """
        Displays the conversation history for a user by routing to AIChatbot cog.

        :param ctx: The command context.
        :param args: Additional arguments for the show_history command.
        """
        logger.info(f"Executing 'show_history' command with args: {args}")
        await self.aichatbot.show_history(ctx, *args)

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
        logger.info(f"Executing 'reset_perms' command with args: {args}")
        await self.channel_manager.reset_perms(ctx, *args)

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
        logger.info(f"Executing 'view_perms' command with args: {args}")
        await self.channel_manager.view_perms(ctx, *args)

    @commands.command(
        name="mute",
        help="Mutes a member in the server.",
        usage="!mute @user [reason]",
        extras={"permissions": ["Moderate Members"]},
    )
    @commands.has_permissions(moderate_members=True)
    async def mute_user(self, ctx: commands.Context, member: Member, *, reason: Optional[str] = None) -> None:
        """
        Mutes a member in the server by routing to AdminCommands cog.

        :param ctx: The command context.
        :param member: The member to mute.
        :param reason: The reason for muting the member.
        """
        logger.info(f"Executing 'mute_user' command for {member} with reason: {reason}")
        await self.admin_commands.mute_user_logic(ctx, member, reason)

    @commands.command(
        name="autoarchive",
        help="Automatically archives inactive channels.",
        usage="!autoarchive",
        extras={"permissions": ["Manage Channels"]},
    )
    @commands.has_permissions(manage_channels=True)
    async def autoarchive(self, ctx: commands.Context) -> None:
        """
        Automatically archives inactive channels by routing to ChannelArchiver cog.

        :param ctx: The command context.
        """
        logger.info("Executing 'autoarchive' command.")
        await self.channel_archiver.autoarchive(ctx)

    @commands.command(
        name="archive",
        help="Archives a specific channel or category.",
        usage="!archive <channel/category>",
        extras={"permissions": ["Manage Channels"]},
    )
    @commands.has_permissions(manage_channels=True)
    async def archive(
        self,
        ctx: commands.Context,
        target: Optional[Union[discord_abc.GuildChannel, int, str]] = None,
    ) -> None:
        """
        Archives a specific channel or category by routing to ChannelArchiver cog.

        :param ctx: The command context.
        :param target: The channel, category, or identifier to archive.
        """
        logger.info(f"Executing 'archive' command for target: {target}")
        await self.channel_archiver.archive(ctx, target)

    @commands.command(
        name="unarchive",
        help="Unarchives a specific channel or category.",
        usage="!unarchive <channel/category>",
        extras={"permissions": ["Manage Channels"]},
    )
    @commands.has_permissions(manage_channels=True)
    async def unarchive(
        self,
        ctx: commands.Context,
        target: Optional[discord_abc.GuildChannel] = None,
    ) -> None:
        """
        Unarchives a specific channel or category by routing to ChannelArchiver cog.

        :param ctx: The command context.
        :param target: The channel or category to unarchive.
        """
        logger.info(f"Executing 'unarchive' command for target: {target}")
        await self.channel_archiver.unarchive(ctx, target)

    # Reaction Role Menu Commands

    @commands.command(
        name="createmenu",
        help="Create a new Reaction Role Menu.",
        usage="!createmenu",
        extras={"permissions": ["Manage Roles", "Manage Messages"]},
    )
    @commands.has_permissions(manage_roles=True, manage_messages=True)
    async def createmenu(self, ctx: commands.Context) -> None:
        """
        Creates a new Reaction Role Menu by routing to the ReactionRoleMenu cog.

        :param ctx: The command context.
        """
        logger.info("Executing 'createmenu' command.")
        await self.reaction_role_menu.create_menu(ctx)

    @commands.command(
        name="listmenus",
        help="List all Reaction Role Menus.",
        usage="!listmenus",
        extras={"permissions": ["Manage Roles", "Manage Messages"]},
    )
    @commands.has_permissions(manage_roles=True, manage_messages=True)
    async def listmenus(self, ctx: commands.Context) -> None:
        """
        Lists all Reaction Role Menus by routing to the ReactionRoleMenu cog.

        :param ctx: The command context.
        """
        logger.info("Executing 'listmenus' command.")
        await self.reaction_role_menu.list_menus(ctx)

    @commands.command(
        name="editmenu",
        help="Edit an existing Reaction Role Menu.",
        usage="!editmenu <menu_id>",
        extras={"permissions": ["Manage Roles", "Manage Messages"]},
    )
    @commands.has_permissions(manage_roles=True, manage_messages=True)
    async def editmenu(self, ctx: commands.Context, menu_id: str) -> None:
        """
        Edits an existing Reaction Role Menu by routing to the ReactionRoleMenu cog.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu to edit.
        """
        logger.info(f"Executing 'editmenu' command for menu_id: {menu_id}")
        await self.reaction_role_menu.edit_menu(ctx, menu_id)

    @commands.command(
        name="exportmenu",
        help="Export a Reaction Role Menu to JSON.",
        usage="!exportmenu <menu_id>",
        extras={"permissions": ["Manage Roles", "Manage Messages"]},
    )
    @commands.has_permissions(manage_roles=True, manage_messages=True)
    async def exportmenu(self, ctx: commands.Context, menu_id: str) -> None:
        """
        Exports a Reaction Role Menu by routing to the ReactionRoleMenu cog.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu to export.
        """
        logger.info(f"Executing 'exportmenu' command for menu_id: {menu_id}")
        await self.reaction_role_menu.export_menu(ctx, menu_id)

    @commands.command(
        name="importmenu",
        help="Import a Reaction Role Menu from JSON.",
        usage="!importmenu",
        extras={"permissions": ["Manage Roles", "Manage Messages"]},
    )
    @commands.has_permissions(manage_roles=True, manage_messages=True)
    async def importmenu(self, ctx: commands.Context) -> None:
        """
        Imports a Reaction Role Menu by routing to the ReactionRoleMenu cog.

        :param ctx: The command context.
        """
        logger.info("Executing 'importmenu' command.")
        await self.reaction_role_menu.import_menu(ctx)

    @commands.command(
        name="deletemenu",
        help="Delete a Reaction Role Menu.",
        usage="!deletemenu <menu_id>",
        extras={"permissions": ["Manage Roles", "Manage Messages"]},
    )
    @commands.has_permissions(manage_roles=True, manage_messages=True)
    async def deletemenu(self, ctx: commands.Context, menu_id: str) -> None:
        """
        Deletes a Reaction Role Menu by routing to the ReactionRoleMenu cog.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu to delete.
        """
        logger.info(f"Executing 'deletemenu' command for menu_id: {menu_id}")
        await self.reaction_role_menu.delete_menu(ctx, menu_id)

    # Autoresponder Commands

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
        logger.info(f"Executing 'add_autoresponse' command with trigger '{trigger}' in guild ID: {ctx.guild.id}")
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
        logger.info(f"Executing 'remove_autoresponse' command for ID: {autoresponse_id} in guild ID: {ctx.guild.id}")
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
        logger.info(f"Executing 'list_autoresponses' command in guild ID: {ctx.guild.id}")
        await self.autoresponder.list_autoresponses(ctx)

    # Ticket Checker Commands

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
        By default, ticket checks are disabled until enabled by this command.

        :param ctx: The command context.
        :param state: The desired state, either "on" or "off".
        """
        logger.info(f"Executing 'ticketmonitor' command with state: {state}")
        await self.channel_manager.ticketmonitor_command(ctx, state)

    # Prefix Manager Commands

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
        logger.info(f"Executing 'setprefix' command with new prefix: {new_prefix}")
        await self.prefix_manager.setprefix(ctx, new_prefix)

    # Commands Metadata

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
        return commands_data

    def _extract_command_permissions(self, command: commands.Command) -> str:
        """
        Extracts the permissions required for a given command based on its extras attribute.

        :param command: The command to inspect.
        :return: A string listing the required permissions.
        """
        permissions = command.extras.get('permissions', "Default")
        if isinstance(permissions, list):
            return ", ".join(sorted(permissions))
        else:
            return permissions

    async def setup_commands_data_route(self):
        """
        Sets up an API route to provide commands data to the dashboard.
        Assumes integration with a Flask-like web framework.
        """
        from flask import Blueprint, jsonify

        commands_bp = Blueprint('commands', __name__)

        @commands_bp.route('/api/commands', methods=['GET'])
        def api_commands():
            data = self.get_commands_data()
            return jsonify(data)

        # Assuming the bot has an attribute `web_app` representing the Flask app
        if hasattr(self.client, 'web_app'):
            self.client.web_app.register_blueprint(commands_bp)
            logger.info("Registered /api/commands route for dashboard.")
        else:
            logger.error("Web application instance not found in the bot.")


async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    """
    Registers the CommandsHandler cog with the bot.

    :param client: The Discord bot client instance.
    :param db_handler: The database handler instance.
    """
    logger.info("Setting up CommandsHandler cog...")
    commands_handler = CommandsHandler(client, db_handler)
    await client.add_cog(commands_handler)
    await commands_handler.setup_commands_data_route()
    logger.info("CommandsHandler cog setup complete.")
