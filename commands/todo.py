import discord
from discord.ext import commands
from typing import Optional, List


class Todo(commands.Cog):
    """
    A cog to manage a user's to-do list.
    """

    def __init__(self, client: commands.Bot, db_handler) -> None:
        self.client = client
        self.db_handler = db_handler

    @commands.command(name="todo")
    async def todo(self, ctx: commands.Context, action: Optional[str] = None, *, message: Optional[str] = None) -> None:
        """
        Manages the user's to-do list.

        Args:
            ctx: The command invocation context.
            action: The action to perform (add, remove, list).
            message: The message to add or remove.
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
        client: The bot instance.
    """
    await client.add_cog(Todo(client, client.db_handler))
