# File: commands/purge_user.py

"""
Purge Messages: Purge Messages Sent by a Specific User
------------------------------------------------------
A cog for purging messages sent by a specific user across all channels in a guild.
"""

from discord.ext import commands
from discord import Guild, Embed, Member, TextChannel
from typing import Callable, Dict, Optional
import discord
import logging

# Set up logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PurgeMessages(commands.Cog):
    """
    A cog for purging messages sent by a specific user across all text channels in a guild.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initializes the PurgeMessages cog.

        Args:
            client (commands.Bot): The bot instance.
        """
        self.client = client
        logging.info("PurgeMessages cog initialized.")

    async def purge_messages_from_user(
        self,
        guild: Guild,
        user_id: int,
        limit: int = 100,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> Dict[str, str]:
        """
        Purge messages sent by a specific user across all text channels in a guild.

        Args:
            guild (Guild): The Discord guild (server) where the purge will take place.
            user_id (int): The ID of the user whose messages will be purged.
            limit (int): The maximum number of messages to search through per channel.
            progress_callback (Optional[Callable[[int, int], None]]): A callback to report progress.

        Returns:
            Dict[str, str]: A summary of the purge results for each channel.
        """
        user = await self.client.fetch_user(user_id)
        summary = {}
        channels_processed = 0

        for channel in guild.text_channels:
            channels_processed += 1
            # Update progress bar via callback if provided
            if progress_callback:
                await progress_callback(len(guild.text_channels), channels_processed)

            # Ensure the bot has permissions to read message history and manage messages
            if not channel.permissions_for(guild.me).read_message_history or not channel.permissions_for(
                guild.me
            ).manage_messages:
                summary[channel.name] = "Skipped: Lack permissions"
                continue

            def is_user(m):
                return m.author.id == user_id

            try:
                deleted = await channel.purge(limit=limit, check=is_user)
                if deleted:
                    summary[channel.name] = f"Deleted {len(deleted)} messages"
            except discord.Forbidden:
                summary[channel.name] = "Forbidden: Lack permissions"
            except discord.HTTPException as e:
                summary[channel.name] = f"HTTPException: {e}"

        return summary

    @commands.command(name="purge_user",
                      help="Purge messages from a specific user across all text channels.",
                      usage="!purge_user <user_id>",
                      extras={"permissions": ["Manage Messages"]})
    @commands.has_permissions(manage_messages=True)
    async def purge_user(self, ctx: commands.Context, user_id: int) -> None:
        """
        A command to initiate the purge of messages from a specific user across all channels.

        Args:
            ctx (commands.Context): The context of the command.
            user_id (int): The ID of the user whose messages will be purged.
        """
        embed = Embed(title="Purge Operation Started", description="Please wait...", color=discord.Color.blue())
        progress_message = await ctx.send(embed=embed)

        async def update_progress(total_channels: int, processed_channels: int) -> None:
            """
            Updates the progress message during the purge operation.

            Args:
                total_channels (int): The total number of text channels in the guild.
                processed_channels (int): The number of channels that have been processed so far.
            """
            progress_embed = Embed(title="Purging Progress", color=discord.Color.blue())
            progress_embed.add_field(name="User ID", value=str(user_id), inline=False)
            progress_embed.add_field(
                name="Progress",
                value=f"{processed_channels}/{total_channels} channels processed",
                inline=False,
            )
            await progress_message.edit(embed=progress_embed)

        # Purge messages and update progress
        summary = await self.purge_messages_from_user(ctx.guild, user_id, progress_callback=update_progress)

        # Create a summary embed with results
        final_embed = Embed(title="Purge Summary", color=discord.Color.green())
        final_embed.add_field(name="User ID", value=str(user_id), inline=False)
        for channel, result in summary.items():
            final_embed.add_field(name=f"Channel: {channel}", value=f"{result}", inline=False)
        await progress_message.edit(embed=final_embed)

    @purge_user.error
    async def purge_user_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        """
        Error handler for the purge_user command.

        Args:
            ctx (commands.Context): The context of the command.
            error (commands.CommandError): The error raised during command execution.
        """
        if isinstance(error, commands.MissingRequiredArgument):
            embed = Embed(title="Missing Argument", color=discord.Color.red())
            embed.add_field(name="Command Usage", value="`!purge_user <user_id>`", inline=False)
            embed.add_field(
                name="Description",
                value="This command purges messages from a specific user across all text channels.",
                inline=False,
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("You lack the necessary roles to execute this command.")
        elif isinstance(error, discord.Forbidden):
            await ctx.send("I don't have the necessary permissions to perform this action in one or more channels.")
        elif isinstance(error, discord.HTTPException):
            await ctx.send("A network error occurred while trying to purge messages. Please try again later.")
        elif isinstance(error, discord.NotFound):
            await ctx.send("The specified User ID does not correspond to an existing user. Please check the ID.")
        else:
            await ctx.send(f"An unexpected error occurred: {error}")


async def setup(client: commands.Bot) -> None:
    """
    Asynchronous setup function to add the cog to the bot.

    Args:
        client (commands.Bot): The bot instance.
    """
    await client.add_cog(PurgeMessages(client))
    logging.info("PurgeMessages cog loaded")
