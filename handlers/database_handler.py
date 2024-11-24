# handlers/database_handler.py

import aiosqlite
import aiomysql
import logging
from typing import Any, List, Optional, Tuple, Union, Dict

logger = logging.getLogger("ColossusBot")


class DatabaseHandler:
    """
    Handles database operations for ColossusBot with support for SQLite and MySQL.
    """

    def __init__(self, db_config: dict):
        """
        Initializes the DatabaseHandler.

        :param db_config: Dictionary containing database configuration.
                          Example for SQLite: {"engine": "sqlite", "database": "activeAlerts.db"}
                          Example for MySQL: {"engine": "mysql", "host": "localhost", "user": "root", "password": "", "database": "activeAlerts"}
        """
        self.db_config = db_config
        self.connection: Optional[Union[aiosqlite.Connection, aiomysql.Connection]] = None

    async def connect(self) -> None:
        """
        Establishes a connection to the database based on the configuration.
        """
        if self.db_config["engine"] == "sqlite":
            self.connection = await aiosqlite.connect(self.db_config["database"])
            logger.info("Connected to SQLite database.")
        elif self.db_config["engine"] == "mysql":
            self.connection = await aiomysql.connect(
                host=self.db_config["host"],
                user=self.db_config["user"],
                password=self.db_config["password"],
                db=self.db_config["database"],
            )
            logger.info("Connected to MySQL database.")
        else:
            raise ValueError(f"Unsupported database engine: {self.db_config['engine']}")

    async def setup(self) -> None:
        """
        Sets up the database by creating necessary tables and ensuring schema consistency.
        """
        # Define all table creation queries
        queries = [
            # Existing Tables
            """
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id INTEGER PRIMARY KEY,
                log_channel_id INTEGER,
                staff_forum_channel_id INTEGER,
                staff_thread_id INTEGER,
                owner_id INTEGER,
                single_user_repeat_threshold INTEGER DEFAULT 5,
                min_word_count INTEGER DEFAULT 5
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_config (
                user_id INTEGER PRIMARY KEY,
                preferred_language TEXT DEFAULT 'en',
                allow_notifications BOOLEAN DEFAULT TRUE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS channel_perms_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INT,
                channel_id INT,
                previous_state BOOLEAN,
                new_state BOOLEAN,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS moveBlacklist (
                guildID INT,
                channelID INT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS channelsBlacklist (
                guildID INT,
                channelID INT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS membersBlacklist (
                guildID INT,
                memberID INT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS activeTextChannels (
                guildID INT,
                channelID INT,
                categoryID INT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS activeVoiceChannels (
                guildID INT,
                channelID INT,
                categoryID INT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS active (
                guildID INT,
                categoryID INT,
                channelID INT,
                messages TEXT,
                timer TEXT,
                remove TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS categories_channels (
                guildID INT,
                categoryID INT,
                channelID INT,
                position INT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS pingME (
                guildID INT,
                channelID INT,
                memberID INT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS bannedCategories (
                guildID INT,
                categoryID INT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS servers (
                guildID INT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS shared_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                guild_id INT,
                message_content TEXT,
                user_id INT,
                message_id INT,
                timestamp INT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS repeated_message_alerts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                guild_id INT,
                message_content TEXT,
                staff_message_id INT,
                original_message_id INT,
                timestamp INT,
                shared_messages TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS warned_channels (
                channel_id INT PRIMARY KEY,
                last_warned TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS paused_tickets (
                channel_id INT PRIMARY KEY,
                paused_at TIMESTAMP
            )
            """,

            # Tables for FlaggedWordsAlert Cog
            """
            CREATE TABLE IF NOT EXISTS flagged_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                user_id INTEGER,
                message_id INTEGER,
                channel_id INTEGER,
                timestamp REAL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS flagged_alert_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS flagged_action_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER
            )
            """,

            # Tables for NSFWChecker Cog
            """
            CREATE TABLE IF NOT EXISTS nsfw_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                user_id INTEGER,
                message_id INTEGER,
                channel_id INTEGER,
                timestamp REAL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS nsfw_alert_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS nsfw_action_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER
            )
            """,

            # Tables for RepeatedMessageAlert Cog
            """
            CREATE TABLE IF NOT EXISTS repeated_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                user_id INTEGER,
                message_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER,
                timestamp REAL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS repeated_alert_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS repeated_action_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER
            )
            """,
        ]

        # Execute all table creation queries
        for query in queries:
            await self.execute(query)

        # Add owner_id column if it doesn't exist (Migration Step)
        await self.migrate_guild_config()

        logger.info("Database setup completed.")

    async def migrate_guild_config(self) -> None:
        """
        Migrates the guild_config table to include the owner_id column if it doesn't exist.
        """
        if self.db_config["engine"] == "sqlite":
            # SQLite: Check pragma table_info
            query = "PRAGMA table_info(guild_config)"
            result = await self.fetchall(query)
            columns = [row[1] for row in result]  # Column name is the second element
            if "owner_id" not in columns:
                try:
                    alter_query = "ALTER TABLE guild_config ADD COLUMN owner_id INTEGER"
                    await self.execute(alter_query)
                    logger.info("Migrated guild_config table: Added owner_id column.")
                except Exception as e:
                    logger.error(f"Failed to migrate guild_config table in SQLite: {e}")
        elif self.db_config["engine"] == "mysql":
            # MySQL: Check information_schema.columns
            query = """
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'guild_config'
            """
            # For MySQL, we need the database name
            db_name = self.db_config["database"]
            result = await self.fetchall(query, (db_name,))
            columns = [row[0] for row in result]  # Column name is the first element
            if "owner_id" not in columns:
                try:
                    alter_query = "ALTER TABLE guild_config ADD COLUMN owner_id INT"
                    await self.execute(alter_query)
                    logger.info("Migrated guild_config table: Added owner_id column.")
                except Exception as e:
                    logger.error(f"Failed to migrate guild_config table in MySQL: {e}")
        else:
            logger.warning("Migration for guild_config table is not implemented for this database engine.")

    async def execute(
        self,
        query: str,
        params: Optional[Tuple[Any, ...]] = None,
        fetch: Optional[str] = None
    ) -> Optional[Union[Tuple[Any, ...], List[Tuple[Any, ...]]]]:
        """
        Executes a query with optional parameters and fetch options.

        :param query: The SQL query to execute.
        :param params: Optional tuple of parameters for the query.
        :param fetch: Type of fetch operation ('one', 'all', or None).
        :return: Fetched data if requested; otherwise, None.
        """
        params = params or ()
        if self.db_config["engine"] == "sqlite":
            assert isinstance(self.connection, aiosqlite.Connection), "Connection is not aiosqlite.Connection"
            async with self.connection.execute(query, params) as cursor:
                await self.connection.commit()
                if fetch == "one":
                    return await cursor.fetchone()
                elif fetch == "all":
                    return await cursor.fetchall()
        elif self.db_config["engine"] == "mysql":
            assert isinstance(self.connection, aiomysql.Connection), "Connection is not aiomysql.Connection"
            async with self.connection.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                await self.connection.commit()
                if fetch == "one":
                    result = await cursor.fetchone()
                    if result:
                        return tuple(result.values())
                elif fetch == "all":
                    results = await cursor.fetchall()
                    return [tuple(row.values()) for row in results]
        return None

    async def fetchone(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Tuple[Any, ...]]:
        """
        Fetches a single result from a query.

        :param query: The SQL query to execute.
        :param params: Optional tuple of parameters for the query.
        :return: The first result row as a tuple, or None if no result.
        """
        return await self.execute(query, params, fetch="one")

    async def fetchall(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[List[Tuple[Any, ...]]]:
        """
        Fetches all results from a query.

        :param query: The SQL query to execute.
        :param params: Optional tuple of parameters for the query.
        :return: A list of result rows as tuples, or None if no results.
        """
        return await self.execute(query, params, fetch="all")

    async def close(self) -> None:
        """
        Closes the database connection.
        """
        if self.connection:
            if self.db_config["engine"] == "sqlite":
                await self.connection.close()
            elif self.db_config["engine"] == "mysql":
                self.connection.close()
            logger.info("Database connection closed.")

    # ==================== Guild Configuration Methods ====================

    async def set_config(
        self,
        guild_id: int,
        log_channel_id: Optional[int] = None,
        staff_forum_channel_id: Optional[int] = None,
        staff_thread_id: Optional[int] = None,
        owner_id: Optional[int] = None,
        single_user_repeat_threshold: Optional[int] = None,
        min_word_count: Optional[int] = None
    ) -> None:
        """
        Sets or updates the configuration for a guild.

        :param guild_id: ID of the guild.
        :param log_channel_id: ID of the log channel.
        :param staff_forum_channel_id: ID of the staff forum channel.
        :param staff_thread_id: ID of the staff thread (if any).
        :param owner_id: ID of the guild owner.
        :param single_user_repeat_threshold: Threshold for repeated messages per user.
        :param min_word_count: Minimum word count to consider a message.
        """
        # Check if the guild_config already exists
        existing = await self.fetchone(
            "SELECT guild_id FROM guild_config WHERE guild_id = ?",
            (guild_id,)
        )

        if existing:
            # Build the update query dynamically based on provided parameters
            updates = []
            params = []
            if log_channel_id is not None:
                updates.append("log_channel_id = ?")
                params.append(log_channel_id)
            if staff_forum_channel_id is not None:
                updates.append("staff_forum_channel_id = ?")
                params.append(staff_forum_channel_id)
            if staff_thread_id is not None:
                updates.append("staff_thread_id = ?")
                params.append(staff_thread_id)
            if owner_id is not None:
                updates.append("owner_id = ?")
                params.append(owner_id)
            if single_user_repeat_threshold is not None:
                updates.append("single_user_repeat_threshold = ?")
                params.append(single_user_repeat_threshold)
            if min_word_count is not None:
                updates.append("min_word_count = ?")
                params.append(min_word_count)

            if updates:
                params.append(guild_id)
                query = f"UPDATE guild_config SET {', '.join(updates)} WHERE guild_id = ?"
                await self.execute(query, tuple(params))
        else:
            # Insert new guild_config
            query = """
                INSERT INTO guild_config (
                    guild_id, log_channel_id, staff_forum_channel_id, staff_thread_id,
                    owner_id, single_user_repeat_threshold, min_word_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            await self.execute(
                query,
                (
                    guild_id,
                    log_channel_id,
                    staff_forum_channel_id,
                    staff_thread_id,
                    owner_id,
                    single_user_repeat_threshold or 5,
                    min_word_count or 5
                )
            )

    async def get_config(self, guild_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves configuration parameters for a guild.

        :param guild_id: ID of the guild.
        :return: Dictionary of configuration parameters or None if not found.
        """
        row = await self.fetchone(
            "SELECT * FROM guild_config WHERE guild_id = ?",
            (guild_id,)
        )
        if row:
            keys = [
                "guild_id", "log_channel_id", "staff_forum_channel_id",
                "staff_thread_id", "owner_id", "single_user_repeat_threshold", "min_word_count"
            ]
            return dict(zip(keys, row))
        return None

    # ==================== FlaggedWordsAlert Methods ====================

    async def setup_flagged_words_alert_database(self) -> None:
        """
        Sets up the database tables for the FlaggedWordsAlert cog.
        """
        queries = [
            """
            CREATE TABLE IF NOT EXISTS flagged_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                user_id INTEGER,
                message_id INTEGER,
                channel_id INTEGER,
                timestamp REAL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS flagged_alert_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS flagged_action_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER
            )
            """
        ]
        for query in queries:
            await self.execute(query)
        logger.info("FlaggedWordsAlert database setup completed.")

    async def insert_flagged_message(
        self,
        content: str,
        user_id: int,
        message_id: int,
        channel_id: int,
        timestamp: float
    ) -> None:
        """
        Inserts a flagged message into the database.

        :param content: The content of the message.
        :param user_id: ID of the user who sent the message.
        :param message_id: ID of the message.
        :param channel_id: ID of the channel where the message was sent.
        :param timestamp: Timestamp of when the message was sent.
        """
        query = """
            INSERT INTO flagged_messages (content, user_id, message_id, channel_id, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """
        await self.execute(query, (content, user_id, message_id, channel_id, timestamp))

    async def insert_flagged_alert_message(
        self,
        message_id: int,
        user_id: int,
        channel_id: int,
        guild_id: int
    ) -> None:
        """
        Inserts a flagged alert message into the database.

        :param message_id: ID of the alert message.
        :param user_id: ID of the user who triggered the alert.
        :param channel_id: ID of the channel where the alert was sent.
        :param guild_id: ID of the guild.
        """
        query = """
            INSERT INTO flagged_alert_messages (message_id, user_id, channel_id, guild_id)
            VALUES (?, ?, ?, ?)
        """
        await self.execute(query, (message_id, user_id, channel_id, guild_id))

    async def fetch_flagged_alert_message(
        self,
        message_id: int
    ) -> Optional[Tuple[int, int, int]]:
        """
        Fetches a flagged alert message by its message ID.

        :param message_id: ID of the alert message.
        :return: Tuple of (user_id, channel_id, guild_id) or None if not found.
        """
        query = "SELECT user_id, channel_id, guild_id FROM flagged_alert_messages WHERE message_id = ?"
        return await self.fetchone(query, (message_id,))

    async def delete_flagged_alert_message(
        self,
        message_id: int
    ) -> None:
        """
        Deletes a flagged alert message by its message ID.

        :param message_id: ID of the alert message.
        """
        query = "DELETE FROM flagged_alert_messages WHERE message_id = ?"
        await self.execute(query, (message_id,))

    async def insert_flagged_action_message(
        self,
        message_id: int,
        user_id: int,
        channel_id: int,
        guild_id: int
    ) -> None:
        """
        Inserts a flagged action message into the database.

        :param message_id: ID of the action message.
        :param user_id: ID of the user to take action against.
        :param channel_id: ID of the originating channel.
        :param guild_id: ID of the guild.
        """
        query = """
            INSERT INTO flagged_action_messages (message_id, user_id, channel_id, guild_id)
            VALUES (?, ?, ?, ?)
        """
        await self.execute(query, (message_id, user_id, channel_id, guild_id))

    async def fetch_flagged_action_message(
        self,
        message_id: int
    ) -> Optional[Tuple[int, int, int]]:
        """
        Fetches a flagged action message by its message ID.

        :param message_id: ID of the action message.
        :return: Tuple of (user_id, channel_id, guild_id) or None if not found.
        """
        query = "SELECT user_id, channel_id, guild_id FROM flagged_action_messages WHERE message_id = ?"
        return await self.fetchone(query, (message_id,))

    async def delete_flagged_action_message(
        self,
        message_id: int
    ) -> None:
        """
        Deletes a flagged action message by its message ID.

        :param message_id: ID of the action message.
        """
        query = "DELETE FROM flagged_action_messages WHERE message_id = ?"
        await self.execute(query, (message_id,))

    # ==================== NSFWChecker Methods ====================

    async def setup_nsfw_checker_database(self) -> None:
        """
        Sets up the database tables for the NSFWChecker cog.
        """
        queries = [
            """
            CREATE TABLE IF NOT EXISTS nsfw_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                user_id INTEGER,
                message_id INTEGER,
                channel_id INTEGER,
                timestamp REAL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS nsfw_alert_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS nsfw_action_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER
            )
            """
        ]
        for query in queries:
            await self.execute(query)
        logger.info("NSFWChecker database setup completed.")

    async def insert_nsfw_message(
        self,
        content: str,
        user_id: int,
        message_id: int,
        channel_id: int,
        timestamp: float
    ) -> None:
        """
        Inserts an NSFW message into the database.

        :param content: The content of the message.
        :param user_id: ID of the user who sent the message.
        :param message_id: ID of the message.
        :param channel_id: ID of the channel where the message was sent.
        :param timestamp: Timestamp of when the message was sent.
        """
        query = """
            INSERT INTO nsfw_messages (content, user_id, message_id, channel_id, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """
        await self.execute(query, (content, user_id, message_id, channel_id, timestamp))

    async def insert_nsfw_alert_message(
        self,
        message_id: int,
        user_id: int,
        channel_id: int,
        guild_id: int
    ) -> None:
        """
        Inserts an NSFW alert message into the database.

        :param message_id: ID of the alert message.
        :param user_id: ID of the user who triggered the alert.
        :param channel_id: ID of the channel where the alert was sent.
        :param guild_id: ID of the guild.
        """
        query = """
            INSERT INTO nsfw_alert_messages (message_id, user_id, channel_id, guild_id)
            VALUES (?, ?, ?, ?)
        """
        await self.execute(query, (message_id, user_id, channel_id, guild_id))

    async def fetch_nsfw_alert_message(
        self,
        message_id: int
    ) -> Optional[Tuple[int, int, int]]:
        """
        Fetches an NSFW alert message by its message ID.

        :param message_id: ID of the alert message.
        :return: Tuple of (user_id, channel_id, guild_id) or None if not found.
        """
        query = "SELECT user_id, channel_id, guild_id FROM nsfw_alert_messages WHERE message_id = ?"
        return await self.fetchone(query, (message_id,))

    async def delete_nsfw_alert_message(
        self,
        message_id: int
    ) -> None:
        """
        Deletes an NSFW alert message by its message ID.

        :param message_id: ID of the alert message.
        """
        query = "DELETE FROM nsfw_alert_messages WHERE message_id = ?"
        await self.execute(query, (message_id,))

    async def insert_nsfw_action_message(
        self,
        message_id: int,
        user_id: int,
        channel_id: int,
        guild_id: int
    ) -> None:
        """
        Inserts an NSFW action message into the database.

        :param message_id: ID of the action message.
        :param user_id: ID of the user to take action against.
        :param channel_id: ID of the originating channel.
        :param guild_id: ID of the guild.
        """
        query = """
            INSERT INTO nsfw_action_messages (message_id, user_id, channel_id, guild_id)
            VALUES (?, ?, ?, ?)
        """
        await self.execute(query, (message_id, user_id, channel_id, guild_id))

    async def fetch_nsfw_action_message(
        self,
        message_id: int
    ) -> Optional[Tuple[int, int, int]]:
        """
        Fetches an NSFW action message by its message ID.

        :param message_id: ID of the action message.
        :return: Tuple of (user_id, channel_id, guild_id) or None if not found.
        """
        query = "SELECT user_id, channel_id, guild_id FROM nsfw_action_messages WHERE message_id = ?"
        return await self.fetchone(query, (message_id,))

    async def delete_nsfw_action_message(
        self,
        message_id: int
    ) -> None:
        """
        Deletes an NSFW action message by its message ID.

        :param message_id: ID of the action message.
        """
        query = "DELETE FROM nsfw_action_messages WHERE message_id = ?"
        await self.execute(query, (message_id,))

    # ==================== RepeatedMessageAlert Methods ====================

    async def setup_repeated_message_alert_database(self) -> None:
        """
        Sets up the database tables for the RepeatedMessageAlert cog.
        """
        queries = [
            """
            CREATE TABLE IF NOT EXISTS repeated_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                user_id INTEGER,
                message_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER,
                timestamp REAL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS repeated_alert_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS repeated_action_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                guild_id INTEGER
            )
            """
        ]
        for query in queries:
            await self.execute(query)
        logger.info("RepeatedMessageAlert database setup completed.")

    async def insert_repeated_message(
        self,
        content: str,
        user_id: int,
        message_id: int,
        channel_id: int,
        guild_id: int,
        timestamp: float
    ) -> None:
        """
        Inserts a repeated message into the database.

        :param content: The content of the message.
        :param user_id: ID of the user who sent the message.
        :param message_id: ID of the message.
        :param channel_id: ID of the channel where the message was sent.
        :param guild_id: ID of the guild.
        :param timestamp: Timestamp of when the message was sent.
        """
        query = """
            INSERT INTO repeated_messages (content, user_id, message_id, channel_id, guild_id, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        await self.execute(query, (content, user_id, message_id, channel_id, guild_id, timestamp))

    async def insert_repeated_alert_message(
        self,
        message_id: int,
        user_id: int,
        channel_id: int,
        guild_id: int
    ) -> None:
        """
        Inserts a repeated alert message into the database.

        :param message_id: ID of the alert message.
        :param user_id: ID of the user who triggered the alert.
        :param channel_id: ID of the channel where the alert was sent.
        :param guild_id: ID of the guild.
        """
        query = """
            INSERT INTO repeated_alert_messages (message_id, user_id, channel_id, guild_id)
            VALUES (?, ?, ?, ?)
        """
        await self.execute(query, (message_id, user_id, channel_id, guild_id))

    async def fetch_repeated_alert_message(
        self,
        message_id: int
    ) -> Optional[Tuple[int, int, int]]:
        """
        Fetches a repeated alert message by its message ID.

        :param message_id: ID of the alert message.
        :return: Tuple of (user_id, channel_id, guild_id) or None if not found.
        """
        query = "SELECT user_id, channel_id, guild_id FROM repeated_alert_messages WHERE message_id = ?"
        return await self.fetchone(query, (message_id,))

    async def delete_repeated_alert_message(
        self,
        message_id: int
    ) -> None:
        """
        Deletes a repeated alert message by its message ID.

        :param message_id: ID of the alert message.
        """
        query = "DELETE FROM repeated_alert_messages WHERE message_id = ?"
        await self.execute(query, (message_id,))

    async def insert_repeated_action_message(
        self,
        message_id: int,
        user_id: int,
        channel_id: int,
        guild_id: int
    ) -> None:
        """
        Inserts a repeated action message into the database.

        :param message_id: ID of the action message.
        :param user_id: ID of the user to take action against.
        :param channel_id: ID of the originating channel.
        :param guild_id: ID of the guild.
        """
        query = """
            INSERT INTO repeated_action_messages (message_id, user_id, channel_id, guild_id)
            VALUES (?, ?, ?, ?)
        """
        await self.execute(query, (message_id, user_id, channel_id, guild_id))

    async def fetch_repeated_action_message(
        self,
        message_id: int
    ) -> Optional[Tuple[int, int, int]]:
        """
        Fetches a repeated action message by its message ID.

        :param message_id: ID of the action message.
        :return: Tuple of (user_id, channel_id, guild_id) or None if not found.
        """
        query = "SELECT user_id, channel_id, guild_id FROM repeated_action_messages WHERE message_id = ?"
        return await self.fetchone(query, (message_id,))

    async def delete_repeated_action_message(
        self,
        message_id: int
    ) -> None:
        """
        Deletes a repeated action message by its message ID.

        :param message_id: ID of the action message.
        """
        query = "DELETE FROM repeated_action_messages WHERE message_id = ?"
        await self.execute(query, (message_id,))

    async def delete_repeated_messages(
        self,
        message_ids: List[int]
    ) -> None:
        """
        Deletes repeated messages from the database.

        :param message_ids: List of message IDs to delete.
        """
        if not message_ids:
            return
        placeholders = ','.join(['?'] * len(message_ids))
        query = f"DELETE FROM repeated_messages WHERE message_id IN ({placeholders})"
        await self.execute(query, tuple(message_ids))
        logger.info("RepeatedMessageAlert: Deleted repeated messages from the database.")
