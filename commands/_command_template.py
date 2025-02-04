# File: commands/command_template.py

"""
CommandTemplate Cog: A Template for Command Creation in ColossusBot
------------------------------------------------------------------
This cog serves as a template for creating and managing commands in 
the ColossusBot, with logging capabilities for debugging and error handling.
"""

from discord.ext import commands
from discord import Embed
import logging

# Initialize logging for debugging purposes
logger = logging.getLogger("ColossusBot")
logger.setLevel(logging.INFO)  # Set logging level to INFO to capture logs

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
        self.db_path = "path/to/database.db"  # Path to the database file (optional, commands that rely on the database should be cogs instead of commands)
        logger.info("[CommandTemplate] CommandTemplate cog initialized.")

    @commands.command(name="example", help="An example command to demonstrate functionality.", usage="!example [input_text]")
    async def example_command(self, ctx: commands.Context, *, input_text: str = "Default Response") -> None:
        """
        Responds with a user-provided message or a default response.

        :param ctx: The command context.
        :param input_text: The input text provided by the user (optional).
        """
        logger.info(f"Executing 'example_command' with input: {input_text}")

        try:
            # Create an embed to display the response
            embed = Embed(
                title="Example Command",
                description=f"You said: {input_text}",
                color=0x00FF00  # Green color for success
            )
            await ctx.send(embed=embed)
        except Exception as e:
            # Log and send an error message if something goes wrong
            logger.error(f"Error executing 'example_command': {str(e)}")
            await ctx.send("Oops! Something went wrong while processing your request.")

    @commands.command(name="another_example", help="Another example command to show usage with arguments.", usage="!another_example [number]")
    async def another_example_command(self, ctx: commands.Context, number: int) -> None:
        """
        Multiplies a number by 2 and returns the result.

        :param ctx: The command context.
        :param number: A number provided by the user.
        """
        logger.info(f"Executing 'another_example_command' with number: {number}")

        try:
            result = number * 2
            await ctx.send(f"Double of {number} is {result}!")
        except Exception as e:
            # Log and send an error message if something goes wrong
            logger.error(f"Error executing 'another_example_command': {str(e)}")
            await ctx.send("Oops! Something went wrong while processing your request.")

    @example_command.error
    async def example_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """
        Catches errors specific to 'example_command' and handles them.

        :param ctx: The command context.
        :param error: The error that was raised.
        """
        logger.error(f"Error in 'example_command': {str(error)}")
        await ctx.send("There was an error processing your example command.")

    @another_example_command.error
    async def another_example_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """
        Catches errors specific to 'another_example_command' and handles them.

        :param ctx: The command context.
        :param error: The error that was raised.
        """
        logger.error(f"Error in 'another_example_command': {str(error)}")
        await ctx.send("There was an error processing your another example command.")


async def setup(client: commands.Bot) -> None:
    """
    Registers the CommandTemplate cog with the bot.

    :param client: The Discord bot client instance.
    """
    logger.info(f"[CommandTemplate] Setting up CommandTemplate cog...")
    await client.add_cog(CommandTemplate(client))
    logger.info(f"[CommandTemplate] CommandTemplate cog successfully set up.")
