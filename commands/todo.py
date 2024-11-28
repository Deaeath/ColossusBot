# File: commands/todo.py

"""
Todo Command: Manage a Personal To-Do List
-------------------------------------------
A cog to manage a user's personal to-do list. Users can add, remove, and list items in their to-do list.
"""

import discord
from discord.ext import commands
from typing import Optional, List
from handlers.database_handler import DatabaseHandler
import logging

# Set up logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Todo(commands.Cog):
    """
    A cog that manages a user's to-do list, allowing actions such as adding, removing, and listing tasks.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler) -> None:
        """
        Initializes the Todo cog.

        Args:
            client (commands.Bot): The bot instance that will interact with Discord.
            db_handler: A database handler instance for managing the to-do list.
        """
        self.client = client
        self.db_handler = db_handler
        logging.info("Todo cog initialized.")

    @commands.command(name="todo",
                      help="Manage your to-do list by adding, removing, or listing items.",
                      usage="!todo <add|remove|list> [message]",)
    async def todo(self, ctx: commands.Context, action: Optional[str] = None, *, message: Optional[str] = None) -> None:
        """
        Manages the user's to-do list by allowing actions to add, remove, or list items.

        Args:
            ctx (commands.Context): The context of the command invocation.
            action (Optional[str]): The action to perform on the to-do list (`add`, `remove`, `list`).
            message (Optional[str]): The message to add or the index to remove.
        """
        if not action:
            await ctx.send("Usage: `!todo <add|remove|list> [message]`")
            return

        if action == "add":
            if not message:
                await ctx.send("Please provide a message to add.")
                return
            todo_list: List[str] = await self.db_handler.get_todo_list(ctx.author.id) or []
            todo_list.append(message)
            await self.db_handler.update_todo_list(ctx.author.id, todo_list)
            await ctx.send(f"Added to todo list: {message}")

        elif action == "remove":
            if not message or not message.isdigit():
                await ctx.send("Please provide the index of the item to remove.")
                return
            index = int(message) - 1
            todo_list: List[str] = await self.db_handler.get_todo_list(ctx.author.id) or []
            if 0 <= index < len(todo_list):
                removed = todo_list.pop(index)
                await self.db_handler.update_todo_list(ctx.author.id, todo_list)
                await ctx.send(f"Removed from todo list: {removed}")
            else:
                await ctx.send("Invalid index.")

        elif action == "list":
            todo_list: List[str] = await self.db_handler.get_todo_list(ctx.author.id) or []
            if not todo_list:
                await ctx.send("Your todo list is empty.")
            else:
                formatted_list = "\n".join(f"{idx + 1}. {item}" for idx, item in enumerate(todo_list))
                await ctx.send(f"Your Todo List:\n{formatted_list}")


async def setup(client: commands.Bot) -> None:
    """
    Loads the Todo cog.

    Args:
        client (commands.Bot): The bot instance.
    """
    db_handler = client.db_handler  # Shared DatabaseHandler instance
    await client.add_cog(Todo(client, client.db_handler))
    logging.info("Todo cog loaded successfully.")
