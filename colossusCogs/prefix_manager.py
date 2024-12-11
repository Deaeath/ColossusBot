# File: colossusCogs/prefix_manager.py

"""
PrefixManager Cog
-----------------
This cog provides a command to change the bot's prefix on a per-guild basis and persists changes to the database.
Mentions will always work as a prefix.
"""

import logging
from discord.ext import commands
from handlers.database_handler import DatabaseHandler

# Set up logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PrefixManager(commands.Cog):
    """
    A cog that provides a command to update the bot's prefix per guild and saves it to the database.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler) -> None:
        """
        Initialize the PrefixManager cog.

        :param client: The Discord bot client instance.
        :param db_handler: The database handler instance for database operations.
        """
        self.client = client
        self.db_handler = db_handler
        logger.info("PrefixManager initialized successfully.")

    async def setprefix(self, ctx: commands.Context, *, new_prefix: str) -> None:
        """
        Change the bot's command prefix for the current guild and persist it to the database.

        :param ctx: The command context.
        :param new_prefix: The new prefix to set for this guild.
        """
        if ctx.guild is None:
            await ctx.send("This command can only be used in a guild.")
            return

        guild_id = ctx.guild.id
        self.client.guild_prefixes[guild_id] = new_prefix
        await self.set_guild_prefix_in_db(guild_id, new_prefix)

        await ctx.send(f"Prefix for this guild updated to: `{new_prefix}`")
        logger.info(f"Prefix for guild {guild_id} changed to: {new_prefix}")

    async def set_guild_prefix_in_db(self, guild_id: int, prefix: str) -> None:
        """
        Upsert the prefix for a guild in the database.

        :param guild_id: The ID of the guild.
        :param prefix: The prefix to store.
        """
        query = """
            INSERT INTO guild_prefixes (guild_id, prefix)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET prefix = ?
        """
        await self.db_handler.execute(query, (guild_id, prefix, prefix))


async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    """
    Registers the PrefixManager cog with the bot.

    :param client: The Discord bot client instance.
    :param db_handler: The database handler instance.
    """
    logger.info("Setting up PrefixManager cog...")
    await client.add_cog(PrefixManager(client, db_handler))
    logger.info("PrefixManager cog setup complete.")