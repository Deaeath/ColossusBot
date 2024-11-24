from discord.ext import commands
from discord import Embed, Member
from datetime import datetime
from typing import Optional
import random


class VoteCommands(commands.Cog):
    """
    A cog to handle voting commands, allowing users to vote and check their vote status.
    """

    def __init__(self, client: commands.Bot, db_handler):
        self.client = client
        self.db_handler = db_handler

    @commands.command()
    async def vote(self, ctx: commands.Context) -> None:
        """
        Sends a link for the user to vote for the server.

        Args:
            ctx (commands.Context): The context of the command invocation.

        Returns:
            None: Sends an embed with the vote link.
        """
        embed = Embed(
            description=f"**[{ctx.guild.name}](https://top.gg/servers/{ctx.guild.id}/vote)**",
            color=random.randint(0, 0xFFFFFF),
        )
        embed.set_footer(text="Thanks for voting for us!")
        await ctx.send(ctx.author.mention, embed=embed)

    @commands.command()
    async def votes(self, ctx: commands.Context, member: Optional[Member] = None) -> None:
        """
        Displays the number of votes a user has and the time until their next vote.

        Args:
            ctx (commands.Context): The context of the command invocation.
            member (Optional[Member]): The user to check votes for. Defaults to the command invoker.

        Returns:
            None: Sends an embed with the user's vote information.
        """
        if member is None:
            member = ctx.author

        # Fetch vote data from the database
        member_votes = self.db_handler.child("votes").child(ctx.guild.id).child(member.id).get().val()
        votes_count = 0
        next_vote_in = "**Now**"

        if member_votes is not None:
            # Extract vote time and count information
            vote_time = {
                "year": 0,
                "month": 0,
                "day": 0,
                "hour": 0,
                "minute": 0,
                "second": 0,
            }
            for key, value in member_votes.items():
                if key in vote_time:
                    vote_time[key] = value
                elif key == "count":
                    votes_count = value

            # Calculate the time remaining until the next vote
            now = datetime.utcnow()
            vote_datetime = datetime(
                vote_time["year"], vote_time["month"], vote_time["day"],
                vote_time["hour"], vote_time["minute"], vote_time["second"]
            )

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
            description=f"**{member.name if member else 'You'} can vote again in:** {next_vote_in}",
            color=random.randint(0, 0xFFFFFF),
        )
        embed.set_author(name=member.name, icon_url=member.avatar_url)
        embed.add_field(name="Votes", value=f"{votes_count}", inline=False)
        if member != ctx.author:
            embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


async def setup(client: commands.Bot) -> None:
    """
    Add the VoteCommands cog to the bot.

    Args:
        client (commands.Bot): The bot instance.

    Returns:
        None: Adds the cog.
    """
    db_handler = client.db_handler  # Replace with your actual database handler
    await client.add_cog(VoteCommands(client, db_handler))
