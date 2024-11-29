# File: handlers/commands_handler.py

"""
CommandsHandler: Routes Commands to Cog Implementations
-------------------------------------------------------
Handles user command registration and directly invokes cog methods.
"""

from discord.ext import commands
from discord import abc as discord_abc
from discord import Member
from typing import Optional, Union
from colossusCogs.aichatbot import AIChatbot
from colossusCogs.channel_access_manager import ChannelAccessManager
from colossusCogs.admin_commands import AdminCommands
from colossusCogs.channel_archiver import ChannelArchiver
from colossusCogs.reaction_role_menu import ReactionRoleMenu  # Import the ReactionRoleMenu cog
from colossusCogs.autoresponder import Autoresponder  # Import the Autoresponder cog
from colossusCogs.eternal_slave_cog import EternalSlaveCog  # Import the EternalSlaveCog
from handlers.database_handler import DatabaseHandler
from decorators import with_roles  # Custom decorator
import logging
import discord

logger = logging.getLogger("ColossusBot")


class CommandsHandler(commands.Cog):
    """
    A handler for routing commands directly to their respective cog methods.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler) -> None:
        """
        Initializes the CommandsHandler.

        :param client: The Discord bot client instance.
        """
        self.client = client
        self.db_handler = db_handler
        self.aichatbot = AIChatbot(client, self.db_handler)
        self.channel_manager = ChannelAccessManager(client, self.db_handler)
        self.admin_commands = AdminCommands(client, self.db_handler)
        self.channel_archiver = ChannelArchiver(client, self.db_handler)
        self.reaction_role_menu = ReactionRoleMenu(client, self.db_handler)  # Instantiate ReactionRoleMenu
        self.autoresponder = Autoresponder(client, self.db_handler)  # Instantiate Autoresponder
        self.eternal_slave_cog = EternalSlaveCog(client, db_handler)  # Instantiate EternalSlaveCog
        logger.info("CommandsHandler initialized successfully.")

    # Existing Command Methods
    @commands.command(name="clear_chat", help="Clears the conversation history for the user.", usage="!clear_chat")
    async def clear_chat(self, ctx: commands.Context, *args) -> None:
        """
        Clears the conversation history for the user by routing to AIChatbot cog.

        :param ctx: The command context.
        :param args: Additional arguments for the clear_chat command.
        """
        logger.info(f"Executing 'clear_chat' command with args: {args}")
        await self.aichatbot.clear_chat(ctx, *args)

    @commands.command(name="show_history", help="Displays the conversation history for a user.", usage="!show_history")
    async def show_history(self, ctx: commands.Context, *args) -> None:
        """
        Displays the conversation history for a user by routing to AIChatbot cog.

        :param ctx: The command context.
        :param args: Additional arguments for the show_history command.
        """
        logger.info(f"Executing 'show_history' command with args: {args}")
        await self.aichatbot.show_history(ctx, *args)

    @commands.command(name="reset_perms", help="Resets custom permissions for users and channels.", usage="!reset_perms")
    async def reset_perms(self, ctx: commands.Context, *args) -> None:
        """
        Resets custom permissions for users and channels by routing to ChannelAccessManager cog.

        :param ctx: The command context.
        :param args: Additional arguments for the reset_perms command.
        """
        logger.info(f"Executing 'reset_perms' command with args: {args}")
        await self.channel_manager.reset_perms(ctx, *args)

    @commands.command(name="view_perms", help="Displays the current database records for custom permissions.", usage="!view_perms")
    async def view_perms(self, ctx: commands.Context, *args) -> None:
        """
        Displays the current database records for custom permissions by routing to ChannelAccessManager cog.

        :param ctx: The command context.
        :param args: Additional arguments for the view_perms command.
        """
        logger.info(f"Executing 'view_perms' command with args: {args}")
        await self.channel_manager.view_perms(ctx, *args)

    @commands.command(name="mute", help="Mutes a member in the server.", usage="!mute @user [reason]")
    @with_roles("owner", "head_staff", "moderator", "administrator")
    async def mute_user(self, ctx: commands.Context, member: Member, *, reason: Optional[str] = None) -> None:
        """
        Mutes a member in the server by routing to AdminCommands cog.

        :param ctx: The command context.
        :param member: The member to mute.
        :param reason: The reason for muting the member.
        """
        logger.info(f"Executing 'mute_user' command for {member} with reason: {reason}")
        await self.admin_commands.mute_user_logic(ctx, member, reason)

    @commands.command(name="autoarchive", help="Automatically archives inactive channels.", usage="!autoarchive")
    async def autoarchive(self, ctx: commands.Context) -> None:
        """
        Automatically archives inactive channels by routing to ChannelArchiver cog.

        :param ctx: The command context.
        """
        logger.info("Executing 'autoarchive' command.")
        await self.channel_archiver.autoarchive(ctx)

    @commands.command(name="archive", help="Archives a specific channel or category.", usage="!archive <channel/category>")
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

    @commands.command(name="unarchive", help="Unarchives a specific channel or category.", usage="!unarchive <channel/category>")
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

    @commands.command(name="createmenu", help="Create a new Reaction Role Menu.", usage="!createmenu")
    @commands.has_permissions(manage_roles=True, manage_messages=True)
    async def createmenu(self, ctx: commands.Context) -> None:
        """
        Creates a new Reaction Role Menu by routing to the ReactionRoleMenu cog.

        :param ctx: The command context.
        """
        logger.info("Executing 'createmenu' command.")
        await self.reaction_role_menu.create_menu(ctx)

    @commands.command(name="listmenus", help="List all Reaction Role Menus.", usage="!listmenus")
    async def listmenus(self, ctx: commands.Context) -> None:
        """
        Lists all Reaction Role Menus by routing to the ReactionRoleMenu cog.

        :param ctx: The command context.
        """
        logger.info("Executing 'listmenus' command.")
        await self.reaction_role_menu.list_menus(ctx)

    @commands.command(name="editmenu", help="Edit an existing Reaction Role Menu.", usage="!editmenu <menu_id>")
    @commands.has_permissions(manage_roles=True, manage_messages=True)
    async def editmenu(self, ctx: commands.Context, menu_id: str) -> None:
        """
        Edits an existing Reaction Role Menu by routing to the ReactionRoleMenu cog.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu to edit.
        """
        logger.info(f"Executing 'editmenu' command for menu_id: {menu_id}")
        await self.reaction_role_menu.edit_menu(ctx, menu_id)

    @commands.command(name="exportmenu", help="Export a Reaction Role Menu to JSON.", usage="!exportmenu <menu_id>")
    @commands.has_permissions(manage_roles=True, manage_messages=True)
    async def exportmenu(self, ctx: commands.Context, menu_id: str) -> None:
        """
        Exports a Reaction Role Menu by routing to the ReactionRoleMenu cog.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu to export.
        """
        logger.info(f"Executing 'exportmenu' command for menu_id: {menu_id}")
        await self.reaction_role_menu.export_menu(ctx, menu_id)

    @commands.command(name="importmenu", help="Import a Reaction Role Menu from JSON.", usage="!importmenu")
    @commands.has_permissions(manage_roles=True, manage_messages=True)
    async def importmenu(self, ctx: commands.Context) -> None:
        """
        Imports a Reaction Role Menu by routing to the ReactionRoleMenu cog.

        :param ctx: The command context.
        """
        logger.info("Executing 'importmenu' command.")
        await self.reaction_role_menu.import_menu(ctx)

    @commands.command(name="deletemenu", help="Delete a Reaction Role Menu.", usage="!deletemenu <menu_id>")
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

    @commands.command(name="add_autoresponse", help="Adds a new autoresponse.", usage="!add_autoresponse <trigger> <response>")
    @with_roles("owner", "administrator")
    async def add_autoresponse(self, ctx: commands.Context, trigger: str, *, response: str) -> None:
        """
        Adds a new autoresponse to the server.

        :param ctx: The command context.
        :param trigger: The keyword or phrase to trigger the response.
        :param response: The response message to send.
        """
        logger.info(f"Executing 'add_autoresponse' command with trigger '{trigger}' in guild ID: {ctx.guild.id}")
        await self.autoresponder.add_autoresponse(ctx, trigger, response)

    @commands.command(name="remove_autoresponse", help="Removes an existing autoresponse.", usage="!remove_autoresponse <id>")
    @with_roles("owner", "administrator")
    async def remove_autoresponse(self, ctx: commands.Context, autoresponse_id: int) -> None:
        """
        Removes an existing autoresponse from the server.

        :param ctx: The command context.
        :param autoresponse_id: The unique ID of the autoresponse to remove.
        """
        logger.info(f"Executing 'remove_autoresponse' command for ID: {autoresponse_id} in guild ID: {ctx.guild.id}")
        await self.autoresponder.remove_autoresponse(ctx, autoresponse_id)

    @commands.command(name="list_autoresponses", help="Lists all autoresponses.", usage="!list_autoresponses")
    async def list_autoresponses(self, ctx: commands.Context) -> None:
        """
        Lists all autoresponses configured in the server.

        :param ctx: The command context.
        """
        logger.info(f"Executing 'list_autoresponses' command in guild ID: {ctx.guild.id}")
        await self.autoresponder.list_autoresponses(ctx)


async def setup(client: commands.Bot) -> None:
    """
    Registers the CommandsHandler cog with the bot.

    :param client: The Discord bot client instance.
    """
    logger.info("Setting up CommandsHandler cog...")
    await client.add_cog(CommandsHandler(client))
    logger.info("CommandsHandler cog setup complete.")
