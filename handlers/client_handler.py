import logging
from typing import Dict, Union, List
import discord
from discord.ext import commands
from config import BOT_PREFIX, DATABASE_CONFIG, OPENAI_API_KEY, GOOGLE_API_KEY, CX_ID
from handlers.database_handler import DatabaseHandler

logger = logging.getLogger("ClientHandler")

class ClientHandler:
    """
    Handles initialization and configuration of the Discord client.
    """

    def __init__(self) -> None:
        """
        Initializes the ClientHandler.
        """
        logger.info(f"[{self.__class__.__name__} Initializing ClientHandler...")
        self.intents = self._setup_intents()

        self.client = commands.Bot(
            command_prefix=self.dynamic_prefix,
            intents=self.intents,
            description="Your Bot Description Here"
        )
        self.console_buffer: List[str] = []  # Buffer to store console logs

        # The guild_prefixes dictionary will be populated from the database on startup
        self.client.guild_prefixes = {}

        logger.info(f"[{self.__class__.__name__} ClientHandler initialization complete.")

        # Register event listeners
        self._register_event_listeners()

    async def initialize_prefixes(self, db_handler: DatabaseHandler):
        """
        Loads guild prefixes from the database into memory.
        Should be called after the bot is ready and the DB is connected.
        """
        query = "SELECT guild_id, prefix FROM guild_prefixes"
        rows = await db_handler.fetchall(query)
        for row in rows:
            guild_id, prefix = row[0], row[1]
            self.client.guild_prefixes[guild_id] = prefix
        logger.info(f"Loaded {len(rows)} guild prefixes from the database.")

    def dynamic_prefix(self, bot: commands.Bot, message: discord.Message) -> Union[List[str], str]:
        """
        A prefix function that returns the mention prefix and the guild-specific prefix.
        If no custom prefix is set for the guild, it falls back to the default BOT_PREFIX.
        Mentions are always available as a prefix.
        """
        guild_id = message.guild.id if message.guild else None
        prefix = self.client.guild_prefixes.get(guild_id, BOT_PREFIX)
        return commands.when_mentioned_or(prefix)(bot, message)

    @staticmethod
    def _setup_intents() -> discord.Intents:
        """
        Configures Discord intents for the bot.

        :return: Configured intents object.
        """
        intents = discord.Intents.default()
        intents.messages = True
        intents.guilds = True
        intents.members = True
        intents.reactions = True
        # Enable message_content if needed
        intents.message_content = True
        logger.info(f"[{ClientHandler.__name__} Intents configured.")
        return intents

    def get_client(self) -> commands.Bot:
        """
        Returns the Discord client instance.

        :return: The bot client.
        """
        return self.client

    def get_database_config(self) -> Dict[str, str]:
        """
        Returns the database configuration.

        :return: Database configuration dictionary.
        """
        return DATABASE_CONFIG

    def _register_event_listeners(self):
        """
        Registers the necessary event listeners for the bot.
        """
        @self.client.event
        async def on_message(message: discord.Message):
            """
            Event listener for on_message. Sends a help message when the bot is mentioned with no other text.
            """
            if message.author.bot:
                return  # Ignore messages from bots

            # Check if the message is a bot mention with no other content
            if message.content.strip() == f"<@{self.client.user.id}>":
                guild_id = message.guild.id if message.guild else None
                prefix = self.client.guild_prefixes.get(guild_id, BOT_PREFIX)

                db_handler = DatabaseHandler(DATABASE_CONFIG)
                await db_handler.connect()

                guild_config = await db_handler.get_config(guild_id) if guild_id else None
                log_channel_id = guild_config.get("log_channel_id") if guild_config else "Not Configured"
                owner_id = guild_config.get("owner_id") if guild_config else "Not Configured"

                role_menus = await db_handler.fetchall("SELECT name, channel_id FROM reaction_role_menus WHERE guild_id = ?", (guild_id,)) if guild_id else []
                auto_responses = await db_handler.fetchall("SELECT trigger, response FROM autoresponses WHERE guild_id = ?", (guild_id,)) if guild_id else []
                alerts_count = await db_handler.fetchone("SELECT COUNT(*) FROM flagged_alert_messages WHERE guild_id = ?", (guild_id,)) if guild_id else (0,)
                active_tickets = await db_handler.fetchall("SELECT channel_id, created_at FROM ticket_channels WHERE guild_id = ?", (guild_id,)) if guild_id else []
                paused_tickets_count = await db_handler.fetchone("SELECT COUNT(*) FROM paused_tickets WHERE channel_id IN (SELECT channel_id FROM ticket_channels WHERE guild_id = ?)", (guild_id,)) if guild_id else (0,)

                embed = discord.Embed(
                    title="ColossusBot Help",
                    description="Hello! I am ColossusBot, your versatile Discord assistant. Here are some details to get you started:",
                    color=discord.Color.blue()
                )

                embed.add_field(
                    name="Key Features",
                    value=(
                        f"- **Help**: Use `@ColossusBot help` or `{prefix}help` for detailed commands.\n"
                        f"- **Custom Prefix**: Each server can set its own prefix. Default is `{BOT_PREFIX}`.\n"
                        "- **Advanced Features**: Check out moderation, alerts, and more!\n"
                        "- **Documentation**: Visit the README for more details."
                    ),
                    inline=False
                )

                embed.add_field(
                    name="Environment Info",
                    value=(
                        f"- **Default Prefix**: `{BOT_PREFIX}`\n"
                        f"- **Database Engine**: `{DATABASE_CONFIG.get('engine', 'sqlite')}`\n"
                        f"- **Database Host**: `{DATABASE_CONFIG.get('host', 'localhost')}`\n"
                        f"- **Google API Configured**: {'Yes' if GOOGLE_API_KEY and CX_ID else 'No'}\n"
                        f"- **OpenAI API Configured**: {'Yes' if OPENAI_API_KEY else 'No'}\n"
                        f"- **Connected Guilds**: {len(self.client.guilds)}"
                    ),
                    inline=False
                )

                embed.add_field(
                    name="Guild-Specific Info",
                    value=(
                        f"- **Log Channel**: <#{log_channel_id}>\n"
                        f"- **Owner ID**: {owner_id}\n"
                        f"- **Role Menus**: {len(role_menus)} menu(s) configured.\n"
                        f"- **Auto Responses**: {len(auto_responses)} response(s) configured.\n"
                        f"- **Active Alerts**: {alerts_count[0]} flagged alert(s) recorded.\n"
                        f"- **Active Tickets**: {len(active_tickets)} ticket(s) open.\n"
                        f"- **Paused Tickets**: {paused_tickets_count[0]} ticket(s) paused."
                    ) if guild_id else "This command was run in a DM or guild information is unavailable.",
                    inline=False
                )

                if role_menus:
                    embed.add_field(
                        name="Role Menus Details",
                        value="\n".join([f"- {name} in <#{channel_id}>" for name, channel_id in role_menus]),
                        inline=False
                    )

                if auto_responses:
                    embed.add_field(
                        name="Auto Responses Details",
                        value="\n".join([f"- Trigger: `{trigger}` | Response: {response}" for trigger, response in auto_responses]),
                        inline=False
                    )

                if active_tickets:
                    embed.add_field(
                        name="Active Tickets",
                        value="\n".join([f"- <#{channel_id}> | Created At: {created_at}" for channel_id, created_at in active_tickets]),
                        inline=False
                    )

                embed.set_footer(text="For more information, reach out to your server administrator or visit the project documentation.")

                await db_handler.close()
                await message.channel.send(embed=embed)

            # Process other commands
            await self.client.process_commands(message)
