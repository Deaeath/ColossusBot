# File: colossusCogs/Listeners/anti_hacking_checker.py

"""
Anti-Hacking Cog for ColossusBot
--------------------------------
This cog tracks the rate of sensitive actions performed by any member (including bots)
to detect possible account compromise or abuse. If the number of actions exceeds a defined
threshold within a specified time window, a security alert is triggered:
  - A designated security channel (configured per guild) is notified.
  - The bot's presence is updated to indicate a security alert.
  - The incident is logged and recorded in the database via the DatabaseHandler.

Configuration options:
  - ACTION_THRESHOLD: The maximum allowed actions within the TIME_WINDOW before triggering an alert.
  - TIME_WINDOW: The time window (in seconds) in which actions are counted.
  - The security channel is determined from the guild configuration in the database,
    falling back to a default if not set.
"""

import time
import random
import asyncio
import traceback
import discord
from discord.ext import commands
import logging

from handlers.database_handler import DatabaseHandler

logger = logging.getLogger("ColossusBot")


class AntiHacking(commands.Cog):
    """
    Anti-Hacking Cog for ColossusBot.
    Tracks sensitive actions from all users (including bots) and triggers alerts if a user
    performs too many actions within a short time period.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler) -> None:
        """
        Initializes the AntiHacking cog.
        :param client: The instance of the Discord bot.
        :param db_handler: Instance of the DatabaseHandler to interact with the database.
        """
        self.client = client
        self.db_handler = db_handler
        logger.info("[AntiHacking] AntiHacking cog initialized.")

        # Dictionary to track timestamps of sensitive actions per user (using (guild_id, user_id) as key)
        self.user_actions = {}

        # Configuration for action threshold and time window
        self.ACTION_THRESHOLD = 15  # Actions allowed in the time window
        self.TIME_WINDOW = 5        # Time window in seconds

        # Default security channel ID (fallback if none is configured for the guild)
        self.default_security_channel_id = 1135648274007724062

        # Start the background task with error handling
        self.client.loop.create_task(self.background_task())

    async def track_action(self, user_id: int, user_name: str, guild: discord.Guild) -> None:
        """
        Tracks an action performed by a user in a specific guild and handles suspicious
        activity if the threshold is exceeded.
        :param user_id: The ID of the user performing the action.
        :param user_name: The display name of the user.
        :param guild: The guild in which the action occurred.
        """
        try:
            current_time = time.time()
            key = (guild.id, user_id)
            if key not in self.user_actions:
                self.user_actions[key] = []
            self.user_actions[key].append(current_time)
            self.user_actions[key] = [
                t for t in self.user_actions[key] if current_time - t <= self.TIME_WINDOW
            ]
            if len(self.user_actions[key]) >= self.ACTION_THRESHOLD:
                await self.handle_suspicious_activity(user_id, user_name, guild)
        except Exception as e:
            logger.exception(f"Error tracking action for user {user_id} in guild {guild.id}: {e}")

    async def handle_suspicious_activity(self, user_id: int, user_name: str, guild: discord.Guild) -> None:
        """
        Handles suspicious activity by alerting the configured security channel, updating the bot's presence,
        logging the incident, and recording it in the database.
        :param user_id: The ID of the suspicious user.
        :param user_name: The display name of the suspicious user.
        :param guild: The guild in which the suspicious activity was detected.
        """
        try:
            # Retrieve guild configuration from the database
            config = await self.db_handler.get_config(guild.id)
            if config and config.get("log_channel_id"):
                security_channel_id = config["log_channel_id"]
            else:
                security_channel_id = self.default_security_channel_id

            security_channel = self.client.get_channel(security_channel_id)
            alert_message = (
                f"🚨 **Security Alert:** User **{user_name}** (ID: {user_id}) has performed too many "
                f"sensitive actions in {self.TIME_WINDOW} seconds in **{guild.name}**. Possible account compromise detected."
            )

            if security_channel:
                if hasattr(security_channel, "send"):
                    try:
                        await security_channel.send(alert_message)
                    except Exception as e:
                        logger.exception(f"Failed to send alert message in channel {security_channel_id}: {e}")
                else:
                    logger.warning(f"Security channel {security_channel_id} does not support sending messages.")
            else:
                logger.warning(f"Security channel with ID {security_channel_id} not found.")

            try:
                await self.client.change_presence(activity=discord.Game(name=f"🚨 Hacked Account Alert! {user_name}"))
            except Exception as e:
                logger.exception(f"Failed to update bot presence: {e}")

            logger.warning(f"Suspicious activity detected from user {user_name} (ID: {user_id}) in guild {guild.name}.")
            await self.db_handler.insert_record("security_incidents", {
                "user_id": user_id,
                "user_name": user_name,
                "incident": f"Excessive sensitive actions detected in guild {guild.name}."
            })
        except Exception as e:
            logger.exception(f"Error handling suspicious activity for user {user_id} in guild {guild.id}: {e}")
        finally:
            key = (guild.id, user_id)
            if key in self.user_actions:
                del self.user_actions[key]

    async def update_security_config(self, ctx, threshold=None, time_window=None, channel=None):
        """
        Updates the anti-hacking configuration for the guild.
        Parameters:
         - threshold (int): New action threshold.
         - time_window (int): New time window in seconds.
         - channel (discord.TextChannel): New security channel for alerts.
        This function updates both the cog's internal parameters and persists the new security channel
        via the DatabaseHandler (assuming the guild_config table uses 'log_channel_id' for the security channel).
        """
        try:
            guild = ctx.guild
            msg_parts = []

            if threshold is not None:
                self.ACTION_THRESHOLD = threshold
                msg_parts.append(f"Threshold set to {threshold}")
            if time_window is not None:
                self.TIME_WINDOW = time_window
                msg_parts.append(f"Time window set to {time_window} seconds")
            if channel is not None:
                # Update the security channel configuration in the database.
                await self.db_handler.set_config(guild.id, log_channel_id=channel.id)
                msg_parts.append(f"Security channel set to {channel.mention}")

            if msg_parts:
                await ctx.send("Security configuration updated: " + "; ".join(msg_parts))
            else:
                await ctx.send("No valid configuration parameters provided.")
        except Exception as e:
            logger.exception(f"Failed to update security configuration: {e}")
            await ctx.send("An error occurred while updating the security configuration.")

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context) -> None:
        if ctx.guild is None:
            return
        try:
            await self.track_action(ctx.author.id, ctx.author.display_name, ctx.guild)
        except Exception as e:
            logger.exception(f"Error in on_command listener: {e}")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        try:
            async for entry in channel.guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_delete):
                if entry.target.id == channel.id:
                    await self.track_action(entry.user.id, entry.user.display_name, channel.guild)
                    break
        except Exception as e:
            logger.exception(f"Error in on_guild_channel_delete listener: {e}")

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel) -> None:
        try:
            async for entry in channel.guild.audit_logs(limit=5, action=discord.AuditLogAction.channel_create):
                if entry.target.id == channel.id:
                    await self.track_action(entry.user.id, entry.user.display_name, channel.guild)
                    break
        except Exception as e:
            logger.exception(f"Error in on_guild_channel_create listener: {e}")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role) -> None:
        try:
            async for entry in role.guild.audit_logs(limit=5, action=discord.AuditLogAction.role_delete):
                if entry.target.id == role.id:
                    await self.track_action(entry.user.id, entry.user.display_name, role.guild)
                    break
        except Exception as e:
            logger.exception(f"Error in on_guild_role_delete listener: {e}")

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role) -> None:
        try:
            async for entry in role.guild.audit_logs(limit=5, action=discord.AuditLogAction.role_create):
                if entry.target.id == role.id:
                    await self.track_action(entry.user.id, entry.user.display_name, role.guild)
                    break
        except Exception as e:
            logger.exception(f"Error in on_guild_role_create listener: {e}")

    @commands.Cog.listener()
    async def on_guild_member_update(self, before: discord.Member, after: discord.Member) -> None:
        try:
            async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                if entry.target.id == after.id:
                    await self.track_action(entry.user.id, entry.user.display_name, after.guild)
                    break
        except Exception as e:
            logger.exception(f"Error in on_guild_member_update listener: {e}")

    async def background_task(self) -> None:
        while True:
            try:
                total_tracked = sum(len(timestamps) for timestamps in self.user_actions.values())
                logger.info(f"[AntiHacking] Tracking {total_tracked} actions from {len(self.user_actions)} entries.")
            except Exception as e:
                logger.exception(f"Error in background task: {e}")
            await asyncio.sleep(60)


async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    try:
        await client.add_cog(AntiHacking(client, db_handler))
        logger.info("[AntiHacking] AntiHacking cog successfully set up.")
    except Exception as e:
        logger.exception(f"Failed to set up AntiHacking cog: {e}")
