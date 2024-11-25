# File: colossusCogs/admin_commands.py

"""
AdminCommands Cog: Handles Administrative Actions
-------------------------------------------------
This cog is responsible for managing core administrative actions such as:
- Muting users
- Kicking users
- Banning users
- Warning users and logging those warnings
It interacts with the DatabaseHandler to store and retrieve warning data.
"""

from discord.ext import commands
from discord import Embed, Member
import discord
import random
from typing import Optional
from handlers.database_handler import DatabaseHandler


class AdminCommands(commands.Cog):
    """
    Handles the core logic for administrative actions like muting, kicking, banning, and warnings.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler) -> None:
        """
        Initializes the AdminCommands cog.

        :param client: The Discord bot client instance.
        :param db_handler: The DatabaseHandler instance for handling database operations.
        """
        self.client = client
        self.db_handler = db_handler

    async def cog_load(self) -> None:
        """Handles logic to execute when the cog is loaded."""
        print("AdminCommands.cog_load: AdminCommands is starting...")
        await self.db_handler.connect()
        print("AdminCommands.cog_load: AdminCommands is ready.")

    async def send_embed(
        self,
        ctx: commands.Context,
        moderator: Optional[Member] = None,
        member: Optional[Member] = None,
        reason: Optional[str] = None,
        action_type: Optional[str] = None,
    ) -> None:
        """
        Sends an embed summarizing an administrative action.

        :param ctx: The command context.
        :param moderator: The moderator who performed the action.
        :param member: The member affected by the action.
        :param reason: The reason for the action.
        :param action_type: The type of action (e.g., Muted, Kicked).
        """
        embed = Embed(color=random.randint(0, 0xFFFFFF))
        if moderator and member and action_type:
            embed.set_author(
                name=f"{moderator.display_name} (ID {moderator.id})",
                icon_url=moderator.avatar.url
            )
            embed.description = f"⚠️ {action_type} {member.display_name} (ID {member.id})"
            embed.add_field(
                name="📄 Reason:",
                value=reason or "No description provided.",
                inline=False
            )
            embed.set_thumbnail(url=member.avatar.url)
        else:
            embed.description = reason or "No description provided."
        await ctx.send(embed=embed)

    async def mute_user_logic(self, ctx: commands.Context, member: Member, reason: Optional[str]) -> None:
        """
        Implements the logic for muting a user.

        :param ctx: The command context.
        :param member: The member to mute.
        :param reason: The reason for the mute.
        """
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted") or await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, speak=False, send_messages=False)
        await member.add_roles(mute_role, reason=reason)
        await self.send_embed(ctx, ctx.author, member, reason, "Muted")

    async def kick_user_logic(self, ctx: commands.Context, member: Member, reason: Optional[str]) -> None:
        """
        Implements the logic for kicking a user.

        :param ctx: The command context.
        :param member: The member to kick.
        :param reason: The reason for the kick.
        """
        await member.kick(reason=reason)
        await self.send_embed(ctx, ctx.author, member, reason, "Kicked")

    async def user_warning_logic(self, ctx: commands.Context, member: Member, reason: Optional[str]) -> None:
        """
        Implements the logic for warning a user.

        :param ctx: The command context.
        :param member: The member to warn.
        :param reason: The reason for the warning.
        """
        # Log the warning in the database
        await self.db_handler.log_warning(member, reason)
        # Send embed summarizing the warning action
        await self.send_embed(ctx, ctx.author, member, reason, "Warned")

    async def fetch_warnings(self, member: Member) -> list:
        """
        Fetches all warnings for a specific member.

        :param member: The member whose warnings to fetch.
        :return: A list of tuples containing the warning reason and timestamp.
        """
        return await self.db_handler.fetch_warnings(member)


async def setup(client: commands.Bot) -> None:
    """
    Registers the AdminCommands cog with the bot.

    :param client: The Discord bot client instance.
    """
    db_handler = DatabaseHandler({
        "engine": "sqlite",  # Or MySQL config here
        "database": "colossusbot.db"
    })
    await client.add_cog(AdminCommands(client, db_handler))
