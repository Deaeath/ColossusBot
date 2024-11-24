"""
EventsHandler: Routes Discord Events
-------------------------------------
Manages Discord event listeners and delegates processing to appropriate modules.
"""

import logging
from discord.ext import commands, tasks
import discord
from colossusCogs.listeners.nsfw_checker import NSFWChecker
from colossusCogs.listeners.flagged_words_alert import FlaggedWordsAlert
from colossusCogs.listeners.repeated_message_alert import RepeatedMessageAlert
from colossusCogs.listeners.active_alert_checker import ActiveAlertChecker
import asyncio 

logger = logging.getLogger("ColossusBot")


class EventsHandler(commands.Cog):
    """
    Handles Discord events and delegates processing to appropriate modules.
    """

    def __init__(self, client, db_handler):
        """
        Initializes the EventsHandler.

        :param client: The Discord bot client instance.
        :param db_handler: The database handler instance for database operations.
        """
        self.client = client
        self.db_handler = db_handler

        # Instantiate modular event-handling classes
        self.nsfw_checker = NSFWChecker(client)
        self.flagged_words_alert = FlaggedWordsAlert(client)
        self.repeated_message_alert = RepeatedMessageAlert(client)
        self.active_alert_checker = ActiveAlertChecker(client, db_handler)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Handles incoming messages and delegates processing to appropriate modules.
        """
        if message.author.bot or not message.guild:
            return

        logger.debug(f"Processing message from {message.author}: {message.content}")

        # Delegate message handling to respective modules
        await self.nsfw_checker.on_message(message)
        await self.flagged_words_alert.on_message(message)
        await self.repeated_message_alert.on_message(message)
        await self.active_alert_checker.on_message(message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """
        Handles reactions and delegates processing to appropriate modules.
        """
        logger.debug(f"Processing reaction: emoji={payload.emoji.name}, message_id={payload.message_id}")

        # Delegate reaction handling to respective modules
        await self.nsfw_checker.on_reaction(payload)
        await self.flagged_words_alert.on_reaction(payload)
        await self.repeated_message_alert.on_reaction(payload)

    @tasks.loop(minutes=5)
    async def check_tickets(self):
        print("Starting ticket check loop")
        for guild in self.client.guilds:
            for channel in guild.text_channels:
                if channel.name.startswith("ticket-"):
                    print(f"Checking channel: {channel.name}")
                    recent_activity = await self.has_recent_activity(channel)
                    if not recent_activity:
                        print(f"No recent activity in channel: {channel.name}, notifying user")
                        await channel.send("Please send a message in the next 60 minutes to keep this ticket open, otherwise it will be closed.")
                        await asyncio.sleep(3600)
                        recent_activity = await self.has_recent_activity(channel)
                        if not recent_activity:
                            print(f"No recent activity after 60 minutes in channel: {channel.name}, closing ticket")
                            await channel.send("$close")
                            await asyncio.sleep(15)
                            await channel.send("$transcript")
                            await asyncio.sleep(15)
                            await channel.send("$delete")

async def setup(client: commands.Bot):
    """
    Registers the EventsHandler cog with the bot.

    :param client: The Discord bot client instance.
    """
    logger.info("Setting up EventsHandler cog...")
    db_handler = client.db_handler
    await client.add_cog(EventsHandler(client, db_handler))
    logger.info("EventsHandler cog setup complete.")
