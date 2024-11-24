import discord
from discord.ext import commands
from typing import Optional


class RestrictRole(commands.Cog):
    """
    A cog to restrict a specific role to only view a designated channel.
    """

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.command(name="restrict_role")
    @commands.has_permissions(administrator=True)
    async def restrict_role(
        self, ctx: commands.Context, role: Optional[discord.Role] = None, allowed_channel: Optional[discord.TextChannel] = None
    ) -> None:
        """
        Restricts a role to only view one specific channel.

        Args:
            ctx: The command invocation context.
            role: The role to restrict (mention or ID).
            allowed_channel: The channel the role will be allowed to view (mention or ID).
        """
        if role is None or allowed_channel is None:
            await ctx.send("Usage: `!restrict_role <role> <channel>`")
            return

        try:
            confirm_message = await ctx.send(
                f"Are you sure you want to restrict {role.mention} to only view {allowed_channel.mention}? React ✅ to confirm."
            )
            await confirm_message.add_reaction("✅")
            await confirm_message.add_reaction("❌")

            def check(reaction: discord.Reaction, user: discord.User) -> bool:
                return user == ctx.author and str(reaction.emoji) in ["✅", "❌"]

            reaction, _ = await self.client.wait_for("reaction_add", timeout=60.0, check=check)

            if str(reaction.emoji) == "❌":
                await ctx.send("Operation canceled.")
                return

            total_channels = len(ctx.guild.channels)
            for idx, channel in enumerate(ctx.guild.channels, 1):
                if isinstance(channel, discord.TextChannel):
                    permissions = discord.PermissionOverwrite(read_messages=(channel == allowed_channel))
                    await channel.set_permissions(role, overwrite=permissions)

                if idx % (total_channels // 10) == 0:  # Periodic updates
                    await ctx.send(f"Progress: {idx}/{total_channels} channels updated.")

            await ctx.send(f"Role {role.mention} has been restricted to only view {allowed_channel.mention}.")

        except Exception as e:
            await ctx.send(f"Error: {e}")


async def setup(client: commands.Bot) -> None:
    """
    Loads the RestrictRole cog.

    Args:
        client: The bot instance.
    """
    await client.add_cog(RestrictRole(client))
