"""
ChannelAccessManager: Manage Channel Access with DatabaseHandler
----------------------------------------------------------------
A cog for managing channel and category access using the shared DatabaseHandler.
"""

import discord
from discord.ext import commands
import logging
import math
import asyncio

logger = logging.getLogger("ChannelAccessManager")


class ChannelAccessManager(commands.Cog):
    """
    A cog for managing access to Discord channels and categories.
    """

    def __init__(self, client: commands.Bot, db_handler):
        """
        Initializes the ChannelAccessManager cog.

        :param client: The Discord bot client instance.
        :param db_handler: The shared DatabaseHandler instance.
        """
        self.client = client
        self.db_handler = db_handler
        logger.info("ChannelAccessManager initialized.")

    @commands.command(name="channels")
    async def channels(self, ctx: commands.Context):
        """
        Entry point command for channel access management.
        """
        if not ctx.guild:
            await ctx.send("This command can only be used in a server.")
            return
        await self.show_home_page(ctx)

    async def toggle_channel_access(self, ctx: commands.Context, member: discord.Member, channel: discord.TextChannel):
        """
        Toggles a member's access to a channel and logs the change via DatabaseHandler.

        :param ctx: The command context.
        :param member: The member whose access is being toggled.
        :param channel: The channel being toggled.
        """
        overwrite = channel.overwrites_for(member)
        current_access = overwrite.read_messages
        new_access = not current_access
        overwrite.read_messages = new_access

        # Log the permission change in the database
        await self.db_handler.execute(
            """
            INSERT INTO channel_perms_log (user_id, channel_id, previous_state, new_state)
            VALUES (?, ?, ?, ?)
            """,
            (member.id, channel.id, current_access, new_access)
        )

        action = "Granted" if new_access else "Removed"
        await channel.set_permissions(member, overwrite=overwrite)
        await ctx.send(f"✅ {action} access for {member.mention} to {channel.mention}.")

    @commands.command(name="view_logs")
    async def view_logs(self, ctx: commands.Context):
        """
        Displays channel permission change logs using DatabaseHandler.
        """
        logs = await self.db_handler.fetchall(
            "SELECT user_id, channel_id, previous_state, new_state, timestamp FROM channel_perms_log"
        )
        if not logs:
            await ctx.send("No permission change logs found.")
            return

        embed = discord.Embed(
            title="📋 Permission Change Logs",
            color=discord.Color.blue()
        )
        for log in logs[:10]:  # Display the first 10 logs
            user = self.client.get_user(log[0])
            user_display = user.mention if user else f"User ID: {log[0]}"
            channel = ctx.guild.get_channel(log[1])
            channel_display = channel.mention if channel else f"Channel ID: {log[1]}"
            embed.add_field(
                name=f"{user_display} in {channel_display}",
                value=(
                    f"Previous: {'✅' if log[2] else '❌'}\n"
                    f"New: {'✅' if log[3] else '❌'}\n"
                    f"Time: {log[4]}"
                ),
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="reset_permissions")
    async def reset_permissions(self, ctx: commands.Context):
        """
        Resets all custom permissions via DatabaseHandler.
        """
        records = await self.db_handler.fetchall(
            "SELECT user_id, channel_id FROM channel_perms_log"
        )
        if not records:
            await ctx.send("No custom permissions to reset.")
            return

        for user_id, channel_id in records:
            member = ctx.guild.get_member(user_id)
            channel = ctx.guild.get_channel(channel_id)
            if member and channel:
                await channel.set_permissions(member, overwrite=None)

        # Clear the log table
        await self.db_handler.execute("DELETE FROM channel_perms_log")
        await ctx.send("✅ Custom permissions reset and cleared from the database.")

    async def show_home_page(self, ctx: commands.Context):
        """
        Displays the home page with options for managing categories and channels.

        :param ctx: The command context.
        """
        embed = discord.Embed(
            title="🏠 Channel Access Manager",
            description=(
                "Manage your access to categories and channels.\n\n"
                "Navigate using the reactions below:\n"
                "➡️ **Categories** - Manage category access\n"
                "🔍 **Channels** - Manage individual channel access\n"
                "❌ Exit"
            ),
            color=discord.Color.purple()
        )

        message = await ctx.send(embed=embed)
        reactions = ["➡️", "🔍", "❌"]

        for reaction in reactions:
            await message.add_reaction(reaction)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in reactions

        try:
            while True:
                reaction, _ = await self.client.wait_for("reaction_add", timeout=600.0, check=check)
                if str(reaction.emoji) == "➡️":
                    await self.show_category_page(ctx, message)
                elif str(reaction.emoji) == "🔍":
                    await self.select_category_for_channels(ctx, message)
                elif str(reaction.emoji) == "❌":
                    await message.delete()
                    break
        except asyncio.TimeoutError:
            await message.clear_reactions()


async def setup(client: commands.Bot):
    """
    Sets up the cog.
    """
    logger.info("Setting up ChannelAccessManager...")
    db_handler = client.db_handler  # Shared DatabaseHandler instance
    await client.add_cog(ChannelAccessManager(client, db_handler))
    logger.info("ChannelAccessManager setup complete.")
