# File: colossusCogs/_cog_template.py

"""
Template Cog for ColossusBot
----------------------------
Use this template for creating new cogs with handler integration. 

This template provides:
- A basic structure for a new cog with a command and background task.
- Integration with the DatabaseHandler for querying and inserting data.
- Logging setup for tracking cog activities.

To use:
1. Copy this file to create a new cog.
2. Modify the class and commands as per your functionality.
3. Ensure to provide the necessary database handler operations.
"""

from discord.ext import commands
import logging
from handlers.database_handler import DatabaseHandler

logger = logging.getLogger("ColossusBot")


class CogTemplate(commands.Cog):
    """
    Template cog for integrating new functionality into ColossusBot.

    This cog provides a starting point for creating commands and background tasks 
    that interact with a database.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler) -> None:
        """
        Initializes the CogTemplate cog.

        :param client: The instance of the Discord bot.
        :param db_handler: Instance of the DatabaseHandler to interact with the database.
        """
        self.client = client
        self.db_handler = db_handler

    @commands.command(name="example", help="An example command with database integration.", usage="!example_command [input_text]")
    async def example_command(self, ctx: commands.Context) -> None:
        """
        Example command that inserts a record into the database.

        :param ctx: The context of the command call.
        """
        await self.db_handler.insert_record("example_table", {"key": "value"})
        await ctx.send("Record added to the database.")

    async def background_task(self) -> None:
        """
        Example background task that fetches records from the database.

        This task logs the number of records fetched from the 'example_table'.
        """
        records = await self.db_handler.fetch_records("example_table")
        logger.info(f"Fetched {len(records)} records from example_table.")


async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    """
    Loads the CogTemplate cog.

    :param client: The instance of the Discord bot.
    :param db_handler: Instance of the DatabaseHandler to interact with the database.
    """
    await client.add_cog(CogTemplate(client, db_handler))
