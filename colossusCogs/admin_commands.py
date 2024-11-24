from discord.ext import commands
from discord import Embed, Member, Role, Message
import discord
import random
import aiosqlite
import time
from typing import List, Tuple, Optional


class AdminCommands(commands.Cog):
    """
    Handles the core logic for administrative actions like muting, kicking, banning, and warnings.
    """

    def __init__(self, client: commands.Bot) -> None:
        """
        Initializes the AdminCommands cog.

        :param client: The Discord bot client instance.
        """
        self.client = client
        self.db_path = 'administrative_actions.db'
        self.user_actions: dict[int, List[float]] = {}
        self.ACTION_THRESHOLD = 15  # Actions in a short time
        self.TIME_WINDOW = 5  # Time window in seconds

    async def cog_load(self) -> None:
        """Handles logic to execute when the cog is loaded."""
        print("AdminCommands.cog_load: AdminCommands is starting...")
        await self.create_warning_table()
        print("AdminCommands.cog_load: AdminCommands is ready.")

    async def create_warning_table(self) -> None:
        """Creates the database table for storing user warnings."""
        print("AdminCommands.create_warning_table: Creating the warning table...")
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await db.commit()
        print("AdminCommands.create_warning_table: Warning table created.")

    async def log_warning(self, member: Member, reason: str) -> None:
        """
        Logs a warning for a member in the database.

        :param member: The member to log the warning for.
        :param reason: The reason for the warning.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT INTO warnings (user_id, guild_id, reason) VALUES (?, ?, ?)',
                (member.id, member.guild.id, reason)
            )
            await db.commit()

    async def fetch_warnings(self, member: Member) -> List[Tuple[str, str]]:
        """
        Fetches all warnings for a specific member.

        :param member: The member whose warnings to fetch.
        :return: A list of tuples containing the warning reason and timestamp.
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                'SELECT reason, timestamp FROM warnings WHERE user_id = ? AND guild_id = ?',
                (member.id, member.guild.id)
            )
            return await cursor.fetchall()

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
        await self.log_warning(member, reason)
        await self.send_embed(ctx, ctx.author, member, reason, "Warned")


async def setup(client: commands.Bot) -> None:
    """
    Registers the AdminCommands cog with the bot.

    :param client: The Discord bot client instance.
    """
    await client.add_cog(AdminCommands(client))
