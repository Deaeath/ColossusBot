# colossusCogs/listeners/flagged_words_alert.py

import discord
from discord.ext import commands
import re
from Flags.flagged_words import flagged_phrases
from handlers.database_handler import DatabaseHandler
from typing import Optional, Tuple, Union

class FlaggedWordsAlert(commands.Cog):
    """
    Cog to monitor and alert for flagged word usage in messages.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler):
        """
        Initializes the FlaggedWordsAlert cog.

        :param client: The Discord bot instance.
        :param db_handler: The DatabaseHandler instance.
        """
        self.client = client
        self.db_handler = db_handler
        print("FlaggedWordsAlert initialized.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Listener for new messages. Checks for flagged words and handles alerts.

        :param message: The Discord message.
        """
        if message.author == self.client.user:
            return

        contains_flagged_word, detected_word = self.contains_flagged_words(message.content)
        if contains_flagged_word:
            await self.record_message(message)
            await self.client.change_presence(activity=discord.Game(name=f"❌ Flagged Word Alert! {message.author}"))
            await self.send_alert(message, detected_word)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User) -> None:
        """
        Listener for reaction additions. Handles actions based on reactions to alert messages.

        :param reaction: The reaction added.
        :param user: The user who added the reaction.
        """
        if user == self.client.user:
            return

        valid_reactions = ["✅", "❌", "⚠️", "🔇", "👢", "🔨"]
        if str(reaction.emoji) not in valid_reactions:
            return

        alert_info = await self.db_handler.fetch_flagged_alert_message(reaction.message.id)
        if alert_info:
            user_id, channel_id, guild_id = alert_info
            guild = self.client.get_guild(guild_id)
            if not guild:
                return
            target_user = guild.get_member(user_id)
            if not target_user:
                await self.db_handler.delete_flagged_alert_message(reaction.message.id)
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
                await self.take_action(target_user, staff_channel, originating_channel, staff_thread)
            elif str(reaction.emoji) == "❌":
                await reaction.message.reply("Flagged words alert ignored.")
                await self.db_handler.delete_flagged_alert_message(reaction.message.id)

    def contains_flagged_words(self, content: str) -> Tuple[bool, Optional[str]]:
        """
        Checks if the content contains any flagged words or patterns.

        :param content: The message content to check.
        :return: Tuple indicating if a flagged word was found and the detected word.
        """
        content_lower = content.lower()
        for phrase in flagged_phrases:
            if isinstance(phrase, str):
                if phrase in content_lower:
                    return True, phrase
            elif isinstance(phrase, re.Pattern):
                match = phrase.search(content)
                if match:
                    return True, match.group()
        return False, None

    async def record_message(self, message: discord.Message) -> None:
        """
        Records a flagged message into the database.

        :param message: The Discord message containing the flagged word.
        """
        await self.db_handler.insert_flagged_message(
            content=message.content,
            user_id=message.author.id,
            message_id=message.id,
            channel_id=message.channel.id,
            timestamp=message.created_at.timestamp()
        )

    async def send_alert(self, message: discord.Message, detected_word: str) -> None:
        """
        Sends an alert to the staff channel about the flagged word usage.

        :param message: The Discord message containing the flagged word.
        :param detected_word: The flagged word that was detected.
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

        embed = discord.Embed(
            title="**Flagged Word Alert!**",
            description=f"Flagged word usage detected in {message.guild.name}.",
            color=discord.Color.red()
        )
        embed.add_field(name="**Detected Flagged Word**", value=detected_word, inline=False)
        embed.add_field(name="**Message Content**", value=message.content[:1024], inline=False)
        embed.add_field(name="**User**", value=message.author.mention, inline=False)
        embed.add_field(name="**Channel**", value=message.channel.mention, inline=False)
        embed.add_field(name="**Message Link**", value=message.jump_url, inline=False)
        embed.set_footer(text=f"User ID: {message.author.id}")

        alert_message = await staff_thread.send(embed=embed)
        await alert_message.add_reaction("✅")
        await alert_message.add_reaction("❌")

        await self.db_handler.insert_flagged_alert_message(
            message_id=alert_message.id,
            user_id=message.author.id,
            channel_id=message.channel.id,
            guild_id=message.guild.id
        )

    async def take_action(
        self,
        user: discord.Member,
        staff_channel: Union[discord.Thread, discord.TextChannel],
        originating_channel: discord.abc.GuildChannel,
        staff_thread: Optional[discord.Thread]
    ) -> None:
        """
        Presents action options to the staff for handling the flagged user.

        :param user: The user to take action against.
        :param staff_channel: The staff thread/channel where actions are discussed.
        :param originating_channel: The channel where the original message was sent.
        :param staff_thread: The staff thread object if staff_channel is a thread.
        """
        action_embed = discord.Embed(
            title="Take Action on Flagged Word Usage",
            description=f"Choose an action to take against {user.mention}:",
            color=discord.Color.red()
        )
        action_embed.add_field(name="Available Actions", value="❌ Unverify\n⚠️ Warn\n🔇 Mute\n👢 Kick\n🔨 Ban", inline=False)

        action_message = await staff_channel.send(embed=action_embed)

        for reaction in ["❌", "⚠️", "🔇", "👢", "🔨"]:
            await action_message.add_reaction(reaction)

        await self.db_handler.insert_flagged_action_message(
            message_id=action_message.id,
            user_id=user.id,
            channel_id=originating_channel.id,
            guild_id=staff_channel.guild.id
        )

async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    """
    Sets up the FlaggedWordsAlert cog.

    :param client: The Discord bot instance.
    :param db_handler: The DatabaseHandler instance.
    """
    print("Setting up FlaggedWordsAlert cog...")
    cog = FlaggedWordsAlert(client, db_handler)
    await client.add_cog(cog)
    print("FlaggedWordsAlert cog loaded successfully.")
