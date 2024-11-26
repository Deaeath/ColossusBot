# File: commands/wiki.py

"""
WikiCommand: Fetches Wikipedia Page Information
------------------------------------------------
Handles the searching of terms on Wikipedia, managing disambiguation errors, 
suggesting alternatives, and providing helpful feedback when no results are found.
"""

from discord.ext import commands
from discord import Embed
import wikipedia
from typing import Optional
import random
import logging

# Set up logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class WikiCommand(commands.Cog):
    """
    A cog to fetch Wikipedia page information and suggest alternatives for invalid terms.
    
    This cog contains a command that allows users to search for a term on Wikipedia and
    receive the page URL. If the term is invalid, the bot will suggest alternative terms,
    handle disambiguation errors, and provide helpful feedback for users.

    Attributes:
        client (commands.Bot): The instance of the Discord bot client.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initializes the WikiCommand cog.

        Args:
            client (commands.Bot): The instance of the Discord bot client.
        """
        self.client = client
        logging.info("WikiCommand cog initialized.")

    @commands.command(aliases=["wikipedia"])
    async def wiki(self, ctx: commands.Context, *, term: Optional[str] = None) -> None:
        """
        Search for a term on Wikipedia and return the page URL. Suggest alternatives if the term is invalid.

        This command performs a Wikipedia search for the provided term and sends the URL of the result.
        If the search term is ambiguous (disambiguation error) or not found (page error), it suggests
        alternative terms or provides an error message.

        Args:
            ctx (commands.Context): The context of the command.
            term (Optional[str]): The term to search for on Wikipedia. Defaults to None.

        Returns:
            None
        """
        if term is None:
            embed = Embed(
                title="How to use this command?",
                description=f"Usage: `{ctx.prefix}wiki <term>`",
                color=random.randint(0, 0xFFFFFF),
            )
            await ctx.send(embed=embed)
            return

        try:
            # Fetch the Wikipedia page for the term
            result = wikipedia.page(term)
            await ctx.send(result.url)
        except wikipedia.DisambiguationError as e:
            # Handle disambiguation errors by listing alternative terms
            alternative_terms = e.options
            alternatives = "\n".join(f"`{term}`" for term in alternative_terms)
            embed = Embed(
                title=f"No exact match found for: `{term}`",
                description=f"Did you mean one of these?\n{alternatives}",
                color=random.randint(0, 0xFFFFFF),
            )
            await ctx.send(embed=embed)
        except wikipedia.PageError:
            # Handle page errors (e.g., term not found)
            embed = Embed(
                title="Page Not Found",
                description=f"Sorry, no results were found for the term `{term}`.",
                color=random.randint(0, 0xFFFFFF),
            )
            await ctx.send(embed=embed)
        except wikipedia.RedirectError:
            # Handle redirect errors if Wikipedia redirects the term
            embed = Embed(
                title="Redirect Detected",
                description=f"The term `{term}` redirected to another page. Try the following link:\n{wikipedia.page(term).url}",
                color=random.randint(0, 0xFFFFFF),
            )
            await ctx.send(embed=embed)
        except Exception as e:
            # Handle other unexpected errors
            embed = Embed(
                title="An Error Occurred",
                description=f"An unexpected error occurred: `{str(e)}`",
                color=random.randint(0, 0xFFFFFF),
            )
            await ctx.send(embed=embed)

async def setup(client: commands.Bot) -> None:
    """
    Asynchronously loads the WikiCommand cog.

    This function is called to add the WikiCommand cog to the bot.

    Args:
        client (commands.Bot): The instance of the bot.

    Returns:
        None
    """
    await client.add_cog(WikiCommand(client))
