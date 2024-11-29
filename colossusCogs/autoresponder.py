# File: colossusCogs/autoresponder.py

"""
Autoresponder Cog for ColossusBot
---------------------------------
This cog enables automatic responses to specific keywords or phrases within the server.

Features:
- Add, remove, and list autoresponses.
- Automatically responds to messages containing predefined keywords or phrases.
- Integration with DatabaseHandler for persistent storage of autoresponses.
- Logging setup for tracking autoresponder activities.

Usage:
1. Ensure this cog is placed in the `colossusCogs` directory.
2. The corresponding commands are routed via CommandsHandler.
3. The event listener should be integrated into the EventsHandler.

Commands:
- `!add_autoresponse <trigger> <response>`: Adds a new autoresponse.
- `!remove_autoresponse <id>`: Removes an existing autoresponse by ID.
- `!list_autoresponses`: Lists all configured autoresponses.
"""

import discord
from discord.ext import commands
import logging
from handlers.database_handler import DatabaseHandler
from typing import List, Dict, Any, Optional

logger = logging.getLogger("ColossusBot")


class Autoresponder(commands.Cog):
    """
    Autoresponder cog for managing automatic responses based on keywords or phrases.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler) -> None:
        """
        Initializes the Autoresponder cog.

        :param client: The instance of the Discord bot.
        :param db_handler: Instance of the DatabaseHandler to interact with the database.
        """
        self.client = client
        self.db_handler = db_handler
        logger.info("Autoresponder cog initialized.")

    async def add_autoresponse(self, ctx: commands.Context, trigger: str, response: str) -> None:
        """
        Adds a new autoresponse to the database and notifies the user.

        :param ctx: The command context.
        :param trigger: The keyword or phrase to trigger the response.
        :param response: The response message to send.
        """
        guild_id = ctx.guild.id
        autoresponse_id = await self.db_handler.insert_autoresponse(guild_id, trigger, response)
        if autoresponse_id != -1:
            await ctx.send(f"✅ Autoresponse added with ID: `{autoresponse_id}` for trigger `{trigger}`.")
            logger.info(f"Added autoresponse ID {autoresponse_id} with trigger '{trigger}' in guild ID: {guild_id}.")
        else:
            await ctx.send("❌ Failed to add autoresponse. Please try again.")
            logger.error(f"Failed to add autoresponse with trigger '{trigger}' in guild ID: {guild_id}.")

    async def remove_autoresponse(self, ctx: commands.Context, autoresponse_id: int) -> None:
        """
        Removes an existing autoresponse from the database and notifies the user.

        :param ctx: The command context.
        :param autoresponse_id: The unique ID of the autoresponse to remove.
        """
        guild_id = ctx.guild.id
        success = await self.db_handler.delete_autoresponse(guild_id, autoresponse_id)
        if success:
            await ctx.send(f"✅ Autoresponse with ID: `{autoresponse_id}` has been removed.")
            logger.info(f"Removed autoresponse ID {autoresponse_id} from guild ID: {guild_id}.")
        else:
            await ctx.send(f"❌ Failed to remove autoresponse with ID: `{autoresponse_id}`. It may not exist.")
            logger.warning(f"Failed to remove autoresponse ID {autoresponse_id} from guild ID: {guild_id}.")

    async def list_autoresponses(self, ctx: commands.Context) -> None:
        """
        Retrieves all autoresponses for the guild and displays them to the user.

        :param ctx: The command context.
        """
        guild_id = ctx.guild.id
        autoresponses = await self.db_handler.fetch_autoresponses(guild_id)
        if not autoresponses:
            await ctx.send("ℹ️ No autoresponses have been set up in this server.")
            logger.info(f"No autoresponses found for guild ID: {guild_id}.")
            return

        embed = discord.Embed(title="📄 Autoresponses", color=discord.Color.blue())
        for autoresponse in autoresponses:
            embed.add_field(
                name=f"ID: {autoresponse['id']} | Trigger: `{autoresponse['trigger']}`",
                value=f"**Response:** {autoresponse['response']}",
                inline=False
            )

        await ctx.send(embed=embed)
        logger.info(f"Listed {len(autoresponses)} autoresponses for guild ID: {guild_id}.")

    async def handle_message(self, message: discord.Message) -> None:
        """
        Processes incoming messages and sends automatic responses if triggers match.

        :param message: The incoming Discord message.
        """
        if message.author.bot:
            return

        guild_id = message.guild.id
        content = message.content.lower()

        autoresponses = await self.db_handler.fetch_autoresponses(guild_id)

        for autoresponse in autoresponses:
            trigger = autoresponse.get("trigger")
            response = autoresponse.get("response")
            if trigger in content:
                try:
                    await message.channel.send(response)
                    logger.info(f"Sent autoresponse for trigger '{trigger}' in guild ID: {guild_id}.")
                except discord.HTTPException as e:
                    logger.error(f"Failed to send autoresponse: {e}")


async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    """
    Loads the Autoresponder cog.

    :param client: The instance of the Discord bot.
    :param db_handler: Instance of the DatabaseHandler to interact with the database.
    """
    await client.add_cog(Autoresponder(client, db_handler))
    logger.info("Autoresponder cog loaded successfully.")
