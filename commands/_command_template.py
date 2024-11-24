"""
Template Command: Example Command for ColossusBot
-------------------------------------------------
Use this template to create and add new commands to the bot.
"""

from discord.ext import commands
from discord import Embed
import logging

# Initialize logging for debugging purposes
logger = logging.getLogger("ColossusBot")

class CommandTemplate(commands.Cog):
    """
    A template cog for creating commands in ColossusBot.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initializes the CommandTemplate cog.

        :param client: The Discord bot client instance.
        """
        self.client = client
        logger.info("CommandTemplate initialized successfully.")

    @commands.command(name="example", help="An example command to demonstrate functionality.")
    async def example_command(self, ctx: commands.Context, *, input_text: str = "Default Response") -> None:
        """
        Responds with a user-provided message or a default response.

        :param ctx: The command context.
        :param input_text: The input text provided by the user (optional).
        """
        logger.info(f"Executing 'example_command' with input: {input_text}")

        # Create an embed to display the response
        embed = Embed(
            title="Example Command",
            description=f"You said: {input_text}",
            color=0x00FF00
        )
        await ctx.send(embed=embed)

    @commands.command(name="another_example", help="Another example command to show usage with arguments.")
    async def another_example_command(self, ctx: commands.Context, number: int) -> None:
        """
        Multiplies a number by 2 and returns the result.

        :param ctx: The command context.
        :param number: A number provided by the user.
        """
        logger.info(f"Executing 'another_example_command' with number: {number}")

        result = number * 2
        await ctx.send(f"Double of {number} is {result}!")


async def setup(client: commands.Bot) -> None:
    """
    Registers the CommandTemplate cog with the bot.

    :param client: The Discord bot client instance.
    """
    logger.info("Setting up CommandTemplate cog...")
    await client.add_cog(CommandTemplate(client))
    logger.info("CommandTemplate cog setup complete.")
