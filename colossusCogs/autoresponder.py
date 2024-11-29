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
2. The corresponding commands should be added to the CommandsHandler.
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
from typing import List, Dict, Any

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

    async def add_autoresponse(self, guild_id: int, trigger: str, response: str) -> Dict[str, Any]:
        """
        Adds a new autoresponse to the database.

        :param guild_id: The ID of the guild (server).
        :param trigger: The keyword or phrase to trigger the response.
        :param response: The response message to send.
        :return: The inserted record.
        """
        record = {
            "guild_id": guild_id,
            "trigger": trigger.lower(),
            "response": response
        }
        result = await self.db_handler.insert_record("autoresponses", record)
        logger.info(f"Added autoresponse: {record}")
        return result

    async def remove_autoresponse(self, guild_id: int, autoresponse_id: int) -> bool:
        """
        Removes an existing autoresponse from the database.

        :param guild_id: The ID of the guild (server).
        :param autoresponse_id: The unique ID of the autoresponse to remove.
        :return: True if removal was successful, False otherwise.
        """
        condition = {"guild_id": guild_id, "id": autoresponse_id}
        result = await self.db_handler.delete_record("autoresponses", condition)
        if result:
            logger.info(f"Removed autoresponse ID: {autoresponse_id} from guild ID: {guild_id}")
        else:
            logger.warning(f"Failed to remove autoresponse ID: {autoresponse_id} from guild ID: {guild_id}")
        return result

    async def list_autoresponses(self, guild_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all autoresponses for a specific guild.

        :param guild_id: The ID of the guild (server).
        :return: A list of autoresponse records.
        """
        condition = {"guild_id": guild_id}
        records = await self.db_handler.fetch_records("autoresponses", condition)
        logger.info(f"Fetched {len(records)} autoresponses for guild ID: {guild_id}")
        return records

    async def handle_message(self, message: discord.Message) -> None:
        """
        Processes incoming messages and sends automatic responses if triggers match.

        :param message: The incoming Discord message.
        """
        if message.author.bot:
            return

        guild_id = message.guild.id
        content = message.content.lower()

        autoresponses = await self.db_handler.fetch_records("autoresponses", {"guild_id": guild_id})

        for autoresponse in autoresponses:
            trigger = autoresponse.get("trigger")
            response = autoresponse.get("response")
            if trigger in content:
                try:
                    await message.channel.send(response)
                    logger.info(f"Sent autoresponse for trigger '{trigger}' in guild ID: {guild_id}")
                except discord.HTTPException as e:
                    logger.error(f"Failed to send autoresponse: {e}")

    # Optional: Background tasks or additional functionalities can be added here.


async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    """
    Loads the Autoresponder cog.

    :param client: The instance of the Discord bot.
    :param db_handler: Instance of the DatabaseHandler to interact with the database.
    """
    await client.add_cog(Autoresponder(client, db_handler))
    logger.info("Autoresponder cog loaded successfully.")
