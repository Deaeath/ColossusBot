# File: commands/define.py

"""
Define Command: Fetch Definitions from Urban Dictionary
------------------------------------------------------
A cog that fetches the definition of a given term from the Urban Dictionary API and 
displays it in an embed with additional details like example, thumbs up, and thumbs down.
"""

import discord
from discord.ext import commands
import requests
import json
import os
from typing import Optional
import logging

# Set up logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Define(commands.Cog):
    """
    A cog to fetch definitions from Urban Dictionary.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initializes the Define cog.

        Args:
            client (commands.Bot): The bot instance.
        """
        self.client = client
        logger.info(f"[{self.__class__.__name__} Define cog initialized.")

    @commands.command(name="define",
                      help="Fetch the definition of a term from Urban Dictionary.",
                      usage="!define <term>",
                      aliases=["definition"])
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
        api_key = os.getenv("RAPIDAPI_KEY")  # Fetch the RapidAPI key from environment variables
        if not api_key:
            await ctx.send("API key is missing. Please set the RAPIDAPI_KEY environment variable.")
            return

        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com",
        }

        try:
            # Make the request to Urban Dictionary API
            response = requests.get(url, headers=headers, params={"term": term})

            # Check if the response status is OK (200)
            if response.status_code == 200:
                data = response.json().get("list", [])
                
                # Check if there are definitions in the response
                if data:
                    embed = discord.Embed(
                        title=f"Definition of {term}",
                        description=data[0]["definition"],
                        color=discord.Color.blue(),
                    )
                    embed.add_field(
                        name="Example", value=data[0].get("example", "No example available."), inline=False
                    )
                    embed.add_field(
                        name="Thumbs Up", value=data[0].get("thumbs_up", 0), inline=True
                    )
                    embed.add_field(
                        name="Thumbs Down", value=data[0].get("thumbs_down", 0), inline=True
                    )
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"No definitions found for `{term}`.")
            else:
                await ctx.send(f"Error: Unable to fetch definition for `{term}`. Status Code: {response.status_code}")
        except requests.RequestException as e:
            # Catch any network-related errors
            await ctx.send(f"Network error occurred while fetching the definition: {e}")
        except Exception as e:
            # Catch any other unexpected errors
            await ctx.send(f"An unexpected error occurred: {e}")


async def setup(client: commands.Bot) -> None:
    """
    Loads the Define cog.

    Args:
        client: The bot instance.
    """
    logger.info("[Define] Setting up Define cog...")
    await client.add_cog(Define(client))
    logger.info("[Define] Define cog setup complete.")
