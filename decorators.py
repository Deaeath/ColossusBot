# File: decorators.py

from discord.ext import commands
from typing import List

def with_roles(*roles: str):
    """
    Custom decorator to apply role-based permissions and assign a permissions attribute.

    :param roles: Roles required to execute the command.
    """
    def decorator(func):
        # Apply the has_any_role decorator
        func = commands.has_any_role(*roles)(func)
        # Assign permissions attribute
        func.permissions = list(roles)
        return func
    return decorator
