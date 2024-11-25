# File: commands/say.py

"""
Say Command: Send a Message to a Specified Channel
--------------------------------------------------
A cog for sending messages to a specific channel by providing its ID.
"""

import discord
from discord.ext import commands
from discord.ext.commands import Context
from typing import Optional


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

    @commands.command(
        help="Sends a message to a specified channel.",
        usage="!say <channel_id> [message]"
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
        channel = self.client.get_channel(channel_id)
        if channel:
            await channel.send(message)
        else:
            await ctx.send(f"Channel with ID {channel_id} not found.")


async def setup(client: commands.Bot) -> None:
    """
    Asynchronous setup function to load the SayCommand cog.

    Args:
        client (commands.Bot): The bot instance.
    """
    await client.add_cog(SayCommand(client))
