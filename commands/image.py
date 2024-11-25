# File: commands/image.py

"""
ImgCommand Cog: Perform Google Image Search and Display Paginated Results
------------------------------------------------------------------------
This cog allows the bot to perform Google image searches and send paginated
results through embeds with navigation.
"""

from discord.ext import commands
from discord import Embed, Message, Reaction, User
from typing import Optional, Dict
import asyncio
import aiohttp
import os
import random



class ImgCommand(commands.Cog):
    """
    A Discord bot cog for performing Google image searches and returning paginated results.
    """

    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    CX_ID = os.getenv('GOOGLE_CX_ID')

    async def get_json(self, url: str) -> dict:
        """
        Fetch JSON data from the given URL.

        Args:
            url (str): The API endpoint to fetch data from.

        Returns:
            dict: The JSON response.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()

    @commands.command(aliases=["image"])
    async def img(self, ctx: commands.Context, *, query: Optional[str] = None) -> None:
        """
        Perform a Google image search and display paginated results.

        Args:
            ctx (commands.Context): The context of the command invocation.
            query (Optional[str]): The search query provided by the user.

        Returns:
            None: Sends embedded paginated results or an error message.
        """
        if query is None:
            embed0 = Embed(
                title="How to use this command?",
                description=f"{ctx.message.content} <search>",
                color=random.randint(0, 0xFFFFFF)
            )
            await ctx.send(embed=embed0)
            return

        results_list = []
        start_index = 0
        safety_level = "medium"  # Adjust this value as per your NSFW filter preference

        # Fetch search results in batches of 10
        while start_index <= 100:
            api_url = (
                f"https://www.googleapis.com/customsearch/v1"
                f"?key={self.GOOGLE_API_KEY}&cx={self.CX_ID}&searchType=image&safe={safety_level}&q={query}&start={start_index}"
            )
            response = await self.get_json(api_url)
            try:
                for item in response.get("items", []):
                    results_list.append(item)
            except Exception as e:
                print(f"Error while fetching search results: {e}")
                break
            start_index += 10

        if not results_list:
            await ctx.send("No results found for your search.")
            return

        # Create embeds for results
        embed_dict: Dict[int, Embed] = {}
        for idx, result in enumerate(results_list, start=1):
            embed = Embed(
                title=result.get("title", "No Title"),
                description=f"[{result.get('displayLink')}]({result.get('link')})",
                color=random.randint(0, 0xFFFFFF)
            )
            embed.set_image(url=result.get("link"))
            embed_dict[idx] = embed

        # Send the first embed and add reactions for navigation
        current_page = 1
        embed_dict[current_page].set_footer(text=f"Page {current_page}/{len(embed_dict)}")
        message = await ctx.send(embed=embed_dict[current_page])

        if len(embed_dict) > 1:
            await message.add_reaction("⬅️")
            await message.add_reaction("➡️")
            await message.add_reaction("⏹️")

            def reaction_check(reaction: Reaction, user: User) -> bool:
                return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️", "⏹️"]

            flag = True
            while flag:
                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=300, check=reaction_check)
                except asyncio.TimeoutError:
                    await message.clear_reactions()
                    break

                if str(reaction.emoji) == "➡️":
                    if current_page < len(embed_dict):
                        current_page += 1
                        embed_dict[current_page].set_footer(text=f"Page {current_page}/{len(embed_dict)}")
                        await message.edit(embed=embed_dict[current_page])
                elif str(reaction.emoji) == "⬅️":
                    if current_page > 1:
                        current_page -= 1
                        embed_dict[current_page].set_footer(text=f"Page {current_page}/{len(embed_dict)}")
                        await message.edit(embed=embed_dict[current_page])
                elif str(reaction.emoji) == "⏹️":
                    await message.clear_reactions()
                    flag = False

                await message.remove_reaction(reaction.emoji, ctx.author)


async def setup(client: commands.Bot) -> None:
    """
    Add the ImgCommand cog to the bot.

    Args:
        client (commands.Bot): The bot instance to which the cog will be added.

    Returns:
        None
    """
    await client.add_cog(ImgCommand())
