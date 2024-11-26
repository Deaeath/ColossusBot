# File: commands/google.py

"""
Google Command Cog: Perform Google Searches and Return Top Results
------------------------------------------------------------------
This cog allows the bot to perform Google searches and sends the top results
in an embedded message format.
"""

from discord.ext import commands
from discord import Embed
from typing import Optional
from googlesearch import search
import random
import logging

# Set up logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Google(commands.Cog):
    """
    A Discord bot cog for performing Google searches and returning the top results.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initializes the Google cog.
        """
        self.client = client
        logger.info("Google cog initialized.")

    @commands.command(aliases=["google", "googlesearch"])
    async def goog(self, ctx: commands.Context, *, query: Optional[str] = None) -> None:
        """
        Perform a Google search and return the top results.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
            query (Optional[str]): The search query provided by the user.

        Returns:
            None: Sends an embedded message with the search results or an error message if no query is provided.
        """
        if query is None:
            embed0 = Embed(
                title="How to use this command?",
                description=f"Usage: `{ctx.prefix}goog <search>`",
                color=random.randint(0, 0xFFFFFF)
            )
            await ctx.send(embed=embed0)
            return

        # Perform the Google search
        results = ""
        n = 1
        try:
            # Perform the search with some basic settings
            search_results = search(query, tld="co.in", num=10, stop=10, pause=2)
            
            # Collect the search results
            for url in search_results:
                results += f"[{n}] {url}\n"
                n += 1
            
            # If no results found
            if not results:
                await ctx.send("No search results found.")
                return

            # Create an embed with the results
            embed = Embed(
                title=f"__Search results for:__ {query}",
                description=results,
                color=random.randint(0, 0xFFFFFF)
            )
            await ctx.send(embed=embed)

        except Exception as e:
            # Handle exceptions like network issues
            await ctx.send(f"An error occurred while performing the search: {e}")


async def setup(client: commands.Bot) -> None:
    """
    Function to add the Google cog to the bot.

    Args:
        client (commands.Bot): The bot instance to which the cog will be added.

    Returns:
        None
    """
    await client.add_cog(Google())
