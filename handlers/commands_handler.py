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
from handlers.database_handler import DatabaseHandler
from decorators import with_roles  # Custom decorator
import logging

logger = logging.getLogger("ColossusBot")


class CommandsHandler(commands.Cog):
    """
    A handler for routing commands directly to their respective cog methods.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler) -> None:
        """
        Initializes the CommandsHandler.

        :param client: The Discord bot client instance.
        :param db_handler: The database handler for archiving operations.
        """
        self.client = client
        self.db_handler = db_handler
        self.aichatbot = AIChatbot(client, db_handler)
        self.channel_manager = ChannelAccessManager(client, db_handler)
        self.admin_commands = AdminCommands(client, db_handler)
        self.channel_archiver = ChannelArchiver(client, db_handler)
        logger.info("CommandsHandler initialized successfully.")

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


async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    """
    Registers the CommandsHandler cog with the bot.

    :param client: The Discord bot client instance.
    :param db_handler: The database handler for archiving operations.
    """
    logger.info("Setting up CommandsHandler cog...")
    await client.add_cog(CommandsHandler(client, db_handler))
    logger.info("CommandsHandler cog setup complete.")
