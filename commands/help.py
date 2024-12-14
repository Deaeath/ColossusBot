# File: commands/help.py

"""
HelpCog: Custom Help Command
----------------------------
Provides a custom help command for the Discord bot.
"""

import logging
from typing import Optional
import discord
from discord.ext import commands

logger = logging.getLogger("HelpCog")


class HelpCog(commands.Cog):
    """
    A Cog for handling the custom help command.
    """

    def __init__(self, client: commands.Bot):
        """
        Initializes the HelpCog.

        :param client: The Discord client instance.
        """
        self.client = client
        # Remove the default help command to implement a custom one
        self.client.remove_command("help")
        logger.info("[HelpCog] HelpCog initialized.")

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context, *, word: Optional[str] = None):
        """
        Custom help command that provides information about available commands or details about a specific command.

        :param ctx: The context in which a command is being invoked.
        :param word: Optional; the specific command to get help for.
        """
        if word is None:
            embed = discord.Embed(
                title="Bot Commands",
                description="Here are the commands grouped by their parent cog:",
                color=0xeee657
            )

            # Sort cogs alphabetically by name
            sorted_cogs = sorted(self.client.cogs.items(), key=lambda cog: cog[0].lower())
            for cog_name, cog in sorted_cogs:
                commands_list = sorted(
                    cog.get_commands(),
                    key=lambda cmd: cmd.name.lower()
                )  # Sort commands alphabetically by name
                commands_info = []
                for cmd in commands_list:
                    if not cmd.hidden:
                        cmd_info = f"**{cmd.name}** - {cmd.help.partition('. Usage:')[0].strip()}"
                        if len(cmd_info) > 1024:
                            cmd_info = cmd_info[:1021] + '...'
                        commands_info.append(cmd_info)
                if commands_info:
                    commands_info_str = "\n".join(commands_info)
                    if len(commands_info_str) > 1024:
                        commands_info_chunks = [commands_info_str[i:i+1024] for i in range(0, len(commands_info_str), 1024)]
                        for chunk in commands_info_chunks:
                            embed.add_field(name=cog_name, value=chunk, inline=False)
                    else:
                        embed.add_field(name=cog_name, value=commands_info_str, inline=False)

            # Handle commands not attached to a cog (e.g., routed through a handler)
            no_cog_commands = [
                cmd for cmd in self.client.commands if cmd.cog is None and not cmd.hidden
            ]
            if no_cog_commands:
                no_cog_info = "\n".join(
                    [f"**{cmd.name}** - {cmd.help.partition('. Usage:')[0].strip()}" for cmd in no_cog_commands]
                )
                embed.add_field(name="Uncategorized Commands", value=no_cog_info, inline=False)

            await ctx.send(embed=embed)
            logger.info(f"[{self.__class__.__name__}.help_command] Displayed general help to {ctx.author}.")
        else:
            command = self.client.get_command(word)
            if command:
                embed = discord.Embed(
                    title=f"`{command.name.capitalize()}` Command",
                    color=0x22ee66
                )
                description = command.help.partition(". Usage:")[0] if command.help else "No description available."
                embed.add_field(name="**Description**", value=description, inline=False)

                usage = command.help.partition(". Usage: ")[2] if (cmd_help := command.help) and ". Usage:" in cmd_help else "No specific usage."
                embed.add_field(
                    name="**Usage**",
                    value=f"```\n{usage}\n```" if usage and usage != "No specific usage." else "No specific usage provided.",
                    inline=False
                )

                if command.aliases:
                    embed.add_field(name="**Aliases**", value=", ".join(command.aliases), inline=False)

                await ctx.send(embed=embed)
                logger.info(f"[{self.__class__.__name__}.help_command] Displayed help for command '{command.name}' to {ctx.author}.")
            else:
                await ctx.send(f"No information found for command: `{word}`")
                logger.warning(f"[{self.__class__.__name__}.help_command] No information found for command: {word} requested by {ctx.author}.")


async def setup(client: commands.Bot):
    """
    Asynchronously adds the HelpCog to the client.

    :param client: The Discord client instance.
    """
    logger.info("[HelpCog] Setting up HelpCog...")
    await client.add_cog(HelpCog(client))
    logger.info("[HelpCog] HelpCog successfully set up.")