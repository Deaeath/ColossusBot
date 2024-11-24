from discord.ext import commands
from discord import Embed
from typing import Optional
from googlesearch import search
import random


class Google(commands.Cog):
    """
    A Discord bot cog for performing Google searches and returning the top results.
    """

    @commands.command(aliases=["google", "googlesearch"])
    async def goog(self, ctx: commands.Context, *, query: Optional[str] = None) -> None:
        """
        Perform a Google search and return the top results.

        Args:
            ctx (commands.Context): The context in which the command was invoked.
            query (Optional[str]): The search query provided by the user.

        Returns:
            None: Sends an embedded message with the search results or an error message.
        """
        if query is None:
            embed0 = Embed(
                title="How to use this command?",
                description=f"{ctx.message.content} <search>",
                color=random.randint(0, 0xFFFFFF)
            )
            await ctx.send(embed=embed0)
            return
        else:
            results = ""
            n = 1
            for j in search(query, tld="co.in", num=10, stop=10, pause=2):
                results += f"[{n}] {j}\n"
                n += 1
            embed = Embed(
                title=f"__Search result of:__ {query}",
                description=f"{results}",
                color=random.randint(0, 0xFFFFFF)
            )
            await ctx.send(embed=embed)
            return


async def setup(client: commands.Bot) -> None:
    """
    A function to add the GoogCommand cog to the bot.

    Args:
        client (commands.Bot): The bot instance to which the cog will be added.

    Returns:
        None
    """
    await client.add_cog(Google())
