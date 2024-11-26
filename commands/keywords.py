# File: commands/keywords.py

"""
KeyWords Command: Display and Explain Key Words for Dynamic Message Customization
--------------------------------------------------------------------------------
A cog that explains and displays key words for dynamic message customization based on 
the member or server in a Discord bot.
"""

from discord.ext import commands
from discord import Embed, Reaction, User
from typing import Dict
import random
import logging

# Set up logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class KeyWordsCommand(commands.Cog):
    """
    A cog that explains and displays key words for dynamic message customization.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initializes the KeyWordsCommand cog.

        Args:
            client (commands.Bot): The bot instance.
        """
        self.client = client
        logging.info("KeyWordsCommand cog initialized.")

    @commands.command(aliases=["key-words"])
    @commands.has_any_role("owner", "head_staff")
    async def key_words(self, ctx: commands.Context) -> None:
        """
        Display an interactive embed to explain and list available key words.

        Args:
            ctx (commands.Context): The context in which the command was called.
        """
        # Embed 1: Introduction and Example
        embed = Embed(
            title="What are key words?",
            description="Key Words allow dynamic customization of messages based on the member or server.",
            color=random.randint(0, 0xFFFFFF),
        )
        embed.add_field(
            name="For Example",
            value=(
                "Let's say we have a message: ```Welcome {mention} to {guild}, enjoy your stay!```\n"
                f"When sent, it becomes:\n\nWelcome {ctx.author.mention} to {ctx.guild.name}, enjoy your stay!"
            ),
            inline=False,
        )
        embed.add_field(
            name="Explanation",
            value="Key words enclosed in `{}` are replaced with their respective values.",
            inline=False,
        )

        # Embed 2: Key Words List
        embed1 = Embed(
            title="Available Key Words",
            description="Below is a list of available key words for customization.",
            color=random.randint(0, 0xFFFFFF),
        )
        embed1.add_field(
            name="{mention}",
            value=(
                f"Mentions the member in a custom command or welcome message.\n"
                f"Example: {ctx.author.mention}"
            ),
            inline=False,
        )
        embed1.add_field(
            name="{member_name}",
            value=(
                f"Displays the member's name in a custom command or welcome message.\n"
                f"Example: {ctx.author.name}"
            ),
            inline=False,
        )
        embed1.add_field(
            name="{member_icon}",
            value=(
                f"Provides the member's profile picture link, suitable for embeds or icon fields.\n"
                f"Example: [Your PFP]({ctx.author.avatar.url})"
            ),
            inline=False,
        )
        embed1.set_author(name="{member_name}", icon_url=ctx.author.avatar.url)
        embed1.add_field(
            name="{guild}",
            value=(
                f"Displays the current server's name.\n"
                f"Example: {ctx.guild.name}"
            ),
            inline=False,
        )
        embed1.add_field(
            name="{guild_icon}",
            value=(
                f"Provides the server's icon link, suitable for embeds or icon fields.\n"
                f"Example: [{ctx.guild.name}]({ctx.guild.icon.url})"
            ),
            inline=False,
        )
        embed1.add_field(
            name="{user}",
            value=(
                f"Displays the member's name and tag.\n"
                f"Example: {ctx.author}"
            ),
            inline=False,
        )

        # Interactive Embeds
        embed_dict: Dict[int, Embed] = {1: embed, 2: embed1}
        current_page = 1
        total_pages = len(embed_dict)

        # Add footer to the first embed
        embed_dict[current_page].set_footer(text=f"Page {current_page}/{total_pages}")

        # Send initial embed and add reactions
        message = await ctx.send(embed=embed_dict[current_page])
        reactions = {"⬅️": -1, "➡️": 1, "⏹️": 0}  # Reaction navigation mapping
        for reaction in reactions.keys():
            await message.add_reaction(reaction)

        def check(reaction: Reaction, user: User) -> bool:
            return (
                user == ctx.author
                and str(reaction.emoji) in reactions
                and reaction.message.id == message.id
            )

        # Reaction loop for navigation
        while True:
            try:
                reaction, user = await self.client.wait_for("reaction_add", timeout=300, check=check)
                direction = reactions[str(reaction.emoji)]
                await message.remove_reaction(reaction.emoji, user)

                if direction == 0:  # Stop condition
                    await message.clear_reactions()
                    embed_cancel = Embed(description="Cancelled.", color=random.randint(0, 0xFFFFFF))
                    await ctx.send(embed=embed_cancel)
                    break

                new_page = current_page + direction
                if 1 <= new_page <= total_pages:
                    current_page = new_page
                    embed_dict[current_page].set_footer(text=f"Page {current_page}/{total_pages}")
                    await message.edit(embed=embed_dict[current_page])
            except TimeoutError:
                await message.clear_reactions()
                timeout_embed = Embed(description="Time out.", color=random.randint(0, 0xFFFFFF))
                await ctx.send(embed=timeout_embed)
                break


async def setup(client: commands.Bot) -> None:
    """
    Asynchronous setup function to add the cog to the bot.

    Args:
        client (commands.Bot): The bot instance.
    """
    await client.add_cog(KeyWordsCommand(client))
