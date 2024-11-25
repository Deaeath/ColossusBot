# colossusCogs/active_alert_checker.py

"""
Active Alert Checker for ColossusBot
------------------------------------
This class handles checking for active alerts in channels. It logs channel activity by tracking the time difference between the last message sent in the channel and the current message. When a channel becomes active, an alert is logged to a designated log channel.
"""

import discord
from datetime import datetime, timezone
import random
import logging


class ActiveAlertChecker:
    """
    Handles checking and logging active alerts for channels.
    """

    def __init__(self, client, db_handler):
        """
        Initializes the ActiveAlertChecker.

        :param client: The Discord bot client instance.
        :param db_handler: The database handler for database operations.
        """
        self.client = client
        self.db_handler = db_handler
        self.logger = logging.getLogger("ColossusBot")
        self.logger.info("Active Alert Checker initialized.")

    async def on_message(self, message: discord.Message):
        """
        Checks for active alerts in a channel and logs activity.

        :param message: The Discord message object.
        """
        # Fetch log channel ID from the database for the guild
        log_channel_id = await self.db_handler.get_log_channel_id(message.guild.id)
        if not log_channel_id:
            return

        log_channel = self.client.get_channel(log_channel_id)
        if log_channel is None:
            return

        chan = self.client.get_channel(message.channel.id)
        embed = discord.Embed(title="Channel Activity Log", color=random.randint(0, 0xFFFFFF))

        try:
            last_message = await chan.fetch_message(chan.last_message_id)
            if last_message is None:
                return

            now = datetime.now(timezone.utc)
            time_diff_seconds = (now - last_message.created_at).total_seconds()

            if time_diff_seconds >= 0:
                log_message = f"{message.channel.name} is now active!"
                embed.add_field(name="Channel Activation", value=log_message, inline=False)
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error in ActiveAlertChecker.on_message: {e}")
