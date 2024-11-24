import discord
from discord.ext import commands
from discord.ext.commands import Context


class SayCommand(commands.Cog):
    """Cog for the `say` command."""

    def __init__(self, client: commands.Bot) -> None:
        """Initialize the SayCommand cog.

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
        """Send a message to a specific channel.

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
    """Setup function to load the SayCommand cog.

    Args:
        client (commands.Bot): The bot instance.
    """
    await client.add_cog(SayCommand(client))
