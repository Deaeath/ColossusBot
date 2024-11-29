# File: colossusCogs/autoresponder.py

import discord
from discord.ext import commands
import logging
from handlers.database_handler import DatabaseHandler
from typing import Optional

logger = logging.getLogger("ColossusBot")


class Autoresponder(commands.Cog):
    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler) -> None:
        self.client = client
        self.db_handler = db_handler
        logger.info("Autoresponder cog initialized.")

    async def add_autoresponse(self, ctx: commands.Context, trigger: str, response: str, channel: Optional[discord.TextChannel] = None) -> None:
        guild_id = ctx.guild.id
        channel_id = channel.id if channel else None
        autoresponse_id = await self.db_handler.insert_autoresponse(guild_id, trigger, response, channel_id)
        if autoresponse_id != -1:
            channel_info = f" in channel {channel.mention}" if channel else ""
            await ctx.send(f"✅ Autoresponse added with ID: `{autoresponse_id}` for trigger `{trigger}`{channel_info}.")
            logger.info(f"Added autoresponse ID {autoresponse_id} with trigger '{trigger}' in guild ID: {guild_id}, channel ID: {channel_id}.")
        else:
            await ctx.send("❌ Failed to add autoresponse. Please try again.")
            logger.error(f"Failed to add autoresponse with trigger '{trigger}' in guild ID: {guild_id}.")

    async def remove_autoresponse(self, ctx: commands.Context, autoresponse_id: int) -> None:
        guild_id = ctx.guild.id
        success = await self.db_handler.delete_autoresponse(guild_id, autoresponse_id)
        if success:
            await ctx.send(f"✅ Autoresponse with ID: `{autoresponse_id}` has been removed.")
            logger.info(f"Removed autoresponse ID {autoresponse_id} from guild ID: {guild_id}.")
        else:
            await ctx.send(f"❌ Failed to remove autoresponse with ID: `{autoresponse_id}`. It may not exist.")
            logger.warning(f"Failed to remove autoresponse ID {autoresponse_id} from guild ID: {guild_id}.")

    async def list_autoresponses(self, ctx: commands.Context) -> None:
        guild_id = ctx.guild.id
        autoresponses = await self.db_handler.fetch_autoresponses(guild_id)
        if not autoresponses:
            await ctx.send("ℹ️ No autoresponses have been set up in this server.")
            logger.info(f"No autoresponses found for guild ID: {guild_id}.")
            return

        embed = discord.Embed(title="📄 Autoresponses", color=discord.Color.blue())
        for autoresponse in autoresponses:
            channel_info = f"<#{autoresponse['channel_id']}>" if autoresponse.get("channel_id") else "Same Channel"
            embed.add_field(
                name=f"ID: {autoresponse['id']} | Trigger: `{autoresponse['trigger']}`",
                value=f"**Response:** {autoresponse['response']}\n**Channel:** {channel_info}",
                inline=False
            )

        await ctx.send(embed=embed)
        logger.info(f"Listed {len(autoresponses)} autoresponses for guild ID: {guild_id}.")

    async def handle_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if not message.guild:
            return

        guild_id = message.guild.id
        content = message.content.lower()

        autoresponses = await self.db_handler.fetch_autoresponses(guild_id)

        for autoresponse in autoresponses:
            trigger = autoresponse.get("trigger").lower()
            response = autoresponse.get("response")
            target_channel_id = autoresponse.get("channel_id")

            if trigger in content:
                try:
                    if target_channel_id:
                        target_channel = message.guild.get_channel(target_channel_id)
                        if target_channel and isinstance(target_channel, discord.TextChannel):
                            await target_channel.send(response)
                            logger.info(f"Sent autoresponse for trigger '{trigger}' to channel ID {target_channel_id} in guild ID: {guild_id}.")
                        else:
                            await message.channel.send(response)
                            logger.warning(f"Target channel ID {target_channel_id} invalid. Sent response in original channel.")
                    else:
                        await message.channel.send(response)
                        logger.info(f"Sent autoresponse for trigger '{trigger}' in channel ID {message.channel.id} of guild ID: {guild_id}.")
                except discord.HTTPException as e:
                    logger.error(f"Failed to send autoresponse: {e}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.handle_message(message)
        await self.client.process_commands(message)


async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    await client.add_cog(Autoresponder(client, db_handler))
    logger.info("Autoresponder cog loaded successfully.")
