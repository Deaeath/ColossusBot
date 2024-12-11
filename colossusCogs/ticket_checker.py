# File: colossusCogs/ticket_checker.py

"""
TicketChecker Cog for ColossusBot
---------------------------------
This cog periodically checks ticket channels for inactivity and takes action.
It integrates with a database handler to determine if a ticket channel is paused 
before performing inactivity checks and subsequent actions.

By default, the ticket checking functionality is disabled. Use the `!ticketmonitor on/off`
command to enable or disable the background task.
"""

import asyncio
import logging
import re
import discord
from discord.ext import commands, tasks
from handlers.database_handler import DatabaseHandler

# Set up logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TicketChecker(commands.Cog):
    """
    A cog that periodically checks ticket channels for inactivity and handles them accordingly.
    Uses the database handler to check if a channel is paused.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler) -> None:
        """
        Initializes the TicketChecker cog.

        :param client: The Discord bot client instance.
        :param db_handler: Instance of the DatabaseHandler to interact with the database.
        """
        self.client = client
        self.db_handler = db_handler
        # The ticket checks are off by default.
        # The `ticketmonitor` command can enable or disable it.
        self.ticket_checks_enabled = False
        self.TICKET_CHANNEL_PATTERN = re.compile(r"ticket-\d+")
        logger.info("TicketChecker initialized successfully with checks disabled.")

    def cog_unload(self):
        """
        Called when the cog is unloaded. Stops the background task loop if it's running.
        """
        if self.check_tickets.is_running():
            self.check_tickets.cancel()

    async def has_recent_activity(self, channel: discord.TextChannel) -> bool:
        """
        Checks if the given channel has recent activity.
        Implement your logic based on your application's requirements.
        For example, check the channel's message history for messages within a certain timeframe.

        :param channel: The Discord text channel to check.
        :return: True if there is recent activity, False otherwise.
        """
        # Example implementation: Check if last message was within the last hour
        async for message in channel.history(limit=1):
            if (discord.utils.utcnow() - message.created_at).total_seconds() < 3600:
                return True
        return False

    @tasks.loop(minutes=5)
    async def check_tickets(self):
        """
        Background task that periodically checks ticket channels for inactivity and handles them accordingly.
        Skips channels that are paused.
        """
        # If checks are disabled, simply return without doing anything.
        if not self.ticket_checks_enabled:
            return

        logger.info("Starting ticket check loop iteration")
        for guild in self.client.guilds:
            for channel in guild.text_channels:
                if self.TICKET_CHANNEL_PATTERN.match(channel.name):
                    # Check if the channel is paused
                    is_paused = await self.db_handler.is_channel_paused(channel.id)
                    if is_paused:
                        logger.info(f"Skipping paused channel: {channel.name} (ID: {channel.id})")
                        continue  # Skip this channel

                    logger.info(f"Checking channel: {channel.name} (ID: {channel.id})")
                    recent_activity = await self.has_recent_activity(channel)
                    if not recent_activity:
                        logger.info(f"No recent activity in channel: {channel.name}, notifying user")
                        try:
                            await channel.send("📌 Please send a message in the next 60 minutes to keep this ticket open, otherwise it will be closed.")
                        except discord.Forbidden:
                            logger.error(f"Insufficient permissions to send messages in channel: {channel.name}")
                            continue
                        except discord.HTTPException as e:
                            logger.error(f"HTTPException when sending message in channel {channel.name}: {e}")
                            continue

                        # Wait for 1 hour before re-checking
                        await asyncio.sleep(3600)

                        # Re-check for recent activity after waiting
                        recent_activity = await self.has_recent_activity(channel)
                        if not recent_activity:
                            logger.info(f"No recent activity after 60 minutes in channel: {channel.name}, closing ticket")
                            try:
                                await channel.send("🔒 Closing this ticket due to inactivity.")
                                await asyncio.sleep(15)
                                await channel.send("$close")
                                await asyncio.sleep(15)
                                await channel.send("$transcript")
                                await asyncio.sleep(15)
                                await channel.send("$delete")
                            except discord.Forbidden:
                                logger.error(f"Insufficient permissions to manage messages in channel: {channel.name}")
                            except discord.HTTPException as e:
                                logger.error(f"HTTPException when managing channel {channel.name}: {e}")

    async def ticketmonitor_command(self, ctx: commands.Context, state: str = None):
        """
        Command to enable or disable the ticket checks.
        By default, ticket checks are disabled until enabled by this command.

        :param ctx: The command context.
        :param state: The desired state, either "on" or "off".
        """
        if state is None:
            # No state given, report current status
            status = "on" if self.ticket_checks_enabled else "off"
            await ctx.send(f"Ticket monitoring is currently **{status}**.")
            return

        state = state.lower()
        if state == "on":
            if self.ticket_checks_enabled:
                await ctx.send("Ticket monitoring is already enabled.")
            else:
                self.ticket_checks_enabled = True
                # Start the loop if not already running
                if not self.check_tickets.is_running():
                    self.check_tickets.start()
                await ctx.send("Ticket monitoring has been **enabled**.")
        elif state == "off":
            if not self.ticket_checks_enabled:
                await ctx.send("Ticket monitoring is already disabled.")
            else:
                self.ticket_checks_enabled = False
                # Stop the loop if it's running
                if self.check_tickets.is_running():
                    self.check_tickets.cancel()
                await ctx.send("Ticket monitoring has been **disabled**.")
        else:
            await ctx.send("Invalid state. Please use `on` or `off`.")


async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    """
    Registers the TicketChecker cog with the bot.

    :param client: The Discord bot client instance.
    :param db_handler: Instance of the DatabaseHandler to interact with the database.
    """
    logger.info("Setting up TicketChecker cog...")
    await client.add_cog(TicketChecker(client, db_handler))
    logger.info("TicketChecker cog setup complete.")