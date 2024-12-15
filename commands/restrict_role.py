# File: commands/restrict_role.py

"""
Restrict Role: Restrict a Role to Only View a Designated Channel
-----------------------------------------------------------------
A cog for restricting a role to view only one specific channel in the server.
"""

import discord
from discord.ext import commands
from typing import Optional
import logging

# Set up logger
logger = logging.getLogger(__name__)

class RestrictRole(commands.Cog):
    """
    A cog to restrict a specific role to only view a designated channel.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initializes the RestrictRole cog.

        Args:
            client (commands.Bot): The bot instance.
        """
        self.client = client
        logging.info("[RestrictRole] RestrictRole cog initialized.")

    @commands.command(name="restrict_role",
                      help="Restrict a role to only view one specific channel.",
                      usage="!restrict_role <role> <channel>",
                      aliases=["restrictrole"],
                      extras={"permissions": ["administrator"]})
    @commands.has_permissions(administrator=True)
    async def restrict_role(
        self, ctx: commands.Context, role: Optional[discord.Role] = None, allowed_channel: Optional[discord.TextChannel] = None
    ) -> None:
        """
        Restricts a role to only view one specific channel.

        Args:
            ctx (commands.Context): The command invocation context.
            role (Optional[discord.Role]): The role to restrict (mention or ID).
            allowed_channel (Optional[discord.TextChannel]): The channel the role will be allowed to view (mention or ID).
        """
        if role is None or allowed_channel is None:
            await ctx.send("Usage: `!restrict_role <role> <channel>`")
            return

        try:
            # Confirm the restriction action with the user
            confirm_message = await ctx.send(
                f"Are you sure you want to restrict {role.mention} to only view {allowed_channel.mention}? React ✅ to confirm."
            )
            await confirm_message.add_reaction("✅")
            await confirm_message.add_reaction("❌")

            def check(reaction: discord.Reaction, user: discord.User) -> bool:
                return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]

            # Wait for the user's reaction
            reaction, _ = await self.client.wait_for("reaction_add", timeout=60.0, check=check)

            # If canceled
            if str(reaction.emoji) == "❌":
                await ctx.send("Operation canceled.")
                return

            # Update permissions for all text channels
            total_channels = len(ctx.guild.channels)
            for idx, channel in enumerate(ctx.guild.channels, 1):
                if isinstance(channel, discord.TextChannel):
                    permissions = discord.PermissionOverwrite(read_messages=(channel == allowed_channel))
                    await channel.set_permissions(role, overwrite=permissions)

                # Periodic updates
                if idx % (total_channels // 10) == 0:
                    await ctx.send(f"Progress: {idx}/{total_channels} channels updated.")

            await ctx.send(f"Role {role.mention} has been restricted to only view {allowed_channel.mention}.")

        except Exception as e:
            await ctx.send(f"Error: {e}")


async def setup(client: commands.Bot) -> None:
    """
    Loads the RestrictRole cog.

    Args:
        client (commands.Bot): The bot instance.
    """
    logger.info("[RestrictRole] Setting up RestrictRole cog...")
    await client.add_cog(RestrictRole(client))
    logger.info("[RestrictRole] RestrictRole cog successfully set up.")