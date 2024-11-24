import discord
from discord.ext import commands
import requests
import json
from typing import Optional


class Define(commands.Cog):
    """
    A cog to fetch definitions from Urban Dictionary.
    """

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.command(name="define")
    async def define(self, ctx: commands.Context, term: Optional[str] = None) -> None:
        """
        Fetches the definition of a term from Urban Dictionary.

        Args:
            ctx: The command invocation context.
            term: The term to define.
        """
        if not term:
            await ctx.send("Usage: `!define <term>`")
            return

        url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"
        headers = {
            'x-rapidapi-key': "YOUR_RAPIDAPI_KEY",
            'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com",
        }
        response = requests.get(url, headers=headers, params={"term": term})

        if response.status_code == 200:
            data = json.loads(response.text).get("list", [])
            if data:
                embed = discord.Embed(
                    title=f"Definition of {term}",
                    description=data[0]["definition"],
                    color=discord.Color.blue(),
                )
                embed.add_field(name="Example", value=data[0].get("example", "No example available."), inline=False)
                embed.add_field(name="Thumbs Up", value=data[0].get("thumbs_up", 0), inline=True)
                embed.add_field(name="Thumbs Down", value=data[0].get("thumbs_down", 0), inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"No definitions found for `{term}`.")
        else:
            await ctx.send(f"Error: Unable to fetch definition for `{term}`.")


async def setup(client: commands.Bot) -> None:
    """
    Loads the Define cog.

    Args:
        client: The bot instance.
    """
    await client.add_cog(Define(client))
