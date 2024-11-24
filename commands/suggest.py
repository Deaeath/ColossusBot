from discord.ext import commands
from discord import Embed, TextChannel, Member
from datetime import datetime
from typing import Optional
import random


class SuggestionCommands(commands.Cog):
    """
    A cog to handle suggestion-related commands such as setting the suggestion channel
    and submitting suggestions.
    """

    def __init__(self, client: commands.Bot, db_handler):
        self.client = client
        self.db_handler = db_handler

    @commands.command(aliases=["suggestion-channel"])
    @commands.has_any_role("owner", "head_staff")
    async def suggestion_channel(self, ctx: commands.Context, channel: Optional[TextChannel] = None):
        """
        Set or update the suggestion channel for the server.

        Args:
            ctx (commands.Context): The context in which the command was called.
            channel (Optional[TextChannel]): The text channel to be set as the suggestion channel.
        """
        if channel is None:
            embed = Embed(
                title="How to use this command?",
                description=f"`{ctx.prefix}suggestion_channel <#channel>`",
                color=random.randint(0, 0xFFFFFF),
            )
            await ctx.send(embed=embed)
            return

        suggestion_data = self.db_handler.child("suggestion").child(ctx.guild.id).get().val()

        if suggestion_data is None:
            # Set up the suggestion channel
            self.db_handler.child("suggestion").child(ctx.guild.id).update({"channel": channel.id})
            embed = Embed(
                description=f"Suggestion channel set to {channel.mention}",
                color=random.randint(0, 0xFFFFFF),
            )
        else:
            # Update the suggestion channel
            self.db_handler.child("suggestion").child(ctx.guild.id).update({"channel": channel.id})
            embed = Embed(
                description=f"Suggestion channel updated to {channel.mention}",
                color=random.randint(0, 0xFFFFFF),
            )

        await ctx.send(embed=embed)

    @commands.command()
    async def suggest(self, ctx: commands.Context, *, suggestion: Optional[str] = None):
        """
        Submit a suggestion to the configured suggestion channel.

        Args:
            ctx (commands.Context): The context in which the command was called.
            suggestion (Optional[str]): The content of the suggestion.
        """
        if suggestion is None:
            embed = Embed(
                title="How to use this command?",
                description=f"`{ctx.prefix}suggest <suggestion>`",
                color=random.randint(0, 0xFFFFFF),
            )
            await ctx.send(embed=embed)
            return

        suggestion_data = self.db_handler.child("suggestion").child(ctx.guild.id).get().val()
        if suggestion_data is None or "channel" not in suggestion_data:
            embed = Embed(
                description="A suggestion channel has not been configured.",
                color=random.randint(0, 0xFFFFFF),
            )
            await ctx.send(embed=embed)
            return

        channel_id = int(suggestion_data["channel"])
        suggestion_channel = self.client.get_channel(channel_id)
        if suggestion_channel is None:
            embed = Embed(
                description="The configured suggestion channel is invalid. Please update it.",
                color=random.randint(0, 0xFFFFFF),
            )
            await ctx.send(embed=embed)
            return

        suggestion_number = suggestion_data.get("number", 0) + 1

        # Create suggestion embed
        suggestion_embed = Embed(
            title=f"Suggestion #{suggestion_number}",
            description=suggestion,
            color=random.randint(0, 0xFFFFFF),
        )
        suggestion_embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        suggestion_embed.set_footer(text=f"User ID: {ctx.author.id}")
        suggestion_embed.timestamp = datetime.utcnow()

        # Send suggestion to the suggestion channel
        suggestion_message = await suggestion_channel.send(embed=suggestion_embed)
        await suggestion_message.add_reaction("⬆")
        await suggestion_message.add_reaction("⬇")

        # Update the suggestion count in the database
        self.db_handler.child("suggestion").child(ctx.guild.id).update({"number": suggestion_number})

        confirmation_embed = Embed(
            description="Your suggestion has been submitted successfully!",
            color=random.randint(0, 0xFFFFFF),
        )
        await ctx.send(embed=confirmation_embed)


async def setup(client: commands.Bot, db_handler):
    """
    Asynchronous setup function to add the cog to the bot.

    Args:
        client (commands.Bot): The bot instance.
        db_handler: The database handler instance.
    """
    await client.add_cog(SuggestionCommands(client, db_handler))
