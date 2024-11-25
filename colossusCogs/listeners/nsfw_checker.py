# colossusCogs/listeners/nsfw_checker.py

"""
NSFW Content Checker for ColossusBot
-------------------------------------
This cog monitors messages and attachments within the server to detect and handle NSFW (Not Safe For Work) content.
When a user sends a message with an image or GIF attachment, the bot performs Optical Character Recognition (OCR) on the image 
to extract any text and checks it for NSFW words. If NSFW content is detected, the bot sends an alert to a designated staff channel.

Actions available to staff include reviewing the message, approving the deletion of the content, or ignoring the alert.
The bot also supports re-checking attachments if necessary.

Features:
- Detects NSFW content from image and GIF attachments.
- Uses OCR to extract text from images for NSFW word detection.
- Sends alerts to a staff channel for review.
- Allows staff reactions to take actions such as deleting the content or ignoring it.

Requirements:
- OCR.space API key for OCR functionality (loaded from environment variable "OCR_SPACE_API_KEY").
- Appropriate permissions for sending messages, managing reactions, and reading attachments in the server.
"""

import discord
from discord.ext import commands
import aiohttp
import asyncio
from typing import Optional, Union, List, Tuple
from handlers.database_handler import DatabaseHandler
from PIL import Image
import io
import re
from Flags.nsfw_words import nsfw_words
import os

