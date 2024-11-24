# colossusCogs/Commands/aichatbot.py

"""
AIChatbot: AI-Powered Discord Assistant
----------------------------------------
A Discord cog that interacts with users using OpenAI and supports moderation actions for administrators.
"""

import asyncio
import discord
from discord.ext import commands
from openai import OpenAI
import re
import logging
from handlers.database_handler import DatabaseHandler


class AIChatbot(commands.Cog):
    """
    A cog for AI-powered interaction and moderation.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler, openai_api_key: str):
        """
        Initializes the AIChatbot cog.

        :param client: The Discord client instance.
        :param db_handler: The DatabaseHandler instance.
        :param openai_api_key: The OpenAI API key for GPT interactions.
        """
        self.client = client
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.conversation_history = {}
        self.db_handler = db_handler
        self.logger = logging.getLogger("ColossusBot")
        self.logger.info("AIChatbot initialized and ready!")

    async def clear_chat_history(self, user_id: int):
        """
        Clears the conversation history for a specific user.

        :param user_id: The Discord ID of the user.
        """
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
            return True
        return False

    async def get_chat_history(self, user_id: int):
        """
        Retrieves the conversation history for a user.

        :param user_id: The Discord ID of the user.
        :return: The conversation history as a list of messages.
        """
        return self.conversation_history.get(user_id, [])

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Listener for new messages. Triggers AI chat interaction.

        :param message: The user's message.
        """
        # Prevent the bot from responding to its own messages
        if message.author == self.client.user:
            return

        # Trigger the AI chat if the message starts with the bot prefix
        if not message.content.startswith('!'):
            await self.chat(message)

    async def chat(self, message: discord.Message):
        """
        Handles AI interaction for a user's message.

        :param message: The user's message.
        """
        user_id = message.author.id
        guild_id = message.guild.id
        self.conversation_history.setdefault(user_id, [])

        # Fetch guild configuration from the database
        config = await self.db_handler.get_config(guild_id)
        if not config:
            self.logger.warning(f"No config found for guild {guild_id}.")
            return

        owner_id = config.get("owner_id")
        if owner_id is None:
            self.logger.warning(f"Owner ID not set for guild {guild_id}.")
            return

        is_admin = message.author.guild_permissions.administrator or user_id == owner_id
        is_owner = user_id == owner_id

        # Clean the message content by removing bot mentions and trimming whitespace
        clean_content = message.clean_content.replace(f"@{self.client.user.display_name}", "").strip()
        self.conversation_history[user_id].append({"role": "user", "content": clean_content})

        # Construct the system message for the AI
        system_message = (
            f"You are an AI assistant for a Discord server with moderation capabilities. "
            f"The user messaging you has ID {user_id}. "
            f"The bot owner has ID {owner_id}. "
            f"The user {'is' if is_admin else 'is not'} an administrator. "
            f"The user {'is' if is_owner else 'is not'} the owner. "
            f"Respond concisely and perform actions only if explicitly instructed by an administrator."
        )

        # Trim conversation history to the last 5 messages to manage token usage
        conversation = [{"role": "system", "content": system_message}] + self.conversation_history[user_id][-5:]

        try:
            # Send the conversation to OpenAI for a response
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=conversation,
                max_tokens=150,
                temperature=0.7,
            )

            ai_response = response.choices[0].message.content.strip()
            self.logger.info(f"AI Response: {ai_response}")

            # Check for moderation actions in the AI's response
            if is_admin or is_owner:
                action_match = re.search(r'\[(KICK|BAN|MUTE|WARN):@(\w+):(.+?)\]', ai_response, re.IGNORECASE)
                if action_match:
                    action, target_username, reason = action_match.groups()
                    await self.perform_moderation_action(message, action, target_username, reason)
                    ai_response = f"Moderation action performed: {action} on user {target_username} for: {reason}"

            # Replace "ping the owner" with an actual mention if present
            if "ping the owner" in ai_response.lower():
                ai_response = ai_response.replace("ping the owner", f"<@{owner_id}>")

            # Append the AI's response to the conversation history
            self.conversation_history[user_id].append({"role": "assistant", "content": ai_response})

            # Handle long responses by splitting them into multiple messages
            if len(ai_response) > 2000:
                pages = [ai_response[i:i + 1900] for i in range(0, len(ai_response), 1900)]
                for index, page in enumerate(pages, start=1):
                    await message.reply(f"Page {index}/{len(pages)}: {page}")
                    await asyncio.sleep(1)
            else:
                await message.reply(ai_response)

        except Exception as e:
            self.logger.error(f"Error during AI chat: {e}")
            await message.reply("I'm sorry, I'm having trouble thinking right now. Please try again later.")

    async def perform_moderation_action(self, message: discord.Message, action: str, target_username: str, reason: str):
        """
        Performs moderation actions based on AI instructions.

        :param message: The command message.
        :param action: The moderation action (KICK, BAN, MUTE, WARN).
        :param target_username: The target user's username.
        :param reason: The reason for the action.
        """
        guild = message.guild
        target_member = discord.utils.get(guild.members, name=target_username)

        if not target_member:
            await message.channel.send(f"Error: Could not find user with username {target_username}")
            return

        log_channel = discord.utils.get(guild.channels, name="mod-log")
        if not log_channel:
            try:
                log_channel = await guild.create_text_channel("mod-log")
            except discord.Forbidden:
                await message.channel.send("I don't have permission to create a 'mod-log' channel.")
                return

        try:
            if action.upper() == "KICK":
                await target_member.kick(reason=reason)
            elif action.upper() == "BAN":
                await target_member.ban(reason=reason)
            elif action.upper() == "MUTE":
                mute_role = discord.utils.get(guild.roles, name="Muted")
                if not mute_role:
                    mute_role = await guild.create_role(name="Muted")
                    for channel in guild.channels:
                        await channel.set_permissions(mute_role, send_messages=False, speak=False, add_reactions=False)
                await target_member.add_roles(mute_role, reason=reason)
            elif action.upper() == "WARN":
                await target_member.send(f"You have been warned for: {reason}")
            await log_channel.send(f"{target_member.mention} was {action.lower()}ed by {message.author.mention} for: {reason}")
            await message.channel.send(f"Action {action} executed on {target_member.mention} for: {reason}")
        except discord.Forbidden:
            await message.channel.send("I don't have permission to perform that action.")
        except Exception as e:
            self.logger.error(f"Error during moderation: {e}")
            await message.channel.send(f"An error occurred: {e}")


async def setup(client: commands.Bot, db_handler: DatabaseHandler):
    """
    Sets up the AIChatbot cog.

    :param client: The Discord bot instance.
    :param db_handler: The DatabaseHandler instance.
    """
    from config import OPENAI_API_KEY
    cog = AIChatbot(client, db_handler, OPENAI_API_KEY)
    await client.add_cog(cog)
    client.logger.info("AIChatbot cog loaded successfully.")
