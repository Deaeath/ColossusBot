# File: colossusCogs/eternal_slave_cog.py

"""
Eternal Slave Cog for ColossusBot
----------------------------------
This cog integrates the Eternal Slave functionality into ColossusBot, providing commands
for users to manage their profiles and interact within their kinky journey.

Features:
- Contract system with owners and subs.
- Manage subs' restrictions, tasks, rules, and more.
- Trusted users management.
- Voice and text channel controls.
- Profile branding and viewing.

Database Tables:
- users
- contracts
- tasks
- rules
- restricted_words
- trusted_users
"""

import discord
from discord.ext import commands
import logging
from handlers.database_handler import DatabaseHandler
from typing import Optional, Tuple, Any, Union, List
import asyncio

logger = logging.getLogger("ColossusBot")


class EternalSlaveCog(commands.Cog):
    """
    Eternal Slave cog integrates commands for managing user profiles and interactions
    related to the Eternal Slave functionality, including a contract system.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler) -> None:
        """
        Initializes the EternalSlaveCog.

        :param client: The instance of the Discord bot.
        :param db_handler: Instance of the DatabaseHandler to interact with the database.
        """
        self.client = client    
        self.db_handler = db_handler
        # self.setup_task = self.client.loop.create_task(self.setup_database())
        logger.info("EternalSlaveCog initialized.")

    async def cog_load(self) -> None:
        """Handles logic to execute when the cog is loaded."""
        logger.info("EternalSlaveCog is starting...")
        await self.setup_database()
        logger.info("EternalSlaveCog is ready.")
        
    async def setup_database(self) -> None:
        """
        Sets up the necessary database tables for the Eternal Slave functionality.
        Adjusts SQL syntax based on the database engine.
        """
        engine = self.db_handler.db_config.get("engine", "sqlite").lower()

        if engine == "sqlite":
            # Users table
            await self.db_handler.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_id BIGINT UNIQUE NOT NULL,
                    profile_setup BOOLEAN DEFAULT FALSE,
                    gagged TEXT,
                    muted BOOLEAN DEFAULT FALSE,
                    bound_channel BIGINT,
                    brand_top TEXT,
                    brand_bottom TEXT,
                    chastity BOOLEAN DEFAULT FALSE,
                    restrictions TEXT,
                    safe_word TEXT
                );
            """)

            # Contracts table
            await self.db_handler.execute("""
                CREATE TABLE IF NOT EXISTS contracts (
                    owner_id BIGINT,
                    sub_id BIGINT PRIMARY KEY,
                    FOREIGN KEY(owner_id) REFERENCES users(discord_id),
                    FOREIGN KEY(sub_id) REFERENCES users(discord_id)
                );
            """)

            # Tasks table
            await self.db_handler.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id BIGINT,
                    task_description TEXT,
                    completed BOOLEAN DEFAULT FALSE,
                    task_type TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(discord_id)
                );
            """)

            # Rules table
            await self.db_handler.execute("""
                CREATE TABLE IF NOT EXISTS rules (
                    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id BIGINT,
                    rule_text TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(discord_id)
                );
            """)

            # Restricted Words table
            await self.db_handler.execute("""
                CREATE TABLE IF NOT EXISTS restricted_words (
                    user_id BIGINT,
                    word TEXT,
                    PRIMARY KEY(user_id, word),
                    FOREIGN KEY(user_id) REFERENCES users(discord_id)
                );
            """)

            # Trusted Users table
            await self.db_handler.execute("""
                CREATE TABLE IF NOT EXISTS trusted_users (
                    owner_id BIGINT,
                    trusted_user_id BIGINT,
                    PRIMARY KEY(owner_id, trusted_user_id),
                    FOREIGN KEY(owner_id) REFERENCES users(discord_id),
                    FOREIGN KEY(trusted_user_id) REFERENCES users(discord_id)
                );
            """)

        elif engine == "mysql":
            # Users table
            await self.db_handler.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INT AUTO_INCREMENT PRIMARY KEY,
                    discord_id BIGINT UNIQUE NOT NULL,
                    profile_setup BOOLEAN DEFAULT FALSE,
                    gagged VARCHAR(255),
                    muted BOOLEAN DEFAULT FALSE,
                    bound_channel BIGINT,
                    brand_top VARCHAR(255),
                    brand_bottom VARCHAR(255),
                    chastity BOOLEAN DEFAULT FALSE,
                    restrictions TEXT,
                    safe_word VARCHAR(255)
                );
            """)

            # Contracts table
            await self.db_handler.execute("""
                CREATE TABLE IF NOT EXISTS contracts (
                    owner_id BIGINT,
                    sub_id BIGINT PRIMARY KEY,
                    FOREIGN KEY(owner_id) REFERENCES users(discord_id),
                    FOREIGN KEY(sub_id) REFERENCES users(discord_id)
                );
            """)

            # Tasks table
            await self.db_handler.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    task_description TEXT,
                    completed BOOLEAN DEFAULT FALSE,
                    task_type VARCHAR(50),
                    FOREIGN KEY(user_id) REFERENCES users(discord_id)
                );
            """)

            # Rules table
            await self.db_handler.execute("""
                CREATE TABLE IF NOT EXISTS rules (
                    rule_id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id BIGINT,
                    rule_text TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(discord_id)
                );
            """)

            # Restricted Words table
            await self.db_handler.execute("""
                CREATE TABLE IF NOT EXISTS restricted_words (
                    user_id BIGINT,
                    word VARCHAR(100),
                    PRIMARY KEY(user_id, word),
                    FOREIGN KEY(user_id) REFERENCES users(discord_id)
                );
            """)

            # Trusted Users table
            await self.db_handler.execute("""
                CREATE TABLE IF NOT EXISTS trusted_users (
                    owner_id BIGINT,
                    trusted_user_id BIGINT,
                    PRIMARY KEY(owner_id, trusted_user_id),
                    FOREIGN KEY(owner_id) REFERENCES users(discord_id),
                    FOREIGN KEY(trusted_user_id) REFERENCES users(discord_id)
                );
            """)

        else:
            logger.error(f"Unsupported database engine: {engine}")
            return

        logger.info("EternalSlaveCog database tables ensured.")

    # -------------------------------
    # Helper Methods
    # -------------------------------

    async def is_owner(self, owner_id: int, sub_id: int) -> bool:
        """
        Checks if the sub is owned by the owner.

        :param owner_id: The Discord ID of the owner.
        :param sub_id: The Discord ID of the sub.
        :return: True if owner owns the sub, else False.
        """
        result = await self.db_handler.fetchone("""
            SELECT * FROM contracts WHERE owner_id = ? AND sub_id = ?;
        """, (owner_id, sub_id))
        return result is not None

    async def add_user_if_not_exists(self, discord_id: int) -> None:
        """
        Adds a user to the users table if they do not already exist.

        :param discord_id: The Discord ID of the user.
        """
        existing = await self.db_handler.fetchone("""
            SELECT * FROM users WHERE discord_id = ?;
        """, (discord_id,))
        if not existing:
            try:
                await self.db_handler.execute("""
                    INSERT INTO users (discord_id, profile_setup) VALUES (?, FALSE);
                """, (discord_id,))
                logger.info(f"Added new user to database: {discord_id}")
            except Exception as e:
                logger.error(f"Error adding user {discord_id}: {e}")

    async def get_trusted_users(self, owner_id: int) -> List[int]:
        """
        Retrieves the list of trusted users for an owner.

        :param owner_id: The Discord ID of the owner.
        :return: List of trusted user Discord IDs.
        """
        rows = await self.db_handler.fetchall("""
            SELECT trusted_user_id FROM trusted_users WHERE owner_id = ?;
        """, (owner_id,))
        return [row[0] for row in rows] if rows else []

    async def is_trusted(self, owner_id: int, user_id: int) -> bool:
        """
        Checks if a user is trusted by the owner.

        :param owner_id: The Discord ID of the owner.
        :param user_id: The Discord ID of the user to check.
        :return: True if trusted, else False.
        """
        result = await self.db_handler.fetchone("""
            SELECT * FROM trusted_users WHERE owner_id = ? AND trusted_user_id = ?;
        """, (owner_id, user_id))
        return result is not None

    async def has_permissions(self, ctx: commands.Context, owner_id: int) -> bool:
        """
        Checks if the command invoker has permissions (is owner or trusted).

        :param ctx: The command context.
        :param owner_id: The Discord ID of the owner.
        :return: True if has permissions, else False.
        """
        if ctx.author.id == owner_id:
            return True
        if await self.is_trusted(owner_id, ctx.author.id):
            return True
        return False

    async def get_user_profile(self, discord_id: int) -> Optional[Tuple]:
        """
        Retrieves a user's profile from the database.

        :param discord_id: The Discord ID of the user.
        :return: Tuple containing user data or None if not found.
        """
        return await self.db_handler.fetchone("""
            SELECT * FROM users WHERE discord_id = ?;
        """, (discord_id,))

    # -------------------------------
    # Commands
    # -------------------------------

    @commands.command(
        name="bind",
        help="Bind one of your subs to a channel.",
        usage="!bind [@sub] [#channel]",
    )
    @commands.cooldown(rate=1, per=150, type=commands.BucketType.user)
    async def bind(self, ctx: commands.Context, sub: discord.Member, channel: discord.TextChannel) -> None:
        """
        Binds a sub to a specific text channel.

        :param ctx: The context of the command call.
        :param sub: The sub to bind.
        :param channel: The channel to bind the sub to.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check if the invoker owns the sub
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to bind a sub they do not own: {sub.id}")
            return

        # Bind the sub to the channel
        try:
            await self.db_handler.execute("""
                UPDATE users SET bound_channel = ? WHERE discord_id = ?;
            """, (channel.id, sub.id))
            await ctx.send(f"{sub.mention} has been bound to {channel.mention}.")
            logger.info(f"User {sub.id} bound to channel {channel.id} by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while binding the sub.")
            logger.error(f"Error binding user {sub.id} to channel {channel.id} by {ctx.author.id}: {e}")

    @commands.command(
        name="chastity",
        help="Put one of your subs in chastity in this server.",
        usage="!chastity [@sub] [enable/disable]",
    )
    @commands.cooldown(rate=1, per=150, type=commands.BucketType.user)
    async def chastity(self, ctx: commands.Context, sub: discord.Member, action: str) -> None:
        """
        Enables or disables chastity for a sub.

        :param ctx: The context of the command call.
        :param sub: The sub to apply chastity to.
        :param action: 'enable' or 'disable'.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to chastity a sub they do not own: {sub.id}")
            return

        if action.lower() not in ["enable", "disable"]:
            await ctx.send("Please specify 'enable' or 'disable'.")
            return

        status = True if action.lower() == "enable" else False
        try:
            await self.db_handler.execute("""
                UPDATE users SET chastity = ? WHERE discord_id = ?;
            """, (status, sub.id))
            status_text = "enabled" if status else "disabled"
            await ctx.send(f"Chastity has been {status_text} for {sub.mention}.")
            logger.info(f"Chastity {status_text} for user {sub.id} by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while updating chastity status.")
            logger.error(f"Error updating chastity for user {sub.id} by {ctx.author.id}: {e}")

    @commands.command(
        name="gag",
        help="Gag one of your subs.",
        usage="!gag [@sub] [type]",
    )
    @commands.cooldown(rate=1, per=8, type=commands.BucketType.user)  # Adjusted cooldown to integer
    async def gag(self, ctx: commands.Context, sub: discord.Member, gag_type: str) -> None:
        """
        Gags a sub with a specified type.

        :param ctx: The context of the command call.
        :param sub: The sub to gag.
        :param gag_type: The type of gag to apply.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to gag a sub they do not own: {sub.id}")
            return

        try:
            await self.db_handler.execute("""
                UPDATE users SET gagged = ? WHERE discord_id = ?;
            """, (gag_type, sub.id))
            await ctx.send(f"{sub.mention} has been gagged with a {gag_type} gag.")
            logger.info(f"User {sub.id} gagged with type {gag_type} by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while gagging the sub.")
            logger.error(f"Error gagging user {sub.id} by {ctx.author.id}: {e}")

    @commands.command(
        name="mute-sub",
        help="Mute one of your subs.",
        usage="!mute-sub [@sub]",
    )
    @commands.cooldown(rate=1, per=8, type=commands.BucketType.user)  # Adjusted cooldown to integer
    async def mute_sub(self, ctx: commands.Context, sub: discord.Member) -> None:
        """
        Mutes a sub, preventing them from sending messages.

        :param ctx: The context of the command call.
        :param sub: The sub to mute.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to mute a sub they do not own: {sub.id}")
            return

        try:
            await self.db_handler.execute("""
                UPDATE users SET muted = TRUE WHERE discord_id = ?;
            """, (sub.id,))
            await ctx.send(f"{sub.mention} has been muted.")
            logger.info(f"User {sub.id} muted by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while muting the sub.")
            logger.error(f"Error muting user {sub.id} by {ctx.author.id}: {e}")

    @commands.command(
        name="rename",
        help="Change the nickname of one of your subs.",
        usage="!rename [@sub] [new nickname]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def rename(self, ctx: commands.Context, sub: discord.Member, *, new_nickname: str) -> None:
        """
        Changes the nickname of a sub.

        :param ctx: The context of the command call.
        :param sub: The sub to rename.
        :param new_nickname: The new nickname for the sub.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to rename a sub they do not own: {sub.id}")
            return

        try:
            await sub.edit(nick=new_nickname)
            await ctx.send(f"{sub.mention}'s nickname has been changed to {new_nickname}.")
            logger.info(f"User {sub.id}'s nickname changed to {new_nickname} by {ctx.author.id}.")
        except discord.Forbidden:
            await ctx.send("I do not have permission to change this user's nickname.")
            logger.error(f"Permission denied when renaming user {sub.id} by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while changing the nickname.")
            logger.error(f"Error renaming user {sub.id} by {ctx.author.id}: {e}")

    @commands.group(
        name="voice",
        help="Manage voice-related settings for your sub.",
        usage="!voice [subcommand] [@sub]",
    )
    async def voice(self, ctx: commands.Context) -> None:
        """
        Group command for managing voice settings.

        :param ctx: The context of the command call.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Available subcommands: mute, deafen")
            logger.warning(f"Voice command invoked without subcommand by {ctx.author.id}.")

    @voice.command(
        name="mute",
        help="Mute one of your subs in voice channels.",
        usage="!voice mute [@sub]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def voice_mute(self, ctx: commands.Context, sub: discord.Member) -> None:
        """
        Mutes a sub in voice channels.

        :param ctx: The context of the command call.
        :param sub: The sub to mute.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to voice mute a sub they do not own: {sub.id}")
            return

        voice_state = sub.voice
        if voice_state and voice_state.channel:
            try:
                await sub.edit(mute=True)
                await ctx.send(f"{sub.mention} has been muted in voice channels.")
                logger.info(f"User {sub.id} muted in voice by {ctx.author.id}.")
            except discord.Forbidden:
                await ctx.send("I do not have permission to mute this user in voice channels.")
                logger.error(f"Permission denied when muting user {sub.id} in voice by {ctx.author.id}.")
            except Exception as e:
                await ctx.send("An error occurred while muting the sub in voice channels.")
                logger.error(f"Error muting user {sub.id} in voice by {ctx.author.id}: {e}")
        else:
            await ctx.send(f"{sub.mention} is not in a voice channel.")
            logger.warning(f"Voice mute attempted on user {sub.id} who is not in a voice channel by {ctx.author.id}.")

    @voice.command(
        name="deafen",
        help="Deafen one of your subs in voice channels.",
        usage="!voice deafen [@sub]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def voice_deafen(self, ctx: commands.Context, sub: discord.Member) -> None:
        """
        Deafens a sub in voice channels.

        :param ctx: The context of the command call.
        :param sub: The sub to deafen.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to voice deafen a sub they do not own: {sub.id}")
            return

        voice_state = sub.voice
        if voice_state and voice_state.channel:
            try:
                await sub.edit(deafen=True)
                await ctx.send(f"{sub.mention} has been deafened in voice channels.")
                logger.info(f"User {sub.id} deafened in voice by {ctx.author.id}.")
            except discord.Forbidden:
                await ctx.send("I do not have permission to deafen this user in voice channels.")
                logger.error(f"Permission denied when deafening user {sub.id} in voice by {ctx.author.id}.")
            except Exception as e:
                await ctx.send("An error occurred while deafening the sub in voice channels.")
                logger.error(f"Error deafening user {sub.id} in voice by {ctx.author.id}: {e}")
        else:
            await ctx.send(f"{sub.mention} is not in a voice channel.")
            logger.warning(f"Voice deafen attempted on user {sub.id} who is not in a voice channel by {ctx.author.id}.")

    @commands.command(
        name="brand",
        help="Brand one of your subs' profiles.",
        usage="!brand [@sub] [top text] | [bottom text]",
    )
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    async def brand(self, ctx: commands.Context, sub: discord.Member, *, texts: str) -> None:
        """
        Adds branding text to the top and bottom of a sub's profile.

        :param ctx: The context of the command call.
        :param sub: The sub to brand.
        :param texts: The branding texts separated by '|'.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to brand a sub they do not own: {sub.id}")
            return

        try:
            top_text, bottom_text = [text.strip() for text in texts.split('|', 1)]
            await self.db_handler.execute("""
                UPDATE users SET brand_top = ?, brand_bottom = ? WHERE discord_id = ?;
            """, (top_text, bottom_text, sub.id))
            await ctx.send(f"{sub.mention}'s profile has been branded.")
            logger.info(f"User {sub.id} branded with top: '{top_text}' and bottom: '{bottom_text}' by {ctx.author.id}.")
        except ValueError:
            await ctx.send("Please provide both top and bottom text separated by '|'.")
            logger.error(f"Brand command invoked with incorrect format by {ctx.author.id}.")

    @commands.group(
        name="trusted",
        help="Manage your trusted users.",
        usage="!trusted [add/remove/clear] [@user]",
    )
    async def trusted(self, ctx: commands.Context) -> None:
        """
        Group command for managing trusted users.

        :param ctx: The context of the command call.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Available subcommands: add, remove, clear")
            logger.warning(f"Trusted command invoked without subcommand by {ctx.author.id}.")

    @trusted.command(
        name="add",
        help="Add a user to your trusted users.",
        usage="!trusted add [@user]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def trusted_add(self, ctx: commands.Context, user: discord.Member) -> None:
        """
        Adds a user to the owner's trusted users.

        :param ctx: The context of the command call.
        :param user: The user to add to trusted users.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(user.id)

        if await self.is_trusted(ctx.author.id, user.id):
            await ctx.send(f"{user.mention} is already a trusted user.")
            return

        try:
            await self.db_handler.execute("""
                INSERT INTO trusted_users (owner_id, trusted_user_id) VALUES (?, ?);
            """, (ctx.author.id, user.id))
            await ctx.send(f"{user.mention} has been added to your trusted users.")
            logger.info(f"User {user.id} added to trusted users by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while adding the trusted user.")
            logger.error(f"Error adding trusted user {user.id} by {ctx.author.id}: {e}")

    @trusted.command(
        name="remove",
        help="Remove a user from your trusted users.",
        usage="!trusted remove [@user]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def trusted_remove(self, ctx: commands.Context, user: discord.Member) -> None:
        """
        Removes a user from the owner's trusted users.

        :param ctx: The context of the command call.
        :param user: The user to remove from trusted users.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(user.id)

        if not await self.is_trusted(ctx.author.id, user.id):
            await ctx.send(f"{user.mention} is not in your trusted users.")
            return

        try:
            await self.db_handler.execute("""
                DELETE FROM trusted_users WHERE owner_id = ? AND trusted_user_id = ?;
            """, (ctx.author.id, user.id))
            await ctx.send(f"{user.mention} has been removed from your trusted users.")
            logger.info(f"User {user.id} removed from trusted users by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while removing the trusted user.")
            logger.error(f"Error removing trusted user {user.id} by {ctx.author.id}: {e}")

    @trusted.command(
        name="clear",
        help="Remove all of your trusted users.",
        usage="!trusted clear",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def trusted_clear(self, ctx: commands.Context) -> None:
        """
        Clears all trusted users for the owner.

        :param ctx: The context of the command call.
        """
        await self.add_user_if_not_exists(ctx.author.id)

        try:
            await self.db_handler.execute("""
                DELETE FROM trusted_users WHERE owner_id = ?;
            """, (ctx.author.id,))
            await ctx.send("All of your trusted users have been removed.")
            logger.info(f"All trusted users cleared by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while clearing trusted users.")
            logger.error(f"Error clearing trusted users by {ctx.author.id}: {e}")

    @commands.command(
        name="disown",
        help="Disown one of your subs.",
        usage="!disown [@sub]",
    )
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def disown(self, ctx: commands.Context, sub: discord.Member) -> None:
        """
        Disowns a sub, removing the contract.

        :param ctx: The context of the command call.
        :param sub: The sub to disown.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to disown a sub they do not own: {sub.id}")
            return

        try:
            await self.db_handler.execute("""
                DELETE FROM contracts WHERE owner_id = ? AND sub_id = ?;
            """, (ctx.author.id, sub.id))
            await self.db_handler.execute("""
                UPDATE users SET gagged = NULL, muted = FALSE, bound_channel = NULL, brand_top = NULL,
                    brand_bottom = NULL, chastity = FALSE, restrictions = NULL WHERE discord_id = ?;
            """, (sub.id,))
            await ctx.send(f"You have disowned {sub.mention}. All impairments and restrictions have been removed.")
            logger.info(f"User {sub.id} disowned by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while disowning the sub.")
            logger.error(f"Error disowning user {sub.id} by {ctx.author.id}: {e}")

    @commands.command(
        name="leave",
        help="Leave your current owner and remove all impairments/restrictions.",
        usage="!leave",
    )
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def leave(self, ctx: commands.Context) -> None:
        """
        Allows a sub to leave their current owner, removing all impairments and restrictions.

        :param ctx: The context of the command call.
        """
        sub_id = ctx.author.id
        # Check if the user is a sub in any contract
        result = await self.db_handler.fetchone("""
            SELECT owner_id FROM contracts WHERE sub_id = ?;
        """, (sub_id,))
        if not result:
            await ctx.send("You are not currently owned by anyone.")
            return

        owner_id = result[0]
        try:
            await self.db_handler.execute("""
                DELETE FROM contracts WHERE owner_id = ? AND sub_id = ?;
            """, (owner_id, sub_id))
            await self.db_handler.execute("""
                UPDATE users SET gagged = NULL, muted = FALSE, bound_channel = NULL, brand_top = NULL,
                    brand_bottom = NULL, chastity = FALSE, restrictions = NULL WHERE discord_id = ?;
            """, (sub_id,))
            await ctx.send("You have left your current owner. All impairments and restrictions have been removed.")
            logger.info(f"User {sub_id} has left owner {owner_id}.")
        except Exception as e:
            await ctx.send("An error occurred while leaving the owner.")
            logger.error(f"Error letting user {sub_id} leave owner {owner_id}: {e}")

    @commands.command(
        name="safeword",
        help="Use your safeword to remove impairments and restrictions.",
        usage="!safeword [your safeword]",
    )
    @commands.cooldown(rate=1, per=150, type=commands.BucketType.user)
    async def safeword(self, ctx: commands.Context, *, word: str) -> None:
        """
        Allows a sub to use their safeword to remove impairments and restrictions.

        :param ctx: The context of the command call.
        :param word: The safeword.
        """
        sub_id = ctx.author.id
        user_record = await self.get_user_profile(sub_id)
        if not user_record:
            await ctx.send("You do not have a profile set up.")
            return

        stored_word = user_record[10]  # safe_word is the 11th column
        if stored_word != word:
            await ctx.send("Incorrect safeword.")
            logger.warning(f"User {sub_id} provided incorrect safeword.")
            return

        try:
            # Remove impairments/restrictions
            await self.db_handler.execute("""
                UPDATE users SET gagged = NULL, muted = FALSE, bound_channel = NULL, brand_top = NULL,
                    brand_bottom = NULL, chastity = FALSE, restrictions = NULL WHERE discord_id = ?;
            """, (sub_id,))
            await self.db_handler.execute("""
                DELETE FROM contracts WHERE sub_id = ?;
            """, (sub_id,))
            await ctx.send("Safeword accepted. All impairments and restrictions have been removed.")
            logger.info(f"User {sub_id} used safeword to remove impairments.")
        except Exception as e:
            await ctx.send("An error occurred while using the safeword.")
            logger.error(f"Error processing safeword for user {sub_id}: {e}")

    @commands.command(
        name="e-say",
        help="Send a message as one of your subs.",
        usage="!e-say [@sub] [message]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def esay(self, ctx: commands.Context, sub: discord.Member, *, message: str) -> None:
        """
        Sends a message as if it were from the specified sub.

        :param ctx: The context of the command call.
        :param sub: The sub to impersonate.
        :param message: The message to send.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to say as a sub they do not own: {sub.id}")
            return

        try:
            await sub.send(message)
            await ctx.send(f"Message sent as {sub.display_name}.")
            logger.info(f"User {ctx.author.id} sent message as {sub.id}: {message}")
        except discord.Forbidden:
            await ctx.send("I cannot send a DM to this user.")
            logger.error(f"Permission denied when sending DM as user {sub.id} by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while sending the message.")
            logger.error(f"Error sending message as user {sub.id} by {ctx.author.id}: {e}")

    @commands.command(
        name="claim",
        help="Request to claim a user as your sub.",
        usage="!claim [@user]",
    )
    @commands.cooldown(rate=1, per=30, type=commands.BucketType.user)
    async def claim(self, ctx: commands.Context, sub: discord.Member) -> None:
        """
        Requests to claim a user as a sub.

        :param ctx: The context of the command call.
        :param sub: The user to claim.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check if the sub is already claimed
        existing = await self.db_handler.fetchone("""
            SELECT * FROM contracts WHERE sub_id = ?;
        """, (sub.id,))
        if existing:
            await ctx.send(f"{sub.mention} is already claimed by another owner.")
            logger.warning(f"User {ctx.author.id} attempted to claim already claimed sub: {sub.id}")
            return

        try:
            # Create the contract
            await self.db_handler.execute("""
                INSERT INTO contracts (owner_id, sub_id) VALUES (?, ?);
            """, (ctx.author.id, sub.id))
            await ctx.send(f"You have successfully claimed {sub.mention} as your sub.")
            logger.info(f"User {sub.id} claimed by owner {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while claiming the sub.")
            logger.error(f"Error claiming user {sub.id} by {ctx.author.id}: {e}")

    @commands.command(
        name="restrictions",
        help="View and update one of your sub's restrictions.",
        usage="!restrictions [@sub] [add/remove/list] [restriction]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def restrictions_command(self, ctx: commands.Context, sub: discord.Member, action: str, *, restriction: Optional[str] = None) -> None:
        """
        Views or updates a sub's restrictions.

        :param ctx: The context of the command call.
        :param sub: The sub to manage restrictions for.
        :param action: 'add', 'remove', or 'list'.
        :param restriction: The restriction to add or remove.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to manage restrictions for a sub they do not own: {sub.id}")
            return

        if action.lower() == "add":
            if not restriction:
                await ctx.send("Please specify a restriction to add.")
                return
            # Fetch current restrictions
            current = await self.get_user_profile(sub.id)
            current_restrictions = current[9].split(',') if current and current[9] else []
            if restriction.lower() in [r.lower() for r in current_restrictions]:
                await ctx.send("This restriction is already applied to the sub.")
                return
            current_restrictions.append(restriction)
            updated = ','.join(current_restrictions)
            try:
                await self.db_handler.execute("""
                    UPDATE users SET restrictions = ? WHERE discord_id = ?;
                """, (updated, sub.id))
                await ctx.send(f"Restriction '{restriction}' has been added to {sub.mention}.")
                logger.info(f"Restriction '{restriction}' added to user {sub.id} by {ctx.author.id}.")
            except Exception as e:
                await ctx.send("An error occurred while adding the restriction.")
                logger.error(f"Error adding restriction '{restriction}' to user {sub.id} by {ctx.author.id}: {e}")

        elif action.lower() == "remove":
            if not restriction:
                await ctx.send("Please specify a restriction to remove.")
                return
            # Fetch current restrictions
            current = await self.get_user_profile(sub.id)
            current_restrictions = current[9].split(',') if current and current[9] else []
            if restriction.lower() not in [r.lower() for r in current_restrictions]:
                await ctx.send("This restriction is not applied to the sub.")
                return
            # Remove the restriction
            updated_restrictions = [r for r in current_restrictions if r.lower() != restriction.lower()]
            updated = ','.join(updated_restrictions)
            try:
                await self.db_handler.execute("""
                    UPDATE users SET restrictions = ? WHERE discord_id = ?;
                """, (updated, sub.id))
                await ctx.send(f"Restriction '{restriction}' has been removed from {sub.mention}.")
                logger.info(f"Restriction '{restriction}' removed from user {sub.id} by {ctx.author.id}.")
            except Exception as e:
                await ctx.send("An error occurred while removing the restriction.")
                logger.error(f"Error removing restriction '{restriction}' from user {sub.id} by {ctx.author.id}: {e}")

        elif action.lower() == "list":
            current = await self.get_user_profile(sub.id)
            restrictions_list = current[9].split(',') if current and current[9] else []
            if restrictions_list:
                await ctx.send(f"Current restrictions for {sub.mention}: " + ', '.join(restrictions_list))
            else:
                await ctx.send(f"{sub.mention} has no restrictions.")
            logger.info(f"Restrictions listed for user {sub.id} by {ctx.author.id}.")

        else:
            await ctx.send("Invalid action. Use 'add', 'remove', or 'list'.")
            logger.warning(f"User {ctx.author.id} invoked restrictions with invalid action: {action}")

    @commands.group(
        name="rules",
        help="Manage rules for your subs.",
        usage="!rules [add/remove/update] [@sub] [rule_id] [text]",
    )
    async def rules(self, ctx: commands.Context) -> None:
        """
        Group command for managing rules.

        :param ctx: The context of the command call.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Available subcommands: add, remove, update")
            logger.warning(f"Rules command invoked without subcommand by {ctx.author.id}.")

    @rules.command(
        name="add",
        help="Add a rule to one of your subs.",
        usage="!rules add [@sub] [rule text]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def rules_add(self, ctx: commands.Context, sub: discord.Member, *, rule_text: str) -> None:
        """
        Adds a rule to a sub.

        :param ctx: The context of the command call.
        :param sub: The sub to add the rule to.
        :param rule_text: The text of the rule.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to add a rule to a sub they do not own: {sub.id}")
            return

        try:
            await self.db_handler.execute("""
                INSERT INTO rules (user_id, rule_text) VALUES (?, ?);
            """, (sub.id, rule_text))
            await ctx.send(f"Rule added to {sub.mention}.")
            logger.info(f"Rule added to user {sub.id} by {ctx.author.id}: {rule_text}")
        except Exception as e:
            await ctx.send("An error occurred while adding the rule.")
            logger.error(f"Error adding rule to user {sub.id} by {ctx.author.id}: {e}")

    @rules.command(
        name="remove",
        help="Remove a rule from one of your subs.",
        usage="!rules remove [@sub] [rule_id]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def rules_remove(self, ctx: commands.Context, sub: discord.Member, rule_id: int) -> None:
        """
        Removes a rule from a sub.

        :param ctx: The context of the command call.
        :param sub: The sub to remove the rule from.
        :param rule_id: The ID of the rule to remove.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to remove a rule from a sub they do not own: {sub.id}")
            return

        # Check if the rule exists
        rule = await self.db_handler.fetchone("""
            SELECT * FROM rules WHERE rule_id = ? AND user_id = ?;
        """, (rule_id, sub.id))
        if not rule:
            await ctx.send("Rule not found.")
            logger.warning(f"Rule ID {rule_id} not found for user {sub.id}.")
            return

        try:
            await self.db_handler.execute("""
                DELETE FROM rules WHERE rule_id = ? AND user_id = ?;
            """, (rule_id, sub.id))
            await ctx.send(f"Rule {rule_id} has been removed from {sub.mention}.")
            logger.info(f"Rule {rule_id} removed from user {sub.id} by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while removing the rule.")
            logger.error(f"Error removing rule {rule_id} from user {sub.id} by {ctx.author.id}: {e}")

    @rules.command(
        name="update",
        help="Update the text of one of your sub's rules.",
        usage="!rules update [@sub] [rule_id] [new text]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def rules_update(self, ctx: commands.Context, sub: discord.Member, rule_id: int, *, new_text: str) -> None:
        """
        Updates the text of a rule for a sub.

        :param ctx: The context of the command call.
        :param sub: The sub to update the rule for.
        :param rule_id: The ID of the rule to update.
        :param new_text: The new text for the rule.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to update a rule for a sub they do not own: {sub.id}")
            return

        # Check if the rule exists
        rule = await self.db_handler.fetchone("""
            SELECT * FROM rules WHERE rule_id = ? AND user_id = ?;
        """, (rule_id, sub.id))
        if not rule:
            await ctx.send("Rule not found.")
            logger.warning(f"Rule ID {rule_id} not found for user {sub.id}.")
            return

        try:
            await self.db_handler.execute("""
                UPDATE rules SET rule_text = ? WHERE rule_id = ? AND user_id = ?;
            """, (new_text, rule_id, sub.id))
            await ctx.send(f"Rule {rule_id} has been updated for {sub.mention}.")
            logger.info(f"Rule {rule_id} updated for user {sub.id} by {ctx.author.id} to: {new_text}")
        except Exception as e:
            await ctx.send("An error occurred while updating the rule.")
            logger.error(f"Error updating rule {rule_id} for user {sub.id} by {ctx.author.id}: {e}")

    @commands.group(
        name="task",
        help="Manage tasks for your sub.",
        usage="!task [view/mark/remove/list/add] [@sub] [options]",
    )
    async def task(self, ctx: commands.Context) -> None:
        """
        Group command for managing tasks.

        :param ctx: The context of the command call.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Available subcommands: view, mark, remove, list, add")
            logger.warning(f"Task command invoked without subcommand by {ctx.author.id}.")

    @task.command(
        name="view",
        help="View all information regarding a task.",
        usage="!task view [task_id]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def task_view(self, ctx: commands.Context, task_id: int) -> None:
        """
        Views information about a specific task.

        :param ctx: The context of the command call.
        :param task_id: The ID of the task to view.
        """
        task = await self.db_handler.fetchone("""
            SELECT * FROM tasks WHERE task_id = ?;
        """, (task_id,))
        if not task:
            await ctx.send("Task not found.")
            logger.warning(f"Task ID {task_id} not found.")
            return

        user_id = task[1]
        task_description = task[2]
        completed = task[3]
        task_type = task[4]

        embed = discord.Embed(title=f"Task {task_id}", color=discord.Color.blue())
        embed.add_field(name="User", value=f"<@{user_id}>", inline=False)
        embed.add_field(name="Description", value=task_description, inline=False)
        embed.add_field(name="Completed", value=str(completed), inline=False)
        embed.add_field(name="Type", value=task_type.capitalize(), inline=False)
        await ctx.send(embed=embed)
        logger.info(f"Task {task_id} viewed by {ctx.author.id}.")

    @task.command(
        name="mark",
        help="Mark a task as complete or incomplete.",
        usage="!task mark [task_id] [complete/incomplete]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def task_mark(self, ctx: commands.Context, task_id: int, status: str) -> None:
        """
        Marks a task as complete or incomplete.

        :param ctx: The context of the command call.
        :param task_id: The ID of the task to mark.
        :param status: 'complete' or 'incomplete'.
        """
        if status.lower() not in ["complete", "incomplete"]:
            await ctx.send("Please specify 'complete' or 'incomplete'.")
            return

        task = await self.db_handler.fetchone("""
            SELECT * FROM tasks WHERE task_id = ?;
        """, (task_id,))
        if not task:
            await ctx.send("Task not found.")
            logger.warning(f"Task ID {task_id} not found.")
            return

        completed = True if status.lower() == "complete" else False
        try:
            await self.db_handler.execute("""
                UPDATE tasks SET completed = ? WHERE task_id = ?;
            """, (completed, task_id))
            await ctx.send(f"Task {task_id} has been marked as {status.lower()}.")
            logger.info(f"Task {task_id} marked as {status.lower()} by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while updating the task status.")
            logger.error(f"Error updating task {task_id} status by {ctx.author.id}: {e}")

    @task.command(
        name="remove",
        help="Remove a task from a user.",
        usage="!task remove [task_id]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def task_remove(self, ctx: commands.Context, task_id: int) -> None:
        """
        Removes a task from the database.

        :param ctx: The context of the command call.
        :param task_id: The ID of the task to remove.
        """
        task = await self.db_handler.fetchone("""
            SELECT * FROM tasks WHERE task_id = ?;
        """, (task_id,))
        if not task:
            await ctx.send("Task not found.")
            logger.warning(f"Task ID {task_id} not found.")
            return

        try:
            await self.db_handler.execute("""
                DELETE FROM tasks WHERE task_id = ?;
            """, (task_id,))
            await ctx.send(f"Task {task_id} has been removed.")
            logger.info(f"Task {task_id} removed by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while removing the task.")
            logger.error(f"Error removing task {task_id} by {ctx.author.id}: {e}")

    @task.command(
        name="list",
        help="List tasks for a user.",
        usage="!task list [@sub]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def task_list(self, ctx: commands.Context, sub: discord.Member) -> None:
        """
        Lists all tasks for a specific sub.

        :param ctx: The context of the command call.
        :param sub: The sub to list tasks for.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to list tasks for a sub they do not own: {sub.id}")
            return

        tasks = await self.db_handler.fetchall("""
            SELECT task_id, task_description, completed, task_type FROM tasks WHERE user_id = ?;
        """, (sub.id,))
        if not tasks:
            await ctx.send(f"{sub.mention} has no tasks.")
            return

        embed = discord.Embed(title=f"Tasks for {sub.display_name}", color=discord.Color.green())
        for task in tasks:
            status = "✅" if task[2] else "❌"
            embed.add_field(name=f"Task {task[0]} ({task[3].capitalize()})", value=f"{status} {task[1]}", inline=False)
        await ctx.send(embed=embed)
        logger.info(f"Tasks listed for user {sub.id} by {ctx.author.id}.")

    @task.group(
        name="add",
        help="Add a task to your sub.",
        usage="!task add [basic/writing] [@sub] [task description]",
    )
    async def task_add(self, ctx: commands.Context) -> None:
        """
        Group command for adding tasks.

        :param ctx: The context of the command call.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Available subcommands: basic, writing")
            logger.warning(f"Task add command invoked without subcommand by {ctx.author.id}.")

    @task_add.command(
        name="basic",
        help="Create a basic task for a user.",
        usage="!task add basic [@sub] [task description]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def task_add_basic(self, ctx: commands.Context, sub: discord.Member, *, task_description: str) -> None:
        """
        Adds a basic task to a sub.

        :param ctx: The context of the command call.
        :param sub: The sub to assign the task to.
        :param task_description: The description of the task.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to add a basic task to a sub they do not own: {sub.id}")
            return

        try:
            await self.db_handler.execute("""
                INSERT INTO tasks (user_id, task_description, task_type) VALUES (?, ?, 'basic');
            """, (sub.id, task_description))
            await ctx.send(f"Basic task added to {sub.mention}.")
            logger.info(f"Basic task added to user {sub.id} by {ctx.author.id}: {task_description}")
        except Exception as e:
            await ctx.send("An error occurred while adding the task.")
            logger.error(f"Error adding basic task to user {sub.id} by {ctx.author.id}: {e}")

    @task_add.command(
        name="writing",
        help="Create a writing task for a user.",
        usage="!task add writing [@sub] [task description]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def task_add_writing(self, ctx: commands.Context, sub: discord.Member, *, task_description: str) -> None:
        """
        Adds a writing task to a sub.

        :param ctx: The context of the command call.
        :param sub: The sub to assign the task to.
        :param task_description: The description of the task.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to add a writing task to a sub they do not own: {sub.id}")
            return

        try:
            await self.db_handler.execute("""
                INSERT INTO tasks (user_id, task_description, task_type) VALUES (?, ?, 'writing');
            """, (sub.id, task_description))
            await ctx.send(f"Writing task added to {sub.mention}.")
            logger.info(f"Writing task added to user {sub.id} by {ctx.author.id}: {task_description}")
        except Exception as e:
            await ctx.send("An error occurred while adding the task.")
            logger.error(f"Error adding writing task to user {sub.id} by {ctx.author.id}: {e}")

    @commands.command(
        name="profile",
        help="View a user's BDSM profile.",
        usage="!profile [@user]",
    )
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.user)
    async def profile(self, ctx: commands.Context, user: discord.Member) -> None:
        """
        Displays a user's BDSM profile.

        :param ctx: The context of the command call.
        :param user: The user whose profile to view.
        """
        await self.add_user_if_not_exists(user.id)

        user_record = await self.get_user_profile(user.id)
        if not user_record:
            await ctx.send("This user does not have a profile set up.")
            return

        embed = discord.Embed(title=f"{user.display_name}'s BDSM Profile", color=discord.Color.purple())
        embed.add_field(name="Gagged", value=user_record[3] or "None", inline=True)
        embed.add_field(name="Muted", value=str(user_record[4]), inline=True)
        embed.add_field(name="Chastity", value=str(user_record[8]), inline=True)
        embed.add_field(name="Brand Top", value=user_record[5] or "None", inline=False)
        embed.add_field(name="Brand Bottom", value=user_record[6] or "None", inline=False)
        await ctx.send(embed=embed)
        logger.info(f"Profile viewed for user {user.id} by {ctx.author.id}.")

    @commands.group(
        name="restricted-words",
        help="Manage restricted words for your subs.",
        usage="!restricted-words [add/remove/clear/toggle] [@sub] [word]",
    )
    async def restricted_words(self, ctx: commands.Context) -> None:
        """
        Group command for managing restricted words.

        :param ctx: The context of the command call.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Available subcommands: add, remove, clear, toggle")
            logger.warning(f"Restricted-words command invoked without subcommand by {ctx.author.id}.")

    @restricted_words.command(
        name="add",
        help="Add new restricted words to one of your subs.",
        usage="!restricted-words add [@sub] [word]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def restricted_words_add(self, ctx: commands.Context, sub: discord.Member, word: str) -> None:
        """
        Adds a restricted word to a sub.

        :param ctx: The context of the command call.
        :param sub: The sub to add the restricted word to.
        :param word: The word to restrict.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to add restricted word to a sub they do not own: {sub.id}")
            return

        try:
            await self.db_handler.execute("""
                INSERT INTO restricted_words (user_id, word) VALUES (?, ?);
            """, (sub.id, word.lower()))
            await ctx.send(f"Word '{word}' has been added to {sub.mention}'s restricted words.")
            logger.info(f"Word '{word}' added to restricted words for user {sub.id} by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while adding the restricted word.")
            logger.error(f"Error adding restricted word '{word}' to user {sub.id} by {ctx.author.id}: {e}")

    @restricted_words.command(
        name="remove",
        help="Remove a restricted word from one of your subs.",
        usage="!restricted-words remove [@sub] [word]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def restricted_words_remove(self, ctx: commands.Context, sub: discord.Member, word: str) -> None:
        """
        Removes a restricted word from a sub.

        :param ctx: The context of the command call.
        :param sub: The sub to remove the restricted word from.
        :param word: The word to remove.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to remove restricted word from a sub they do not own: {sub.id}")
            return

        try:
            await self.db_handler.execute("""
                DELETE FROM restricted_words WHERE user_id = ? AND word = ?;
            """, (sub.id, word.lower()))
            await ctx.send(f"Word '{word}' has been removed from {sub.mention}'s restricted words.")
            logger.info(f"Word '{word}' removed from restricted words for user {sub.id} by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while removing the restricted word.")
            logger.error(f"Error removing restricted word '{word}' from user {sub.id} by {ctx.author.id}: {e}")

    @restricted_words.command(
        name="clear",
        help="Remove all restricted words from one of your subs.",
        usage="!restricted-words clear [@sub]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def restricted_words_clear(self, ctx: commands.Context, sub: discord.Member) -> None:
        """
        Clears all restricted words from a sub.

        :param ctx: The context of the command call.
        :param sub: The sub to clear restricted words from.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to clear restricted words from a sub they do not own: {sub.id}")
            return

        try:
            await self.db_handler.execute("""
                DELETE FROM restricted_words WHERE user_id = ?;
            """, (sub.id,))
            await ctx.send(f"All restricted words have been removed from {sub.mention}.")
            logger.info(f"All restricted words cleared for user {sub.id} by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while clearing restricted words.")
            logger.error(f"Error clearing restricted words for user {sub.id} by {ctx.author.id}: {e}")

    @restricted_words.command(
        name="toggle",
        help="Quickly enable or disable a user's restricted words.",
        usage="!restricted-words toggle [@sub]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def restricted_words_toggle(self, ctx: commands.Context, sub: discord.Member) -> None:
        """
        Toggles the restricted words for a sub by clearing or re-adding them.

        :param ctx: The context of the command call.
        :param sub: The sub to toggle restricted words for.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to toggle restricted words for a sub they do not own: {sub.id}")
            return

        # Check if sub has any restricted words
        restricted = await self.db_handler.fetchall("""
            SELECT word FROM restricted_words WHERE user_id = ?;
        """, (sub.id,))
        if restricted:
            # Clear them
            try:
                await self.db_handler.execute("""
                    DELETE FROM restricted_words WHERE user_id = ?;
                """, (sub.id,))
                await ctx.send(f"All restricted words have been disabled for {sub.mention}.")
                logger.info(f"Restricted words disabled for user {sub.id} by {ctx.author.id}.")
            except Exception as e:
                await ctx.send("An error occurred while disabling restricted words.")
                logger.error(f"Error disabling restricted words for user {sub.id} by {ctx.author.id}: {e}")
        else:
            await ctx.send(f"{sub.mention} has no restricted words to enable.")
            logger.info(f"No restricted words to toggle for user {sub.id} by {ctx.author.id}.")

    @commands.group(
        name="sub-trusted",
        help="Manage trusted users for your subs.",
        usage="!sub-trusted [add/remove/clear] [@sub] [@user]",
    )
    async def sub_trusted(self, ctx: commands.Context) -> None:
        """
        Group command for managing sub's trusted users.

        :param ctx: The context of the command call.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("Available subcommands: add, remove, clear")
            logger.warning(f"Sub-trusted command invoked without subcommand by {ctx.author.id}.")

    @sub_trusted.command(
        name="add",
        help="Add a user to one of your sub's trusted users.",
        usage="!sub-trusted add [@sub] [@user]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def sub_trusted_add(self, ctx: commands.Context, sub: discord.Member, user: discord.Member) -> None:
        """
        Adds a trusted user to a sub.

        :param ctx: The context of the command call.
        :param sub: The sub to add a trusted user to.
        :param user: The user to add as trusted.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)
        await self.add_user_if_not_exists(user.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to add trusted user to a sub they do not own: {sub.id}")
            return
        
        # Check if user is already trusted
        trusted = await self.db_handler.fetchone("""
            SELECT * FROM trusted_users WHERE owner_id = ? AND trusted_user_id = ?;
        """, (ctx.author.id, user.id))
        if trusted:
            await ctx.send(f"{user.mention} is already a trusted user for {sub.mention}.")
            return
        
    # -------------------------------
    # sub_trusted Commands Continued
    # -------------------------------

    @sub_trusted.command(
        name="remove",
        help="Remove a user from one of your sub's trusted users.",
        usage="!sub-trusted remove [@sub] [@user]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def sub_trusted_remove(self, ctx: commands.Context, sub: discord.Member, user: discord.Member) -> None:
        """
        Removes a trusted user from a sub.

        :param ctx: The context of the command call.
        :param sub: The sub to remove a trusted user from.
        :param user: The user to remove as trusted.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)
        await self.add_user_if_not_exists(user.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to remove trusted user from a sub they do not own: {sub.id}")
            return

        try:
            # Delete from trusted_users table
            await self.db_handler.execute("""
                DELETE FROM trusted_users WHERE owner_id = ? AND trusted_user_id = ?;
            """, (ctx.author.id, user.id))
            await ctx.send(f"{user.mention} has been removed from trusted users for {sub.mention}.")
            logger.info(f"User {user.id} removed from trusted users for sub {sub.id} by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while removing the trusted user.")
            logger.error(f"Error removing trusted user {user.id} for sub {sub.id} by {ctx.author.id}: {e}")

    @sub_trusted.command(
        name="clear",
        help="Remove all trusted users from one of your subs.",
        usage="!sub-trusted clear [@sub]",
    )
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def sub_trusted_clear(self, ctx: commands.Context, sub: discord.Member) -> None:
        """
        Clears all trusted users from a sub.

        :param ctx: The context of the command call.
        :param sub: The sub to clear trusted users from.
        """
        await self.add_user_if_not_exists(ctx.author.id)
        await self.add_user_if_not_exists(sub.id)

        # Check ownership
        if not await self.is_owner(ctx.author.id, sub.id):
            await ctx.send("You do not own this sub.")
            logger.warning(f"User {ctx.author.id} attempted to clear trusted users from a sub they do not own: {sub.id}")
            return

        try:
            # Delete all trusted users for the sub's owner
            await self.db_handler.execute("""
                DELETE FROM trusted_users WHERE owner_id = ?;
            """, (ctx.author.id,))
            await ctx.send(f"All trusted users have been removed for {sub.mention}.")
            logger.info(f"All trusted users cleared for sub {sub.id} by {ctx.author.id}.")
        except Exception as e:
            await ctx.send("An error occurred while clearing trusted users.")
            logger.error(f"Error clearing trusted users for sub {sub.id} by {ctx.author.id}: {e}")

    # -------------------------------
    # Additional Commands
    # -------------------------------

    @commands.command(
        name="leave-server",
        help="Allows a user to leave the server and removes all their data.",
        usage="!leave-server",
    )
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def leave_server(self, ctx: commands.Context) -> None:
        """
        Allows a user to leave the server and removes all their data.

        :param ctx: The context of the command call.
        """
        user_id = ctx.author.id

        try:
            # Remove user from all contracts where they are a sub
            await self.db_handler.execute("""
                DELETE FROM contracts WHERE sub_id = ?;
            """, (user_id,))

            # Remove user from all contracts where they are an owner
            await self.db_handler.execute("""
                DELETE FROM contracts WHERE owner_id = ?;
            """, (user_id,))

            # Remove all tasks associated with the user
            await self.db_handler.execute("""
                DELETE FROM tasks WHERE user_id = ?;
            """, (user_id,))

            # Remove all rules associated with the user
            await self.db_handler.execute("""
                DELETE FROM rules WHERE user_id = ?;
            """, (user_id,))

            # Remove all restricted words
            await self.db_handler.execute("""
                DELETE FROM restricted_words WHERE user_id = ?;
            """, (user_id,))

            # Remove all trusted users
            await self.db_handler.execute("""
                DELETE FROM trusted_users WHERE owner_id = ? OR trusted_user_id = ?;
            """, (user_id, user_id))

            # Remove user from users table
            await self.db_handler.execute("""
                DELETE FROM users WHERE discord_id = ?;
            """, (user_id,))

            # Kick the user from the server
            try:
                await ctx.guild.kick(user=ctx.author, reason="User requested to leave and remove all data.")
                await ctx.send("You have been kicked from the server and all your data has been removed.")
                logger.info(f"User {user_id} left the server and data was removed.")
            except discord.Forbidden:
                await ctx.send("I do not have permission to kick you from the server.")
                logger.error(f"Permission denied when attempting to kick user {user_id}.")
            except Exception as e:
                await ctx.send("An error occurred while trying to kick you from the server.")
                logger.error(f"Error kicking user {user_id}: {e}")

        except Exception as e:
            await ctx.send("An error occurred while processing your request.")
            logger.error(f"Error processing leave-server for user {user_id}: {e}")

    # -------------------------------
    # Event Listeners
    # -------------------------------

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """
        Listens to messages and deletes them if they contain restricted words.
        Notifies the user if they use a restricted word.

        :param message: The message to check.
        """
        if message.author.bot or not message.guild:  # Ignore bots and DMs
            return

        # Ensure the message belongs to a guild where the cog is active
        if not self.client.get_cog("EternalSlaveCog"):
            return

        # Fetch restricted words for the user
        user_record = await self.get_user_profile(message.author.id)
        if not user_record:
            return

        restricted_words = user_record[9].split(',') if user_record[9] else []
        restricted_words = [word.strip().lower() for word in restricted_words]

        if restricted_words:
            message_content = message.content.lower()
            for word in restricted_words:
                if word in message_content:
                    try:
                        await message.delete()
                        await message.channel.send(f"{message.author.mention}, you used a restricted word: `{word}`")
                        logger.info(f"Deleted message containing restricted word '{word}' from user {message.author.id}.")
                        break
                    except discord.Forbidden:
                        logger.error(f"Failed to delete message from user {message.author.id} due to permissions.")
                    except Exception as e:
                        logger.error(f"Error deleting message from user {message.author.id}: {e}")
                        break

    # -------------------------------
    # Before and After Invoke Hooks
    # -------------------------------

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        """
        Called before any command in the cog is invoked.

        :param ctx: The context of the command call.
        """
        logger.debug(f"Command '{ctx.command}' invoked by {ctx.author.id}.")

    async def cog_after_invoke(self, ctx: commands.Context) -> None:
        """
        Called after any command in the cog is invoked.

        :param ctx: The context of the command call.
        """
        logger.debug(f"Command '{ctx.command}' completed for {ctx.author.id}.")

    # -------------------------------
    # Error Handling
    # -------------------------------

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """
        Handles errors for commands in this cog.

        :param ctx: The context of the command call.
        :param error: The exception raised.
        """
        if ctx.command and ctx.cog_name == "EternalSlaveCog":  # Restrict to this cog's commands
            if isinstance(error, commands.CommandOnCooldown):
                await ctx.send(f"This command is on cooldown. Please try again after {round(error.retry_after, 1)} seconds.")
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send("Missing required argument. Please check the command usage.")
            elif isinstance(error, commands.BadArgument):
                await ctx.send("Invalid argument type. Please check the command usage.")
            else:
                await ctx.send("An error occurred while processing the command.")
                logger.error(f"Unhandled error in EternalSlaveCog: {error}")

    # -------------------------------
    # Additional Features
    # -------------------------------

    @commands.command(
        name="leave-server",
        help="Allows a user to leave the server and removes all their data.",
        usage="!leave-server",
    )
    @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def leave_server(self, ctx: commands.Context) -> None:
        """
        Allows a user to leave the server and removes all their data.

        :param ctx: The context of the command call.
        """
        user_id = ctx.author.id

        try:
            # Remove user from all contracts where they are a sub
            await self.db_handler.execute("""
                DELETE FROM contracts WHERE sub_id = ?;
            """, (user_id,))

            # Remove user from all contracts where they are an owner
            await self.db_handler.execute("""
                DELETE FROM contracts WHERE owner_id = ?;
            """, (user_id,))

            # Remove all tasks associated with the user
            await self.db_handler.execute("""
                DELETE FROM tasks WHERE user_id = ?;
            """, (user_id,))

            # Remove all rules associated with the user
            await self.db_handler.execute("""
                DELETE FROM rules WHERE user_id = ?;
            """, (user_id,))

            # Remove all restricted words
            await self.db_handler.execute("""
                DELETE FROM restricted_words WHERE user_id = ?;
            """, (user_id,))

            # Remove all trusted users
            await self.db_handler.execute("""
                DELETE FROM trusted_users WHERE owner_id = ? OR trusted_user_id = ?;
            """, (user_id, user_id))

            # Remove user from users table
            await self.db_handler.execute("""
                DELETE FROM users WHERE discord_id = ?;
            """, (user_id,))

            # Kick the user from the server
            try:
                await ctx.guild.kick(user=ctx.author, reason="User requested to leave and remove all data.")
                await ctx.send("You have been kicked from the server and all your data has been removed.")
                logger.info(f"User {user_id} left the server and data was removed.")
            except discord.Forbidden:
                await ctx.send("I do not have permission to kick you from the server.")
                logger.error(f"Permission denied when attempting to kick user {user_id}.")
            except Exception as e:
                await ctx.send("An error occurred while trying to kick you from the server.")
                logger.error(f"Error kicking user {user_id}: {e}")

        except Exception as e:
            await ctx.send("An error occurred while processing your request.")
            logger.error(f"Error processing leave-server for user {user_id}: {e}")
    
# -------------------------------
# Cog Setup Function
# -------------------------------

async def setup(client: commands.Bot) -> None:
    """
    Loads the EternalSlaveCog.

    :param client: The instance of the Discord bot.
    """
    logger.info("Loading EternalSlaveCog...")
    db_handler = client.db_handler  # Access db_handler from the bot instance
    await client.add_cog(EternalSlaveCog(client, db_handler))
    logger.info("EternalSlaveCog has been loaded.")
