# colossusCogs/listeners/repeated_message_alert.py

import discord
from discord.ext import commands
import asyncio
from typing import List, Optional, Tuple, Union
from handlers.database_handler import DatabaseHandler

class RepeatedMessageAlert(commands.Cog):
    """
    Cog to monitor and alert for repeated messages across multiple guilds.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler):
        """
        Initializes the RepeatedMessageAlert cog.

        :param client: The Discord bot instance.
        :param db_handler: The DatabaseHandler instance.
        """
        self.client = client
        self.db_handler = db_handler
        self.SINGLE_USER_REPEAT_THRESHOLD = 5
        self.MIN_WORD_COUNT = 5
        print("RepeatedMessageAlert initialized.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Listener for new messages. Records messages and checks for repetitions.

        :param message: The Discord message.
        """
        if message.author == self.client.user:
            return

        if len(message.content.split()) < self.MIN_WORD_COUNT:
            return  # Ignore messages with fewer than MIN_WORD_COUNT words

        await self.db_handler.insert_repeated_message(
            content=message.content,
            user_id=message.author.id,
            message_id=message.id,
            channel_id=message.channel.id,
            guild_id=message.guild.id,
            timestamp=message.created_at.timestamp()
        )

        await self.check_for_repeated_messages(message)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User) -> None:
        """
        Listener for reaction additions. Handles actions based on reactions to repeated message alerts.

        :param reaction: The reaction added.
        :param user: The user who added the reaction.
        """
        if user == self.client.user:
            return

        valid_reactions = ["✅", "❌", "⚠️", "🔇", "👢", "🔨"]
        if str(reaction.emoji) not in valid_reactions:
            return

        if user.bot:
            return

        alert_info = await self.db_handler.fetch_repeated_alert_message(reaction.message.id)
        if alert_info:
            user_id, channel_id, guild_id = alert_info
            guild = self.client.get_guild(guild_id)
            if not guild:
                return
            target_user = guild.get_member(user_id)
            if not target_user:
                await self.db_handler.delete_repeated_alert_message(reaction.message.id)
                return
            originating_channel = guild.get_channel(channel_id)
            if not originating_channel:
                return

            # Retrieve staff channel ID from the database
            config = await self.db_handler.get_config(guild_id)
            staff_forum_channel_id = config.get("staff_forum_channel_id")
            staff_thread_id = config.get("staff_thread_id")

            staff_channel = guild.get_channel(staff_forum_channel_id)
            if not staff_channel:
                return

            # Determine if staff_channel is a thread or a regular channel
            if isinstance(staff_channel, discord.Thread):
                staff_thread = staff_channel
            else:
                staff_thread = guild.get_channel(staff_thread_id) if staff_thread_id else None

            if str(reaction.emoji) == "✅":
                await self.take_action(target_user, originating_channel, staff_channel, staff_thread)
            elif str(reaction.emoji) == "❌":
                await reaction.message.reply("Repeated message alert ignored.")
                await self.db_handler.delete_repeated_alert_message(reaction.message.id)

    async def check_for_repeated_messages(self, message: discord.Message) -> None:
        """
        Checks if the message content has been repeated across multiple guilds.

        :param message: The Discord message to check.
        """
        user_repeated_messages = await self.db_handler.fetchall(
            """
            SELECT user_id, message_id, channel_id, guild_id, timestamp
            FROM repeated_messages 
            WHERE user_id = ? AND content = ?
            """,
            (message.author.id, message.content)
        )

        all_repeated_messages = await self.db_handler.fetchall(
            """
            SELECT DISTINCT user_id 
            FROM repeated_messages 
            WHERE content = ?
            """,
            (message.content,)
        )

        unique_users = {record[0] for record in all_repeated_messages}

        if len(unique_users) > 1:
            await self.client.change_presence(activity=discord.Game(name=f"🚨 Bot Alert! {message.author}"))
            await self.send_alert(message, user_repeated_messages)

    async def send_alert(
        self,
        message: discord.Message,
        repeated_messages: List[Tuple[int, int, int, int, float]]
    ) -> None:
        """
        Sends an alert to the staff channel about the repeated messages.

        :param message: The Discord message that triggered the alert.
        :param repeated_messages: List of tuples containing repeated message details.
        """
        config = await self.db_handler.get_config(message.guild.id)
        if not config:
            return

        staff_forum_channel_id = config.get("staff_forum_channel_id")
        staff_thread_id = config.get("staff_thread_id")

        staff_channel = message.guild.get_channel(staff_forum_channel_id)
        if not staff_channel:
            return

        # Determine if staff_channel is a thread or a regular channel
        if isinstance(staff_channel, discord.Thread):
            staff_thread = staff_channel
        else:
            staff_thread = message.guild.get_channel(staff_thread_id) if staff_thread_id else None

        if not staff_thread:
            return

        occurrences_by_user = {}
        for record in repeated_messages:
            user_id, message_id, channel_id, guild_id, timestamp = record
            guild = self.client.get_guild(guild_id)
            if not guild:
                continue
            channel = guild.get_channel(channel_id)
            user = guild.get_member(user_id)
            if channel and user:
                occurrences_by_user[user_id] = (
                    f"<@{user.id}> - {discord.utils.format_dt(discord.utils.snowflake_time(message_id), 'F')} - {channel.mention}"
                )

        occurrences_text = "\n".join(occurrences_by_user.values())
        if len(occurrences_text) > 1024:
            occurrences_text = occurrences_text[:1020] + "..."

        embed = discord.Embed(
            title="**Repeated Message Alert Across Network!**",
            description=f"A message has been repeated multiple times across servers.",
            color=discord.Color.orange()
        )
        embed.add_field(name="**Message Content**", value=message.content[:1024], inline=False)
        embed.add_field(name="**Number of Occurrences**", value=len(repeated_messages), inline=False)
        embed.add_field(name="**Message Occurrences**", value=occurrences_text, inline=False)
        embed.add_field(
            name="**Action Required**",
            value="React with ✅ to delete and take further action or ❌ to ignore this message permanently.",
            inline=False
        )
        embed.set_footer(text=f"User ID: {message.author.id}")

        alert_message = await staff_thread.send(embed=embed)
        await alert_message.add_reaction("✅")
        await alert_message.add_reaction("❌")

        await self.db_handler.insert_repeated_alert_message(
            message_id=alert_message.id,
            user_id=message.author.id,
            channel_id=message.channel.id,
            guild_id=message.guild.id
        )

    async def take_action(
        self,
        user: discord.Member,
        originating_channel: discord.abc.GuildChannel,
        staff_channel: Union[discord.Thread, discord.TextChannel],
        staff_thread: Optional[discord.Thread]
    ) -> None:
        """
        Takes action against the user based on staff's decision.

        :param user: The user to take action against.
        :param originating_channel: The channel where the original message was sent.
        :param staff_channel: The staff thread/channel where actions are discussed.
        :param staff_thread: The staff thread object if staff_channel is a thread.
        """
        action_embed = discord.Embed(
            title="Take Action on Repeated Messages",
            description=f"Choose an action to take against {user.mention}:",
            color=discord.Color.red()
        )
        action_embed.add_field(name="Available Actions", value="⚠️ Warn\n🔇 Mute\n👢 Kick\n🔨 Ban", inline=False)

        action_message = await staff_channel.send(embed=action_embed)
        for reaction in ["⚠️", "🔇", "👢", "🔨"]:
            await action_message.add_reaction(reaction)

        await self.db_handler.insert_repeated_action_message(
            message_id=action_message.id,
            user_id=user.id,
            channel_id=originating_channel.id,
            guild_id=staff_channel.guild.id
        )

    async def get_staff_channel_id(self, guild_id: int) -> Optional[int]:
        """
        Retrieves the staff forum channel ID from the database configuration.

        :param guild_id: ID of the guild.
        :return: Staff forum channel ID or None if not set.
        """
        config = await self.db_handler.get_config(guild_id)
        return config.get("staff_forum_channel_id") if config else None

async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    """
    Sets up the RepeatedMessageAlert cog.

    :param client: The Discord bot instance.
    :param db_handler: The DatabaseHandler instance.
    """
    print("Setting up RepeatedMessageAlert cog...")
    cog = RepeatedMessageAlert(client, db_handler)
    await client.add_cog(cog)
    print("RepeatedMessageAlert cog loaded successfully.")
