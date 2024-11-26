# File: commands/vote.py

"""
File: commands/vote.py

VoteCommands: Handles Voting Features
--------------------------------------
Provides commands for users to vote for the server and check their vote status.
"""

import random
from datetime import datetime
from typing import Optional
import logging

from discord import Embed, Member
from discord.ext import commands

# Set up logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class VoteCommands(commands.Cog):
    """
    A cog to handle voting commands, allowing users to vote and check their vote status.
    """

    def __init__(self, client: commands.Bot, db_handler):
        """
        Initializes the VoteCommands cog.

        Args:
            client (commands.Bot): The bot instance.
            db_handler: The database handler for vote tracking.
        """
        self.client = client
        self.db_handler = db_handler
        logging.info("VoteCommands cog initialized.")

    @commands.command(name="vote", help="Get the link to vote for the server.")
    async def vote(self, ctx: commands.Context) -> None:
        """
        Sends a link for the user to vote for the server.

        Args:
            ctx (commands.Context): The context of the command invocation.

        Returns:
            None
        """
        logger.info(f"User {ctx.author} requested the vote link.")

        embed = Embed(
            description=f"**[Vote for {ctx.guild.name}](https://top.gg/servers/{ctx.guild.id}/vote)**",
            color=random.randint(0, 0xFFFFFF),
        )
        embed.set_footer(text="Thanks for voting for us!")
        await ctx.send(ctx.author.mention, embed=embed)

    @commands.command(name="votes", help="Check your vote count and time until the next vote.")
    async def votes(self, ctx: commands.Context, member: Optional[Member] = None) -> None:
        """
        Displays the number of votes a user has and the time until their next vote.

        Args:
            ctx (commands.Context): The context of the command invocation.
            member (Optional[Member]): The user to check votes for. Defaults to the command invoker.

        Returns:
            None
        """
        member = member or ctx.author
        logger.info(f"User {ctx.author} requested vote status for {member}.")

        # Fetch vote data from the database
        vote_data = await self.db_handler.fetchone(
            "SELECT votes_count, next_vote_time FROM votes WHERE guild_id = ? AND user_id = ?",
            (ctx.guild.id, member.id),
        )

        votes_count = 0
        next_vote_in = "**Now**"

        if vote_data:
            votes_count, next_vote_time = vote_data
            if next_vote_time:
                now = datetime.utcnow()
                vote_datetime = datetime.strptime(next_vote_time, "%Y-%m-%d %H:%M:%S")

                if now < vote_datetime:
                    remaining_time = vote_datetime - now
                    total_seconds = int(remaining_time.total_seconds())
                    days, remainder = divmod(total_seconds, 86400)
                    hours, remainder = divmod(remainder, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    if days > 0:
                        next_vote_in = f"`{days} days, {hours} hours`"
                    elif hours > 0:
                        next_vote_in = f"`{hours} hours, {minutes} minutes`"
                    elif minutes > 0:
                        next_vote_in = f"`{minutes} minutes, {seconds} seconds`"
                    else:
                        next_vote_in = "`10 seconds`"

        # Create the response embed
        embed = Embed(
            description=f"**{member.display_name} can vote again in:** {next_vote_in}",
            color=random.randint(0, 0xFFFFFF),
        )
        embed.set_author(name=member.display_name, icon_url=member.avatar.url)
        embed.add_field(name="Votes", value=f"{votes_count}", inline=False)
        if member != ctx.author:
            embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)


async def setup(client: commands.Bot) -> None:
    """
    Adds the VoteCommands cog to the bot.

    Args:
        client (commands.Bot): The bot instance.

    Returns:
        None
    """
    db_handler = client.db_handler  # Replace with the actual database handler
    await client.add_cog(VoteCommands(client, db_handler))
    logger.info("VoteCommands cog added successfully.")
