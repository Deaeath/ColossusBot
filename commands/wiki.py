from discord.ext import commands
from discord import Embed
import wikipedia
from typing import Optional
import random


class WikiCommand(commands.Cog):
    """
    A cog to fetch Wikipedia page information and suggest alternatives for invalid terms.
    """

    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command(aliases=["wikipedia"])
    async def wiki(self, ctx: commands.Context, *, term: Optional[str] = None):
        """
        Search for a term on Wikipedia and return the page URL. Suggest alternatives if the term is invalid.

        Args:
            ctx (commands.Context): The context of the command.
            term (Optional[str]): The term to search for on Wikipedia.
        """
        if term is None:
            embed = Embed(
                title="How to use this command?",
                description=f"`{ctx.message.content} <term>`",
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
                title=f"No exact match found for: {term}",
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
        except Exception as e:
            # Handle other unexpected errors
            embed = Embed(
                title="An Error Occurred",
                description=f"An unexpected error occurred: `{str(e)}`",
                color=random.randint(0, 0xFFFFFF),
            )
            await ctx.send(embed=embed)


async def setup(client: commands.Bot):
    """
    Asynchronous setup function to add the cog to the bot.

    Args:
        client (commands.Bot): The bot instance.
    """
    await client.add_cog(WikiCommand(client))
