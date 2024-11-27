# File: commands/vibecheck.py

"""
VibeCheckCommand: Performs Sentiment Analysis on Messages
-------------------------------------------------------
A cog that provides a command to perform sentiment analysis on messages
in a Discord channel or from specific users based on configurable parameters.
"""

from discord.ext import commands
from discord import Embed, TextChannel, Member
from typing import Optional, List, Dict
from datetime import datetime
import asyncio
import random
import json
from vaderSentiment import SentimentIntensityAnalyzer
import logging

# Set up logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class VibeCheckCommand(commands.Cog):
    """
    A cog that allows for sentiment analysis on messages in a Discord server.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initializes the VibeCheckCommand.

        Args:
            client (commands.Bot): The bot instance to associate with the command.
        """
        self.client = client
        logging.info("VibeCheckCommand cog initialized.")

    @commands.command()
    @commands.has_any_role("owner", "head_staff", "moderator", "administrator")
    async def vibecheck(
        self, ctx: commands.Context, messages_count: Optional[int] = None, *, setup: Optional[str] = None
    ) -> None:
        """
        Perform sentiment analysis on messages in a channel or from a specific user.

        Args:
            ctx (commands.Context): The context of the command invocation.
            messages_count (Optional[int]): Number of messages to analyze.
            setup (Optional[str]): A JSON string with parameters for sentiment analysis.

        Returns:
            None: Sends an embed message with the analysis results.
        """
        # Default embed for usage instructions
        embed_help = Embed(
            title="How to use this command?",
            description=f"`!vibecheck <messageCount> <setup>`",
            color=random.randint(0, 0xFFFFFF),
        )
        embed_help.add_field(
            name="What is setup?",
            value=(
                '`{"channel": "<#channel>", "user": "<@user>", "month": monthNumber, '
                '"day": dayNumber, "from": hourStart, "to": hourEnd}`\n'
                "**Required Parts:**\n"
                '`{"channel": "<#channel>", "from": hourStart, "to": hourEnd}`\n'
                "**or**\n"
                '`{"user": "<@user>", "from": hourStart, "to": hourEnd}`'
            ),
            inline=False,
        )

        if messages_count is None or setup is None:
            await ctx.send(embed=embed_help)
            return

        try:
            setup_data = json.loads(setup)
        except json.JSONDecodeError:
            await ctx.send("Invalid JSON format in the `setup` parameter.")
            return

        channel = None
        member = None
        month = datetime.utcnow().strftime("%m")
        day = datetime.utcnow().strftime("%d")
        hour_start = setup_data.get("from")
        hour_end = setup_data.get("to")

        # Validate and parse user
        if "user" in setup_data:
            user_id = int("".join(filter(str.isdigit, setup_data["user"])))
            member = ctx.guild.get_member(user_id)
            if member is None:
                await ctx.send(
                    embed=Embed(
                        description=f"No user found with ID `{user_id}` in **{ctx.guild.name}**",
                        color=random.randint(0, 0xFFFFFF),
                    )
                )
                return

        # Validate and parse channel
        if "channel" in setup_data:
            channel_id = int("".join(filter(str.isdigit, setup_data["channel"])))
            channel = self.client.get_channel(channel_id)
            if channel is None:
                await ctx.send(
                    embed=Embed(
                        description=f"No channel found with ID `{channel_id}`.",
                        color=random.randint(0, 0xFFFFFF),
                    )
                )
                return

        # Validate hours
        if not (0 <= int(hour_start) <= 24 and 0 <= int(hour_end) <= 24):
            await ctx.send(
                embed=Embed(
                    description="Hours must be between 0 and 24.",
                    color=random.randint(0, 0xFFFFFF),
                )
            )
            return

        # Validate date
        if "month" in setup_data:
            month = str(setup_data["month"]).zfill(2)
        if "day" in setup_data:
            day = str(setup_data["day"]).zfill(2)

        # Fetch messages
        messages = await self.fetch_messages(ctx, channel, member, messages_count, month, day, hour_start, hour_end)

        if not messages:
            await ctx.send(embed=Embed(title="No messages found with the specified criteria.", color=0xFF0000))
            return

        # Perform sentiment analysis
        sentiment_results = self.analyze_sentiment(messages)
        await self.send_results(ctx, sentiment_results, channel, member, month, day, hour_start, hour_end)

    async def fetch_messages(
        self,
        ctx: commands.Context,
        channel: Optional[TextChannel],
        member: Optional[Member],
        messages_count: int,
        month: str,
        day: str,
        hour_start: str,
        hour_end: str,
    ) -> List[str]:
        """
        Fetch messages from a specified channel or member.

        Args:
            ctx (commands.Context): The command context.
            channel (Optional[TextChannel]): The target channel.
            member (Optional[Member]): The target user.
            messages_count (int): The number of messages to retrieve.
            month (str): The month of analysis.
            day (str): The day of analysis.
            hour_start (str): The start of the hour range.
            hour_end (str): The end of the hour range.

        Returns:
            List[str]: A list of messages to analyze.
        """
        message_list = []
        search_limit = 1000
        flag = True

        async def is_valid_message(message) -> bool:
            return (
                not message.author.bot
                and (member is None or message.author.id == member.id)
                and message.created_at.strftime("%m") == month
                and message.created_at.strftime("%d") == day
                and int(hour_start) <= int(message.created_at.strftime("%H")) <= int(hour_end)
            )

        while flag:
            messages = (
                await channel.history(limit=search_limit).flatten()
                if channel
                else [message async for channel in ctx.guild.text_channels for message in channel.history(limit=search_limit)]
            )

            for message in messages:
                if await is_valid_message(message):
                    message_list.append(message.content)
                    if len(message_list) >= messages_count:
                        flag = False
                        break

            if len(messages) < search_limit:
                flag = False

        return message_list

    def analyze_sentiment(self, messages: List[str]) -> Dict[str, float]:
        """
        Perform sentiment analysis on the collected messages.

        Args:
            messages (List[str]): The messages to analyze.

        Returns:
            Dict[str, float]: The sentiment analysis results.
        """
        analyser = SentimentIntensityAnalyzer()
        combined_message = " ".join(messages)
        scores = analyser.polarity_scores(combined_message)

        return {
            "positive": scores["pos"] * 100,
            "neutral": scores["neu"] * 100,
            "negative": scores["neg"] * 100,
            "compound": scores["compound"],
        }

    async def send_results(
        self,
        ctx: commands.Context,
        sentiment_results: Dict[str, float],
        channel: Optional[TextChannel],
        member: Optional[Member],
        month: str,
        day: str,
        hour_start: str,
        hour_end: str,
    ) -> None:
        """
        Sends the results of the sentiment analysis.

        Args:
            ctx (commands.Context): The context for the command.
            sentiment_results (Dict[str, float]): The sentiment analysis results.
            channel (Optional[TextChannel]): The target channel (if applicable).
            member (Optional[Member]): The target member (if applicable).
            month (str): The month of analysis.
            day (str): The day of analysis.
            hour_start (str): The start of the hour range.
            hour_end (str): The end of the hour range.

        Returns:
            None: Sends an embed message with the results.
        """
        state = (
            "Based" if sentiment_results["compound"] >= 0.05 else
            "Neutral" if -0.05 < sentiment_results["compound"] < 0.05 else
            "Cringe"
        )

        embed = Embed(
            title=f"Vibe Check Results for {member.name if member else channel.name}",
            description=f"**Overall Sentiment:** {state}",
            color=random.randint(0, 0xFFFFFF),
        )
        embed.add_field(name="Positive %", value=f"{sentiment_results['positive']:.2f}%", inline=True)
        embed.add_field(name="Neutral %", value=f"{sentiment_results['neutral']:.2f}%", inline=True)
        embed.add_field(name="Negative %", value=f"{sentiment_results['negative']:.2f}%", inline=True)
        embed.add_field(name="Date", value=f"{month}-{day}", inline=True)
        embed.add_field(name="Time Range", value=f"{hour_start}:00 to {hour_end}:00", inline=True)
        await ctx.send(embed=embed)


async def setup(client: commands.Bot) -> None:
    """
    Adds the VibeCheckCommand cog to the bot.

    Args:
        client (commands.Bot): The bot instance.

    Returns:
        None: Adds the cog to the bot.
    """
    await client.add_cog(VibeCheckCommand(client))
    logging.info("VibeCheckCommand cog loaded.")
