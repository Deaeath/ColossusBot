# File: handlers/events_handler.py

"""
    EventsHandler: Routes Discord Events
    -------------------------------------
    Manages Discord event listeners and delegates processing to appropriate modules.
"""

from datetime import datetime, timedelta, timezone  # Ensure timezone is imported
import logging
import re  # Import the re module for regex operations
from discord.ext import commands, tasks
import discord
from colossusCogs.aichatbot import AIChatbot
from colossusCogs.listeners.active_alert_checker import ActiveAlertChecker
from colossusCogs.listeners.flagged_words_alert import FlaggedWordsAlert
from colossusCogs.listeners.nsfw_checker import NSFWChecker
from colossusCogs.listeners.repeated_message_alert import RepeatedMessageAlert
from colossusCogs.reaction_role_menu import ReactionRoleMenu
from colossusCogs.autoresponder import Autoresponder  # Import the Autoresponder cog
from handlers.database_handler import DatabaseHandler
import asyncio

logger = logging.getLogger("ColossusBot")

# Compile the regex pattern once for efficiency
TICKET_CHANNEL_PATTERN = re.compile(r'^ticket-\d+$')


class EventsHandler(commands.Cog):
    """
    Handles Discord events and delegates processing to appropriate modules.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler):
        """
        Initializes the EventsHandler.

        :param client: The Discord bot client instance.
        :param db_handler: The database handler instance for database operations.
        """
        self.client = client
        self.db_handler = db_handler

        # Instantiate modular event-handling classes
        self.ai_chat_bot = AIChatbot(client, db_handler)
        self.nsfw_checker = NSFWChecker(client, db_handler)
        self.flagged_words_alert = FlaggedWordsAlert(client, db_handler)
        self.repeated_message_alert = RepeatedMessageAlert(client, db_handler)
        self.active_alert_checker = ActiveAlertChecker(client, db_handler)
        self.reaction_role_menu = ReactionRoleMenu(client, db_handler)  # Instantiate ReactionRoleMenu
        self.autoresponder = Autoresponder(client, db_handler)  # Instantiate Autoresponder

        # Start background tasks
        self.check_tickets.start()

    def cog_unload(self):
        """
        Called when the cog is unloaded. Cancels any running background tasks.
        """
        self.check_tickets.cancel()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Handles incoming messages and delegates processing to appropriate modules.
        Also checks for the "pause" command in ticket channels to pause ticket checking.

        :param message: The message object.
        """
        if message.author.bot or not message.guild:
            return

        logger.debug(f"Processing message from {message.author}: {message.content}")

        # Check if the message is in a ticket channel
        if TICKET_CHANNEL_PATTERN.match(message.channel.name):
            # Check if the message content is "pause" (case-insensitive)
            if message.content.strip().lower() == "pause":
                # Set the channel as paused in the database
                await self.db_handler.set_channel_paused(message.channel.id, True)
                try:
                    await message.channel.send("✅ Ticket checking and closing has been **paused** for this channel.")
                    logger.info(f"Paused ticket checking for channel: {message.channel.name} (ID: {message.channel.id})")
                except discord.Forbidden:
                    logger.error(f"Insufficient permissions to send messages in channel: {message.channel.name}")
                except discord.HTTPException as e:
                    logger.error(f"HTTPException when sending pause confirmation in channel {message.channel.name}: {e}")
                return  # Optionally, stop further processing if needed

        # Delegate message handling to respective modules
        await self.ai_chat_bot.on_message(message)
        await self.nsfw_checker.on_message(message)
        await self.flagged_words_alert.on_message(message)
        await self.repeated_message_alert.on_message(message)
        await self.active_alert_checker.on_message(message)

        # Delegate message handling to Autoresponder cog
        await self.autoresponder.handle_message(message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """
        Handles reactions added to messages and delegates processing to appropriate modules.
        """
        logger.debug(f"Processing reaction add: emoji={payload.emoji.name}, message_id={payload.message_id}")

        # Fetch the user who reacted
        try:
            user = self.client.get_user(payload.user_id)
            if user is None:
                user = await self.client.fetch_user(payload.user_id)
        except discord.NotFound:
            logger.warning(f"User with ID {payload.user_id} not found.")
            return
        except discord.HTTPException as e:
            logger.error(f"Failed to fetch user with ID {payload.user_id}: {e}")
            return

        # Fetch the channel
        try:
            channel = self.client.get_channel(payload.channel_id)
            if channel is None:
                channel = await self.client.fetch_channel(payload.channel_id)
        except discord.NotFound:
            logger.warning(f"Channel with ID {payload.channel_id} not found.")
            return
        except discord.HTTPException as e:
            logger.error(f"Failed to fetch channel with ID {payload.channel_id}: {e}")
            return

        # Fetch the message
        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            logger.warning(f"Message with ID {payload.message_id} not found.")
            return
        except discord.HTTPException as e:
            logger.error(f"Failed to fetch message with ID {payload.message_id}: {e}")
            return

        # Get the reaction object
        reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
        if reaction is None:
            # If the reaction is not found in cache, attempt to fetch it
            try:
                # Note: discord.py does not provide a direct way to fetch a single reaction.
                # As a workaround, you can re-fetch the message's reactions.
                await message.remove_reaction(payload.emoji, user)  # Attempt to remove to trigger cache update
                reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
            except discord.HTTPException as e:
                logger.error(f"Failed to update/fetch reaction: {e}")
                return

        if reaction is None:
            logger.warning(f"Reaction {payload.emoji.name} not found in message {payload.message_id}.")
            return

        # Now, 'reaction' should have the 'count' attribute
        logger.debug(f"Reaction count: {reaction.count}")

        # Delegate reaction handling to respective modules with both reaction and user
        await self.nsfw_checker.on_reaction(reaction, user)
        await self.flagged_words_alert.on_reaction(reaction, user)
        await self.repeated_message_alert.on_reaction(reaction, user)

        # Delegate reaction handling to ReactionRoleMenu cog
        await self.reaction_role_menu.handle_reaction_add(payload)

    @tasks.loop(minutes=5)
    async def check_tickets(self):
        """
        Background task that periodically checks ticket channels for inactivity and handles them accordingly.
        Skips channels that are paused.
        """
        logger.info("Starting ticket check loop")
        for guild in self.client.guilds:
            for channel in guild.text_channels:
                if TICKET_CHANNEL_PATTERN.match(channel.name):
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
                        except discord.HTTPException as e:
                            logger.error(f"HTTPException when sending message in channel {channel.name}: {e}")

                        await asyncio.sleep(3600)  # Wait for 1 hour

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

    async def has_recent_activity(self, channel: discord.TextChannel) -> bool:
        """
        Checks if there has been recent activity in the channel.

        :param channel: The channel to check.
        :return: True if recent activity exists, False otherwise.
        """
        try:
            # Fetch the last 100 messages
            messages = []
            async for msg in channel.history(limit=100):
                messages.append(msg)
            if messages:
                # Define "recent" as within the last hour using aware datetime
                cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
                for msg in messages:
                    if msg.created_at > cutoff:
                        return True
            return False
        except Exception as e:
            logger.error(f"Error checking recent activity in channel {channel.id}: {e}")
            return False

async def setup(client: commands.Bot):
    """
    Registers the EventsHandler cog with the bot.

    :param client: The Discord bot client instance.
    """
    logger.info("Setting up EventsHandler cog...")
    db_handler = client.db_handler
    await client.add_cog(EventsHandler(client, db_handler))
    logger.info("EventsHandler cog setup complete.")
