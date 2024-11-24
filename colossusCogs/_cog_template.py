"""
Template Cog for ColossusBot
----------------------------
Use this template for creating new cogs with handler integration.
"""

from discord.ext import commands
import logging
from handlers.database_handler import DatabaseHandler

logger = logging.getLogger("ColossusBot")


class CogTemplate(commands.Cog):
    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler) -> None:
        self.client = client
        self.db_handler = db_handler

    @commands.command(name="example", help="An example command with database integration.")
    async def example_command(self, ctx: commands.Context) -> None:
        await self.db_handler.insert_record("example_table", {"key": "value"})
        await ctx.send("Record added to the database.")

    async def background_task(self) -> None:
        records = await self.db_handler.fetch_records("example_table")
        logger.info(f"Fetched {len(records)} records from example_table.")


async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    await client.add_cog(CogTemplate(client, db_handler))
