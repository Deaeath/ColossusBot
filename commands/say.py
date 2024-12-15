# File: commands/say.py

"""
Say Command: Send a Message to a Specified Channel
--------------------------------------------------
A cog for sending messages to a specific channel by providing its ID.
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
import logging

# Set up logger
logger = logging.getLogger(__name__)

class SayCommand(commands.Cog):
    """
    Cog for the `say` command, which allows sending a message to a specified channel by its ID.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initializes the SayCommand cog.

        Args:
            client (commands.Bot): The bot instance.
        """
        self.client = client
        logger.info("[SayCommand] SayCommand cog initialized.")

    @commands.command(
        help="Sends a message to a specified channel.",
        usage="say <channel_id> [message]",
        extras={"permissions": ["administrator"]},
    )
    @commands.has_permissions(administrator=True)
    async def say(self, ctx: Context, channel_id: int, *, message: str) -> None:
        """
        Send a message to a specified channel.

        Args:
            ctx (Context): The context of the command invocation.
            channel_id (int): The ID of the target channel.
            message (str): The message to send.
        """
        logger.debug(f"[{self.__class__.__name__}] Command `say` invoked by {ctx.author} with channel_id={channel_id} and message='{message}'.")

        channel = self.client.get_channel(channel_id)
        if channel:
            try:
                await channel.send(message)
                logger.info(f"[{self.__class__.__name__}] Sent message to channel ID {channel_id} by user {ctx.author}.")
                await ctx.send(f"Message successfully sent to {channel.mention}.")
            except discord.Forbidden:
                logger.error(f"[{self.__class__.__name__}] Permission denied when trying to send message to channel ID {channel_id}.")
                await ctx.send("I do not have permission to send messages in that channel.")
            except discord.HTTPException as e:
                logger.error(f"[{self.__class__.__name__}] HTTPException occurred: {e}")
                await ctx.send("Failed to send the message due to an internal error.")
        else:
            logger.warning(f"[{self.__class__.__name__}] Channel with ID {channel_id} not found.")
            await ctx.send(f"Channel with ID {channel_id} not found.")


async def setup(client: commands.Bot) -> None:
    """
    Asynchronous setup function to load the SayCommand cog.

    Args:
        client (commands.Bot): The bot instance.
    """
    logger.info("[SayCommand] Adding SayCommand cog to bot.")
    await client.add_cog(SayCommand(client))
    logger.info("[SayCommand] SayCommand cog added to bot.")
