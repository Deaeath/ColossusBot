# File: colossusCogs/channel_archiver.py

"""
ChannelArchiver Cog: Manages Channel Archiving and Auto-Archiving
----------------------------------------------------------------
This cog is responsible for managing the archiving and unarchiving of 
channels in a Discord server. It includes functionality for:
- Auto-archiving inactive channels.
- Archiving and unarchiving specific channels or categories.
- Ensuring that archived channels are moved to a dedicated archive category.
- Handling rate limits and providing progress updates during operations.
"""

import discord
from discord.ext import commands
import logging
from typing import Union, Optional, List
from datetime import datetime
import asyncio

from handlers.database_handler import DatabaseHandler

# Set up logger
logger = logging.getLogger(__name__)

class ChannelArchiver(commands.Cog):
    """
    A cog to manage channel archiving in Discord servers.
    """

    MAX_CHANNELS_PER_CATEGORY: int = 50  # Discord's approximate limit per category
    BASE_DELAY: float = 1.5  # Base delay between operations
    RATE_LIMIT_DELAY: float = 5  # Delay after a rate limit is encountered

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler):
        """
        Initialize the ChannelArchiver cog.

        :param client: The Discord bot client instance.
        :param db_handler: An instance of the DatabaseHandler.
        """
        self.client = client
        self.db_handler = db_handler
        logging.info("[ChannelArchiver] ChannelArchiver cog initialized.")

    async def cog_load(self) -> None:
        """
        Load the cog and ensure the database is properly set up.
        """
        logger.info(f"[{self.__class__.__name__}] ChannelArchiver cog loaded and database ready.")

    async def autoarchive(self, ctx: commands.Context) -> None:
        """
        Scans for inactive channels of all types and prompts for confirmation to archive each.

        :param ctx: The command context.
        """
        one_month_ago = datetime.utcnow().timestamp() - (30 * 24 * 60 * 60)
        ignored_channels = ['rules', 'roles']

        total_channels = len(ctx.guild.channels)
        gathering_progress_message = await ctx.send(f"🔄 Gathering inactive channels... [0%]")
        inactive_channels = []
        start_time = asyncio.get_event_loop().time()

        for idx, channel in enumerate(ctx.guild.channels, start=1):
            if channel.name.lower() in ignored_channels or (channel.category and "archive" in channel.category.name.lower()):
                continue

            if isinstance(channel, discord.CategoryChannel):
                continue

            last_message_time = 0
            last_message_link = None

            try:
                if isinstance(channel, discord.TextChannel):
                    async for message in channel.history(limit=1):
                        last_message_time = message.created_at.timestamp()
                        last_message_link = message.jump_url
                    if last_message_time == 0:
                        last_message_time = channel.created_at.timestamp()
                elif isinstance(channel, (discord.VoiceChannel, discord.StageChannel)):
                    last_message_time = channel.created_at.timestamp()
                elif isinstance(channel, discord.ForumChannel):
                    if channel.threads:
                        last_post = await channel.threads[0].fetch_message(channel.threads[0].last_message_id)
                        last_message_time = last_post.created_at.timestamp() if last_post else channel.created_at.timestamp()
                        last_message_link = last_post.jump_url if last_post else None
                    else:
                        last_message_time = channel.created_at.timestamp()
                else:
                    continue

                if last_message_time < one_month_ago:
                    inactive_channels.append((channel, last_message_time, last_message_link))
            except Exception as e:
                logger.error(f"Error processing channel `{channel.name}`: {e}")
                continue

            elapsed_time = asyncio.get_event_loop().time() - start_time
            progress = (idx / total_channels) * 100
            progress_bar = '█' * int(progress // 4) + '-' * (25 - int(progress // 4))
            await gathering_progress_message.edit(
                content=f"🔄 Gathering inactive channels... [{progress:.2f}%] [{progress_bar}]"
            )

        await gathering_progress_message.edit(content="✅ Finished gathering inactive channels!")

        if not inactive_channels:
            await ctx.send("✨ No inactive channels found.")
            return

        total_inactive_channels = len(inactive_channels)
        await ctx.send(f"🔍 Found {total_inactive_channels} inactive channel(s).")

        # Archive inactive channels
        await self.archive_channels(ctx, inactive_channels)

    async def archive_channels(self, ctx: commands.Context, channels: List[tuple]) -> None:
        """
        Archives the list of inactive channels.

        :param ctx: The command context.
        :param channels: List of tuples containing channel info to archive.
        """
        for idx, (channel, last_message_time, last_message_link) in enumerate(channels, start=1):
            try:
                archive_category = await self.get_or_create_archive_category(ctx.guild)
                await self.db_handler.add_archived_channel(
                    channel_id=channel.id,
                    original_category_id=channel.category.id if channel.category else None,
                    archive_category_id=archive_category.id,
                    channel_type=type(channel).__name__
                )
                await channel.edit(category=archive_category, sync_permissions=True)
                await ctx.send(f"✅ Channel `{channel.name}` has been archived! 📦")
            except Exception as e:
                logger.error(f"Error archiving channel `{channel.name}`: {e}")

    async def archive(self, ctx: commands.Context, target: Optional[Union[discord.abc.GuildChannel, int, str]] = None) -> None:
        """
        Archives a specified channel or category.

        :param ctx: The command context.
        :param target: The channel or category to archive.
        """
        if target is None:
            await ctx.send("⚠️ Please specify what to archive.")
            return

        channels_to_archive = []
        if isinstance(target, discord.CategoryChannel):
            channels_to_archive.extend(target.channels)
        elif isinstance(target, discord.abc.GuildChannel):
            channels_to_archive.append(target)
        else:
            await ctx.send("⚠️ Invalid target specified.")
            return

        for channel in channels_to_archive:
            try:
                archive_category = await self.get_or_create_archive_category(ctx.guild)
                await self.db_handler.add_archived_channel(
                    channel_id=channel.id,
                    original_category_id=channel.category.id if channel.category else None,
                    archive_category_id=archive_category.id,
                    channel_type=type(channel).__name__
                )
                await channel.edit(category=archive_category, sync_permissions=True)
                await ctx.send(f"✅ Archived `{channel.name}`.")
            except Exception as e:
                logger.error(f"Error archiving `{channel.name}`: {e}")

    async def unarchive(self, ctx: commands.Context, target: Optional[discord.abc.GuildChannel] = None) -> None:
        """
        Unarchives a specified channel or category.

        :param ctx: The command context.
        :param target: The channel or category to unarchive.
        """
        if target is None:
            await ctx.send("⚠️ Please specify what to unarchive.")
            return

        try:
            if isinstance(target, discord.CategoryChannel):
                for channel in target.channels:
                    await channel.edit(category=None, sync_permissions=True)
                await ctx.send(f"✅ Unarchived category `{target.name}`.")
            else:
                await target.edit(category=None, sync_permissions=True)
                await ctx.send(f"✅ Unarchived channel `{target.name}`.")
        except Exception as e:
            logger.error(f"Error unarchiving `{target}`: {e}")

    async def get_or_create_archive_category(self, guild: discord.Guild) -> discord.CategoryChannel:
        """
        Ensures there is an archive category with available space, creating a new one if necessary.

        :param guild: The Discord guild (server).
        :return: The archive category.
        """
        existing_category = await self.db_handler.get_available_archive_category(guild.id)
        if existing_category:
            category = guild.get_channel(existing_category["category_id"])
            if category:
                return category

        new_category = await guild.create_category(
            name=f"Archive-{len(guild.categories) + 1}",
            reason="Created new archive category due to limit reached"
        )
        await self.db_handler.add_archive_category(new_category.id)
        return new_category


async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    """
    Sets up the ChannelArchiver cog.

    :param client: The Discord bot client instance.
    :param db_handler: An instance of the DatabaseHandler.
    """
    logger.info("[ChannelArchiver] Setting up ChannelArchiver cog...")
    await client.add_cog(ChannelArchiver(client, db_handler))
    logger.info("[ChannelArchiver] ChannelArchiver cog successfully set up.")