class NSFWChecker(commands.Cog):
    """
    Cog to monitor and handle NSFW content in messages.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler):
        """
        Initializes the NSFWChecker cog.

        :param client: The Discord bot instance.
        :param db_handler: The DatabaseHandler instance.
        """
        self.client = client
        self.db_handler = db_handler
        self.nsfw_word_list = nsfw_words.nsfw_words
        self.OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY")
        print("NSFWChecker initialized.")

    async def on_message(self, message: discord.Message) -> None:
        """
        Listener for new messages. Checks attachments for NSFW content.

        :param message: The Discord message.
        """
        if message.author == self.client.user:
            return

        if message.attachments:
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif']):
                    image_data = await attachment.read()
                    if attachment.filename.lower().endswith('.gif'):
                        frames = self.extract_frames_from_gif(image_data)
                        for frame in frames:
                            resized_frame = self.resize_image_if_needed(frame)
                            extracted_text = await self.perform_ocr(resized_frame)
                            if any(keyword in extracted_text.lower() for keyword in self.nsfw_word_list):
                                await self.handle_nsfw_content(message, attachment, extracted_text)
                                break
                    else:
                        resized_image = self.resize_image_if_needed(image_data)
                        extracted_text = await self.perform_ocr(resized_image)
                        if any(keyword in extracted_text.lower() for keyword in self.nsfw_word_list):
                            await self.handle_nsfw_content(message, attachment, extracted_text)
                            break

    async def on_reaction(self, reaction: discord.Reaction, user: discord.User) -> None:
        """
        Listener for reaction additions. Handles actions based on reactions to NSFW alert messages.

        :param reaction: The reaction added.
        :param user: The user who added the reaction.
        """
        if user == self.client.user:
            return

        valid_reactions = ["✅", "❌", "⚠️", "🔇", "👢", "🔨"]
        if str(reaction.emoji) not in valid_reactions:
            return

        if user.bot:
            return

        alert_info = await self.db_handler.fetch_nsfw_alert_message(reaction.message.id)
        if alert_info:
            user_id, channel_id, guild_id = alert_info
            guild = self.client.get_guild(guild_id)
            if not guild:
                return
            target_user = guild.get_member(user_id)
            if not target_user:
                await self.db_handler.delete_nsfw_alert_message(reaction.message.id)
                return
            originating_channel = guild.get_channel(channel_id)
            if not originating_channel:
                return

            # Retrieve staff channel ID from the database
            config = await self.db_handler.get_config(guild_id)
            staff_forum_channel_id = config.get("staff_forum_channel_id")
            staff_thread_id = config.get("staff_thread_id")

            staff_channel = guild.get_channel(staff_forum_channel_id)
            if not staff_channel:
                return

            # Determine if staff_channel is a thread or a regular channel
            if isinstance(staff_channel, discord.Thread):
                staff_thread = staff_channel
            else:
                staff_thread = guild.get_channel(staff_thread_id) if staff_thread_id else None

            if str(reaction.emoji) == "✅":
                await self.check_attachments(reaction.message)
            elif str(reaction.emoji) == "❌":
                await reaction.message.reply("NSFW alert ignored.")
                await self.db_handler.delete_nsfw_alert_message(reaction.message.id)

    def extract_frames_from_gif(self, image_data: bytes) -> List[bytes]:
        """
        Extracts frames from a GIF image.

        :param image_data: Binary data of the GIF image.
        :return: List of binary data for each frame in PNG format.
        """
        frames = []
        with Image.open(io.BytesIO(image_data)) as img:
            for frame in range(img.n_frames):
                img.seek(frame)
                frame_data = io.BytesIO()
                img.save(frame_data, format="PNG")
                frames.append(frame_data.getvalue())
        return frames

    def resize_image_if_needed(self, image_data: bytes) -> bytes:
        """
        Resizes the image if its size exceeds 1MB.

        :param image_data: Binary data of the image.
        :return: Binary data of the resized image or original if no resizing needed.
        """
        if len(image_data) > 1024 * 1024:
            with Image.open(io.BytesIO(image_data)) as img:
                img.thumbnail((1024, 1024), Image.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                return buffer.getvalue()
        return image_data

    async def perform_ocr(self, image_data: bytes) -> str:
        """
        Performs OCR on the provided image data using the OCR.space API.

        :param image_data: Binary data of the image.
        :return: Extracted text from the image.
        """
        url = 'https://api.ocr.space/parse/image'
        data = aiohttp.FormData()
        data.add_field('file', image_data, filename='image.png', content_type='image/png')
        data.add_field('apikey', self.OCR_SPACE_API_KEY)
        data.add_field('language', 'eng')

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    parsed_results = result.get("ParsedResults")
                    if parsed_results and isinstance(parsed_results, list):
                        return parsed_results[0].get("ParsedText", "")
        return ""

    async def handle_nsfw_content(
        self,
        message: discord.Message,
        attachment: discord.Attachment,
        extracted_text: str,
        image_url: Optional[str] = None
    ) -> None:
        """
        Handles NSFW content by sending an alert to the staff channel and recording it in the database.

        :param message: The Discord message containing NSFW content.
        :param attachment: The attachment object of the message.
        :param extracted_text: Text extracted from the image via OCR.
        :param image_url: Optional URL of the image if available.
        """
        config = await self.db_handler.get_config(message.guild.id)
        if not config:
            return

        staff_forum_channel_id = config.get("staff_forum_channel_id")
        staff_thread_id = config.get("staff_thread_id")

        staff_channel = message.guild.get_channel(staff_forum_channel_id)
        if not staff_channel:
            return

        # Determine if staff_channel is a thread or a regular channel
        if isinstance(staff_channel, discord.Thread):
            staff_thread = staff_channel
        else:
            staff_thread = message.guild.get_channel(staff_thread_id) if staff_thread_id else None

        if not staff_thread:
            return

        embed = discord.Embed(
            title="NSFW Content Alert",
            description=f"NSFW content detected from {message.author.mention}. React with ✅ to delete the message and warn the user, or with ❌ to ignore.",
            color=discord.Color.red()
        )
        embed.add_field(name="Extracted Text", value=extracted_text or "No text extracted.", inline=False)
        embed.add_field(name="Origin", value=f"Guild: {message.guild.name}\nChannel: {message.channel.mention}", inline=False)
        embed.add_field(name="Message Link", value=message.jump_url, inline=False)
        if attachment:
            embed.set_image(url=attachment.url)
        elif image_url:
            embed.set_image(url=image_url)
        embed.set_footer(text=f"User ID: {message.author.id} | Message ID: {message.id}")

        alert_message = await staff_thread.send(embed=embed)
        await alert_message.add_reaction("✅")
        await alert_message.add_reaction("❌")

        await self.db_handler.insert_nsfw_alert_message(
            message_id=alert_message.id,
            user_id=message.author.id,
            channel_id=message.channel.id,
            guild_id=message.guild.id
        )

    async def check_attachments(self, alert_message: discord.Message) -> None:
        """
        Re-checks attachments in a message for NSFW content. This can be used after a staff member approves an alert.

        :param alert_message: The alert message reacted to.
        """
        # Assuming the original message link is in the embed's "Message Link" field
        if not alert_message.embeds:
            return
        embed = alert_message.embeds[0]
        message_link = embed.fields[2].value  # "Message Link" is the third field
        original_message_id = int(message_link.split('/')[-1])
        original_message = await alert_message.channel.fetch_message(original_message_id)
        if not original_message:
            return
        if not original_message.attachments:
            return
        attachment = original_message.attachments[0]
        extracted_text = embed.fields[0].value  # "Extracted Text" is the first field
        await self.handle_nsfw_content(original_message, attachment, extracted_text)

    async def take_action(
        self,
        user: discord.Member,
        staff_channel: Union[discord.Thread, discord.TextChannel],
        originating_channel: discord.abc.GuildChannel,
        staff_thread: Optional[discord.Thread]
    ) -> None:
        """
        Takes action against the user based on staff's decision.

        :param user: The user to take action against.
        :param staff_channel: The staff thread/channel where actions are discussed.
        :param originating_channel: The channel where the original message was sent.
        :param staff_thread: The staff thread object if staff_channel is a thread.
        """
        action_embed = discord.Embed(
            title="Take Action on NSFW Content",
            description=f"Choose an action to take against {user.mention}:",
            color=discord.Color.red()
        )
        action_embed.add_field(name="Available Actions", value="⚠️ Warn\n🔇 Mute\n👢 Kick\n🔨 Ban", inline=False)

        action_message = await staff_channel.send(embed=action_embed)
        for reaction in ["⚠️", "🔇", "👢", "🔨"]:
            await action_message.add_reaction(reaction)

        await self.db_handler.insert_nsfw_action_message(
            message_id=action_message.id,
            user_id=user.id,
            channel_id=originating_channel.id,
            guild_id=staff_channel.guild.id
        )

async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    """
    Sets up the NSFWChecker cog.

    :param client: The Discord bot instance.
    :param db_handler: The DatabaseHandler instance.
    """
    print("Setting up NSFWChecker cog...")
    cog = NSFWChecker(client, db_handler)
    await client.add_cog(cog)
    print("NSFWChecker cog loaded successfully.")
