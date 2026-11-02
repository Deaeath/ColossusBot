# File: decorators.py

from functools import wraps
from discord.ext import commands

def with_roles(*roles):
    """
    Custom decorator to restrict command access to users with specific roles.

    :param roles: Role names that are allowed to use the command.
    """
    def predicate(ctx):
        return any(role.name in roles for role in ctx.author.roles)
    
    def decorator(func):
        func.roles = roles  # Attach roles to the function for later extraction
        return commands.check(predicate)(func)
    return decorator
