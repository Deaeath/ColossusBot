# File: colossusCogs/reaction_role_menu.py

"""
Reaction Role Menu Cog for ColossusBot
---------------------------------------
This cog manages Reaction Role Menus, including creation, listing, editing, exporting,
importing, and deletion. It handles role assignments based on user reactions but does not
define any commands directly. Commands are routed through the CommandsHandler.
"""

import discord
from discord.ext import commands, tasks
import logging
import asyncio
import uuid
import json
import io
from handlers.database_handler import DatabaseHandler
from typing import Dict, Any, List, Optional

logger = logging.getLogger("ColossusBot")


class ReactionRoleMenu(commands.Cog):
    """
    Cog for managing Reaction Role Menus.

    This cog provides methods to create, list, edit, export, import, and delete reaction role menus.
    Commands and events are handled by the CommandsHandler and EventsHandler, respectively.
    """

    def __init__(self, client: commands.Bot, db_handler: DatabaseHandler) -> None:
        """
        Initializes the ReactionRoleMenu cog.

        :param client: The instance of the Discord bot.
        :param db_handler: Instance of the DatabaseHandler to interact with the database.
        """
        self.client = client
        self.db_handler = db_handler
        self.ensure_tables.start()

    def cog_unload(self):
        self.ensure_tables.cancel()

    @tasks.loop(count=1)
    async def ensure_tables(self):
        """
        Ensures that the necessary tables exist in the database.
        """
        try:
            await self.db_handler.create_table(
                "reaction_role_menus",
                """
                CREATE TABLE IF NOT EXISTS reaction_role_menus (
                    menu_id UUID PRIMARY KEY,
                    guild_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    message_id BIGINT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    emoji TEXT NOT NULL,
                    role_id BIGINT NOT NULL
                )
                """
            )
            logger.info("Ensured reaction_role_menus table exists.")
        except Exception as e:
            logger.error(f"Failed to ensure reaction_role_menus table: {e}")

    # Exposed Methods for CommandsHandler

    async def create_menu(self, ctx: commands.Context) -> None:
        """
        Creates a new Reaction Role Menu by guiding the user through the setup process.

        :param ctx: The command context.
        """
        try:
            await ctx.send("Please provide a name for the Reaction Role Menu. This helps in identifying the menu later.")

            def name_check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                name_msg = await self.client.wait_for('message', check=name_check, timeout=120)  # 2 minutes
                menu_name = name_msg.content.strip()
                if not menu_name:
                    await ctx.send("Menu name cannot be empty. Setup cancelled.")
                    return
            except asyncio.TimeoutError:
                await ctx.send("Setup timed out. Please try again.")
                return

            await ctx.send("Please send the message you'd like to use for the reaction role menu.")

            try:
                original_message = await self.client.wait_for('message', check=name_check, timeout=120)  # 2 minutes
            except asyncio.TimeoutError:
                await ctx.send("Setup timed out. Please try again.")
                return

            embed = discord.Embed(
                title=f"Reaction Role Setup: {menu_name}",
                description="React to this message with the emojis corresponding to the roles you want to assign.",
                color=discord.Color.blue()
            )
            setup_message = await ctx.send(embed=embed)

            await ctx.send("Please provide the emojis and roles in the format `emoji role`. Type `done` when finished.")

            emoji_role_mapping: Dict[str, int] = {}
            while True:
                try:
                    response = await self.client.wait_for('message', check=name_check, timeout=300)  # 5 minutes
                except asyncio.TimeoutError:
                    await ctx.send("Setup timed out. Please try again.")
                    return

                if response.content.lower() == 'done':
                    if not emoji_role_mapping:
                        await ctx.send("No emoji-role pairs were added. Setup cancelled.")
                        return
                    break

                parts = response.content.strip().split(maxsplit=1)
                if len(parts) < 2:
                    await ctx.send("Invalid format. Please use `emoji role`. Example: 😄 @Happy")
                    continue

                emoji, role_mention = parts
                role_id = self.extract_role_id(role_mention)
                if not role_id:
                    await ctx.send("Invalid role mention. Please try again.")
                    continue

                role = ctx.guild.get_role(role_id)
                if not role:
                    await ctx.send("Role not found. Please try again.")
                    continue

                if role in ctx.guild.roles and not role.is_assignable():
                    await ctx.send(f"Cannot assign the role `{role.name}` due to role hierarchy. Please choose a different role.")
                    continue

                if emoji in emoji_role_mapping:
                    await ctx.send(f"The emoji `{emoji}` is already assigned to a role. Please choose a different emoji.")
                    continue

                # Validate emoji
                if not self.is_valid_emoji(emoji, ctx.guild):
                    await ctx.send(f"The emoji `{emoji}` is invalid or not accessible by the bot. Please try a different emoji.")
                    continue

                emoji_role_mapping[emoji] = role.id

                try:
                    await setup_message.add_reaction(emoji)
                except discord.HTTPException:
                    await ctx.send(f"Failed to add reaction `{emoji}`. It might be an invalid emoji.")
                    del emoji_role_mapping[emoji]
                    continue

                await ctx.send(f"Added {emoji} for role {role.mention}.")

            # Assign a unique UUID to the menu
            menu_id = uuid.uuid4()

            # Optionally, collect a description for the menu
            await ctx.send("Would you like to add a description for this menu? Type your description or `skip` to continue without.")

            try:
                desc_msg = await self.client.wait_for('message', check=name_check, timeout=120)
                if desc_msg.content.lower() != 'skip':
                    menu_description = desc_msg.content.strip()
                else:
                    menu_description = ""
            except asyncio.TimeoutError:
                menu_description = ""

            # Store the mappings in the database
            try:
                async with self.db_handler.transaction():
                    for emoji, role_id in emoji_role_mapping.items():
                        await self.db_handler.insert_record(
                            "reaction_role_menus",
                            {
                                "menu_id": str(menu_id),
                                "guild_id": ctx.guild.id,
                                "channel_id": setup_message.channel.id,
                                "message_id": setup_message.id,
                                "name": menu_name,
                                "description": menu_description,
                                "emoji": emoji,
                                "role_id": role_id
                            }
                        )
            except Exception as e:
                logger.error(f"Failed to insert reaction role menu records: {e}")
                await ctx.send("An error occurred while saving the reaction role menu. Rolling back.")
                await self.db_handler.rollback()
                return

            await ctx.send(f"Reaction Role Menu `{menu_name}` created successfully with ID: `{menu_id}`.")
        except Exception as e:
            logger.error(f"Error in create_menu method: {e}", exc_info=True)
            await ctx.send("An error occurred while creating the reaction role menu.")

    async def list_menus(self, ctx: commands.Context) -> None:
        """
        Lists all Reaction Role Menus in the guild.

        :param ctx: The command context.
        """
        try:
            records = await self.db_handler.fetch_records(
                "reaction_role_menus",
                {"guild_id": ctx.guild.id}
            )
            if not records:
                await ctx.send("There are no reaction role menus in this server.")
                return

            # Organize records by menu_id
            menus: Dict[str, Dict[str, Any]] = {}
            for record in records:
                menu_id = record['menu_id']
                if menu_id not in menus:
                    menus[menu_id] = {
                        "name": record['name'],
                        "description": record['description'],
                        "channel_id": record['channel_id'],
                        "message_id": record['message_id'],
                        "reactions": []
                    }
                menus[menu_id]["reactions"].append({
                    "emoji": record['emoji'],
                    "role_id": record['role_id']
                })

            # Prepare embed pages
            embed_pages = []
            current_embed = discord.Embed(
                title="Reaction Role Menus",
                description="List of all reaction role menus in this server.",
                color=discord.Color.green()
            )
            field_count = 0
            for menu_id, data in menus.items():
                channel = ctx.guild.get_channel(data["channel_id"])
                if not channel:
                    message_link = f"Channel not found (ID: {data['channel_id']})"
                else:
                    try:
                        message = await channel.fetch_message(data["message_id"])
                        message_link = f"[Jump to message]({message.jump_url})"
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                        message_link = "Message not found."

                description = data["description"] or "No description provided."
                reactions = "\n".join([f"{reaction['emoji']} : <@&{reaction['role_id']}>" for reaction in data["reactions"]])
                field_value = f"**Channel:** {channel.mention if channel else 'Unknown'}\n" \
                              f"**Message:** {message_link}\n" \
                              f"**Description:** {description}\n" \
                              f"**Reactions:**\n{reactions}"

                current_embed.add_field(
                    name=f"Menu ID: {menu_id} | {data['name']}",
                    value=field_value,
                    inline=False
                )
                field_count += 1

                # Check if current_embed exceeds Discord's embed limits
                if field_count >= 25:  # Discord allows up to 25 fields per embed
                    embed_pages.append(current_embed)
                    current_embed = discord.Embed(
                        title="Reaction Role Menus (Continued)",
                        description="List of all reaction role menus in this server.",
                        color=discord.Color.green()
                    )
                    field_count = 0

            if field_count > 0:
                embed_pages.append(current_embed)

            # Send embeds with pagination if necessary
            if len(embed_pages) == 1:
                await ctx.send(embed=embed_pages[0])
            else:
                await self.paginate(ctx, embed_pages)

        except Exception as e:
            logger.error(f"Error in list_menus method: {e}", exc_info=True)
            await ctx.send("An error occurred while listing the reaction role menus.")

    async def edit_menu(self, ctx: commands.Context, menu_id: str) -> None:
        """
        Edits an existing Reaction Role Menu.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu to edit.
        """
        try:
            # Validate UUID format
            try:
                uuid_obj = uuid.UUID(menu_id)
            except ValueError:
                await ctx.send("Invalid `menu_id` format. Please provide a valid UUID.")
                return

            # Fetch existing menu records
            records = await self.db_handler.fetch_records(
                "reaction_role_menus",
                {"menu_id": menu_id, "guild_id": ctx.guild.id}
            )
            if not records:
                await ctx.send(f"No reaction role menu found with ID `{menu_id}`.")
                return

            # Organize menu details
            menu_details: Dict[str, Any] = {
                "name": records[0]['name'],
                "description": records[0]['description'],
                "channel_id": records[0]['channel_id'],
                "message_id": records[0]['message_id'],
                "reactions": {record['emoji']: record['role_id'] for record in records}
            }

            await ctx.send(f"Editing Reaction Role Menu `{menu_details['name']}`. Choose an option:\n"
                           f"1. Add Reaction\n"
                           f"2. Remove Reaction\n"
                           f"3. Update Reaction\n"
                           f"4. Rename Menu\n"
                           f"5. Update Description\n"
                           f"6. Finish Editing")

            def option_check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= 6

            try:
                option_msg = await self.client.wait_for('message', check=option_check, timeout=120)  # 2 minutes
                option = int(option_msg.content)
            except asyncio.TimeoutError:
                await ctx.send("Edit menu timed out.")
                return

            if option == 1:
                await self.handle_add_reaction(ctx, menu_id, menu_details)
            elif option == 2:
                await self.handle_remove_reaction(ctx, menu_id, menu_details)
            elif option == 3:
                await self.handle_update_reaction(ctx, menu_id, menu_details)
            elif option == 4:
                await self.handle_rename_menu(ctx, menu_id, menu_details)
            elif option == 5:
                await self.handle_description_menu(ctx, menu_id, menu_details)
            elif option == 6:
                await ctx.send("Finished editing the Reaction Role Menu.")

        except Exception as e:
            logger.error(f"Error in edit_menu method: {e}", exc_info=True)
            await ctx.send("An error occurred while editing the reaction role menu.")

    async def export_menu(self, ctx: commands.Context, menu_id: str) -> None:
        """
        Exports a Reaction Role Menu to a JSON file.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu to export.
        """
        try:
            # Validate UUID format
            try:
                uuid_obj = uuid.UUID(menu_id)
            except ValueError:
                await ctx.send("Invalid `menu_id` format. Please provide a valid UUID.")
                return

            # Fetch menu records
            records = await self.db_handler.fetch_records(
                "reaction_role_menus",
                {"menu_id": menu_id, "guild_id": ctx.guild.id}
            )
            if not records:
                await ctx.send(f"No reaction role menu found with ID `{menu_id}`.")
                return

            # Organize menu data
            menu_data = {
                "menu_id": menu_id,
                "name": records[0]['name'],
                "description": records[0]['description'],
                "guild_id": records[0]['guild_id'],
                "channel_id": records[0]['channel_id'],
                "message_id": records[0]['message_id'],
                "reactions": {record['emoji']: record['role_id'] for record in records}
            }

            # Convert to JSON
            json_data = json.dumps(menu_data, indent=4)
            json_bytes = json_data.encode()

            # Create a file-like object
            file = discord.File(io.BytesIO(json_bytes), filename=f"reaction_role_menu_{menu_id}.json")

            await ctx.send(f"Here is the exported JSON for Reaction Role Menu `{menu_data['name']}`:", file=file)

        except Exception as e:
            logger.error(f"Error in export_menu method: {e}", exc_info=True)
            await ctx.send("An error occurred while exporting the reaction role menu.")

    async def import_menu(self, ctx: commands.Context) -> None:
        """
        Imports a Reaction Role Menu from a JSON file.

        :param ctx: The command context.
        """
        import io  # Ensure import is available

        try:
            await ctx.send("Please upload the JSON file containing the Reaction Role Menu to import.")

            def file_check(m):
                return m.author == ctx.author and m.channel == ctx.channel and len(m.attachments) > 0

            try:
                message = await self.client.wait_for('message', check=file_check, timeout=300)  # 5 minutes
                attachment = message.attachments[0]
                if not attachment.filename.endswith('.json'):
                    await ctx.send("Invalid file format. Please upload a `.json` file.")
                    return

                json_bytes = await attachment.read()
                menu_data = json.loads(json_bytes.decode())
            except asyncio.TimeoutError:
                await ctx.send("Import timed out. Please try again.")
                return
            except json.JSONDecodeError:
                await ctx.send("Failed to decode JSON. Please ensure the file is a valid JSON.")
                return

            # Validate required fields
            required_fields = ["menu_id", "name", "guild_id", "channel_id", "message_id", "reactions"]
            if not all(field in menu_data for field in required_fields):
                await ctx.send("JSON is missing required fields. Please check the file and try again.")
                return

            # Ensure the menu is being imported into the correct guild
            if menu_data["guild_id"] != ctx.guild.id:
                await ctx.send("This menu is intended for a different server. Cannot import.")
                return

            # Validate roles and emojis
            for emoji, role_id in menu_data["reactions"].items():
                role = ctx.guild.get_role(role_id)
                if not role:
                    await ctx.send(f"Role with ID `{role_id}` not found. Import aborted.")
                    return
                if not self.is_valid_emoji(emoji, ctx.guild):
                    await ctx.send(f"The emoji `{emoji}` is invalid or not accessible by the bot. Import aborted.")
                    return

            # Assign a new UUID for the imported menu to avoid conflicts
            new_menu_id = uuid.uuid4()

            # Insert records into the database
            try:
                async with self.db_handler.transaction():
                    for emoji, role_id in menu_data["reactions"].items():
                        await self.db_handler.insert_record(
                            "reaction_role_menus",
                            {
                                "menu_id": str(new_menu_id),
                                "guild_id": ctx.guild.id,
                                "channel_id": menu_data["channel_id"],
                                "message_id": menu_data["message_id"],
                                "name": menu_data["name"],
                                "description": menu_data.get("description", ""),
                                "emoji": emoji,
                                "role_id": role_id
                            }
                        )
            except Exception as e:
                logger.error(f"Failed to insert imported reaction role menu records: {e}")
                await ctx.send("An error occurred while importing the reaction role menu. Rolling back.")
                await self.db_handler.rollback()
                return

            await ctx.send(f"Reaction Role Menu `{menu_data['name']}` imported successfully with new ID: `{new_menu_id}`.")

        except Exception as e:
            logger.error(f"Error in import_menu method: {e}", exc_info=True)
            await ctx.send("An unexpected error occurred while importing the reaction role menu.")

    async def delete_menu(self, ctx: commands.Context, menu_id: str) -> None:
        """
        Deletes a specific Reaction Role Menu.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu to delete.
        """
        try:
            # Validate UUID format
            try:
                uuid_obj = uuid.UUID(menu_id)
            except ValueError:
                await ctx.send("Invalid `menu_id` format. Please provide a valid UUID.")
                return

            # Fetch existing menu records
            records = await self.db_handler.fetch_records(
                "reaction_role_menus",
                {"menu_id": menu_id, "guild_id": ctx.guild.id}
            )
            if not records:
                await ctx.send(f"No reaction role menu found with ID `{menu_id}`.")
                return

            # Confirm deletion
            await ctx.send(f"Are you sure you want to delete the Reaction Role Menu `{records[0]['name']}`? Type `yes` to confirm.")

            def confirm_check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'yes'

            try:
                confirmation = await self.client.wait_for('message', check=confirm_check, timeout=60)  # 1 minute
            except asyncio.TimeoutError:
                await ctx.send("Deletion timed out. Menu was not deleted.")
                return

            # Fetch unique message details to remove reactions if possible
            unique_messages = {}
            for record in records:
                key = (record['channel_id'], record['message_id'])
                if key not in unique_messages:
                    unique_messages[key] = []
                unique_messages[key].append(record['emoji'])

            # Attempt to remove reactions from the message
            for (channel_id, message_id), emojis in unique_messages.items():
                channel = ctx.guild.get_channel(channel_id)
                if not channel:
                    continue
                try:
                    message = await channel.fetch_message(message_id)
                    for emoji in emojis:
                        try:
                            await message.clear_reaction(emoji)
                        except discord.HTTPException:
                            logger.warning(f"Failed to remove reaction {emoji} from message {message_id}.")
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    logger.warning(f"Message {message_id} not found or inaccessible in channel {channel_id}.")

            # Delete all entries with the given menu_id
            await self.db_handler.delete_records(
                "reaction_role_menus",
                {"menu_id": menu_id, "guild_id": ctx.guild.id}
            )

            await ctx.send(f"Reaction Role Menu `{menu_id}` has been deleted.")

        except Exception as e:
            logger.error(f"Error in delete_menu method: {e}", exc_info=True)
            await ctx.send("An error occurred while deleting the reaction role menu.")

    async def edit_menu(self, ctx: commands.Context, menu_id: str) -> None:
        """
        Edits an existing Reaction Role Menu.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu to edit.
        """
        try:
            # Validate UUID format
            try:
                uuid_obj = uuid.UUID(menu_id)
            except ValueError:
                await ctx.send("Invalid `menu_id` format. Please provide a valid UUID.")
                return

            # Fetch existing menu records
            records = await self.db_handler.fetch_records(
                "reaction_role_menus",
                {"menu_id": menu_id, "guild_id": ctx.guild.id}
            )
            if not records:
                await ctx.send(f"No reaction role menu found with ID `{menu_id}`.")
                return

            # Organize menu details
            menu_details: Dict[str, Any] = {
                "name": records[0]['name'],
                "description": records[0]['description'],
                "channel_id": records[0]['channel_id'],
                "message_id": records[0]['message_id'],
                "reactions": {record['emoji']: record['role_id'] for record in records}
            }

            await ctx.send(f"Editing Reaction Role Menu `{menu_details['name']}`. Choose an option:\n"
                           f"1. Add Reaction\n"
                           f"2. Remove Reaction\n"
                           f"3. Update Reaction\n"
                           f"4. Rename Menu\n"
                           f"5. Update Description\n"
                           f"6. Finish Editing")

            def option_check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit() and 1 <= int(m.content) <= 6

            try:
                option_msg = await self.client.wait_for('message', check=option_check, timeout=120)  # 2 minutes
                option = int(option_msg.content)
            except asyncio.TimeoutError:
                await ctx.send("Edit menu timed out.")
                return

            if option == 1:
                await self.handle_add_reaction(ctx, menu_id, menu_details)
            elif option == 2:
                await self.handle_remove_reaction(ctx, menu_id, menu_details)
            elif option == 3:
                await self.handle_update_reaction(ctx, menu_id, menu_details)
            elif option == 4:
                await self.handle_rename_menu(ctx, menu_id, menu_details)
            elif option == 5:
                await self.handle_description_menu(ctx, menu_id, menu_details)
            elif option == 6:
                await ctx.send("Finished editing the Reaction Role Menu.")

        except Exception as e:
            logger.error(f"Error in edit_menu method: {e}", exc_info=True)
            await ctx.send("An error occurred while editing the reaction role menu.")

    async def handle_add_reaction(self, ctx: commands.Context, menu_id: str, menu_details: Dict[str, Any]):
        """
        Handles adding a new emoji-role pair to an existing menu.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu.
        :param menu_details: The details of the menu.
        """
        await ctx.send("Please provide the emoji and role in the format `emoji role`. Example: 😄 @Happy")

        def add_check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            response = await self.client.wait_for('message', check=add_check, timeout=120)  # 2 minutes
            parts = response.content.strip().split(maxsplit=1)
            if len(parts) < 2:
                await ctx.send("Invalid format. Please use `emoji role`. Example: 😄 @Happy")
                return

            emoji, role_mention = parts
            role_id = self.extract_role_id(role_mention)
            if not role_id:
                await ctx.send("Invalid role mention. Please try again.")
                return

            role = ctx.guild.get_role(role_id)
            if not role:
                await ctx.send("Role not found. Please try again.")
                return

            if role in ctx.guild.roles and not role.is_assignable():
                await ctx.send(f"Cannot assign the role `{role.name}` due to role hierarchy. Please choose a different role.")
                return

            if emoji in menu_details["reactions"]:
                await ctx.send(f"The emoji `{emoji}` is already assigned to a role. Please choose a different emoji.")
                return

            if not self.is_valid_emoji(emoji, ctx.guild):
                await ctx.send(f"The emoji `{emoji}` is invalid or not accessible by the bot. Please try a different emoji.")
                return

            try:
                channel = ctx.guild.get_channel(menu_details["channel_id"])
                message = await channel.fetch_message(menu_details["message_id"])
                await message.add_reaction(emoji)
            except discord.HTTPException:
                await ctx.send(f"Failed to add reaction `{emoji}` to the message.")
                return

            # Insert into database
            await self.db_handler.insert_record(
                "reaction_role_menus",
                {
                    "menu_id": menu_id,
                    "guild_id": ctx.guild.id,
                    "channel_id": menu_details["channel_id"],
                    "message_id": menu_details["message_id"],
                    "name": menu_details["name"],
                    "description": menu_details["description"],
                    "emoji": emoji,
                    "role_id": role_id
                }
            )

            # Update in-memory data
            menu_details["reactions"][emoji] = role_id

            await ctx.send(f"Added `{emoji}` for role {role.mention} to the menu.")

        except asyncio.TimeoutError:
            await ctx.send("Add reaction timed out.")
        except Exception as e:
            logger.error(f"Error in handle_add_reaction: {e}", exc_info=True)
            await ctx.send("An error occurred while adding the reaction.")

    async def handle_remove_reaction(self, ctx: commands.Context, menu_id: str, menu_details: Dict[str, Any]):
        """
        Handles removing an existing emoji-role pair from a menu.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu.
        :param menu_details: The details of the menu.
        """
        await ctx.send("Please provide the emoji you want to remove from the menu.")

        def remove_check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            response = await self.client.wait_for('message', check=remove_check, timeout=120)  # 2 minutes
            emoji = response.content.strip()

            if emoji not in menu_details["reactions"]:
                await ctx.send(f"The emoji `{emoji}` is not part of this menu.")
                return

            role_id = menu_details["reactions"][emoji]
            role = ctx.guild.get_role(role_id)
            if role:
                # Remove the reaction from the message
                try:
                    channel = ctx.guild.get_channel(menu_details["channel_id"])
                    message = await channel.fetch_message(menu_details["message_id"])
                    await message.clear_reaction(emoji)
                except discord.HTTPException:
                    await ctx.send(f"Failed to remove reaction `{emoji}` from the message.")
                    return

            # Delete from database
            await self.db_handler.delete_records(
                "reaction_role_menus",
                {"menu_id": menu_id, "emoji": emoji, "guild_id": ctx.guild.id}
            )

            # Update in-memory data
            del menu_details["reactions"][emoji]

            await ctx.send(f"Removed `{emoji}` from the menu.")

        except asyncio.TimeoutError:
            await ctx.send("Remove reaction timed out.")
        except Exception as e:
            logger.error(f"Error in handle_remove_reaction: {e}", exc_info=True)
            await ctx.send("An error occurred while removing the reaction.")

    async def handle_update_reaction(self, ctx: commands.Context, menu_id: str, menu_details: Dict[str, Any]):
        """
        Handles updating an existing emoji-role pair in a menu.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu.
        :param menu_details: The details of the menu.
        """
        await ctx.send("Please provide the emoji you want to update and the new role in the format `emoji new_role`. Example: 😄 @Joyful")

        def update_check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            response = await self.client.wait_for('message', check=update_check, timeout=120)  # 2 minutes
            parts = response.content.strip().split(maxsplit=1)
            if len(parts) < 2:
                await ctx.send("Invalid format. Please use `emoji new_role`. Example: 😄 @Joyful")
                return

            emoji, new_role_mention = parts
            if emoji not in menu_details["reactions"]:
                await ctx.send(f"The emoji `{emoji}` is not part of this menu.")
                return

            new_role_id = self.extract_role_id(new_role_mention)
            if not new_role_id:
                await ctx.send("Invalid role mention. Please try again.")
                return

            new_role = ctx.guild.get_role(new_role_id)
            if not new_role:
                await ctx.send("Role not found. Please try again.")
                return

            if new_role in ctx.guild.roles and not new_role.is_assignable():
                await ctx.send(f"Cannot assign the role `{new_role.name}` due to role hierarchy. Please choose a different role.")
                return

            if new_role_id in menu_details["reactions"].values():
                await ctx.send("This role is already assigned to another emoji in the menu.")
                return

            # Update in database
            await self.db_handler.update_record(
                "reaction_role_menus",
                {"role_id": new_role_id},
                {"menu_id": menu_id, "emoji": emoji, "guild_id": ctx.guild.id}
            )

            # Update in-memory data
            menu_details["reactions"][emoji] = new_role_id

            await ctx.send(f"Updated `{emoji}` to assign role {new_role.mention}.")

        except asyncio.TimeoutError:
            await ctx.send("Update reaction timed out.")
        except Exception as e:
            logger.error(f"Error in handle_update_reaction: {e}", exc_info=True)
            await ctx.send("An error occurred while updating the reaction.")

    async def handle_rename_menu(self, ctx: commands.Context, menu_id: str, menu_details: Dict[str, Any]):
        """
        Handles renaming a reaction role menu.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu.
        :param menu_details: The details of the menu.
        """
        await ctx.send("Please provide the new name for the Reaction Role Menu.")

        def rename_check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            response = await self.client.wait_for('message', check=rename_check, timeout=120)  # 2 minutes
            new_name = response.content.strip()
            if not new_name:
                await ctx.send("Menu name cannot be empty. Rename cancelled.")
                return

            # Update in database
            await self.db_handler.update_record(
                "reaction_role_menus",
                {"name": new_name},
                {"menu_id": menu_id, "guild_id": ctx.guild.id}
            )

            # Update in-memory data
            menu_details["name"] = new_name

            await ctx.send(f"Reaction Role Menu renamed to `{new_name}`.")

        except asyncio.TimeoutError:
            await ctx.send("Rename timed out.")
        except Exception as e:
            logger.error(f"Error in handle_rename_menu: {e}", exc_info=True)
            await ctx.send("An error occurred while renaming the menu.")

    async def handle_description_menu(self, ctx: commands.Context, menu_id: str, menu_details: Dict[str, Any]):
        """
        Handles updating the description of a reaction role menu.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu.
        :param menu_details: The details of the menu.
        """
        await ctx.send("Please provide the new description for the Reaction Role Menu. Type `clear` to remove the description.")

        def desc_check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            response = await self.client.wait_for('message', check=desc_check, timeout=120)  # 2 minutes
            if response.content.lower() == 'clear':
                new_description = ""
            else:
                new_description = response.content.strip()

            # Update in database
            await self.db_handler.update_record(
                "reaction_role_menus",
                {"description": new_description},
                {"menu_id": menu_id, "guild_id": ctx.guild.id}
            )

            # Update in-memory data
            menu_details["description"] = new_description

            if new_description:
                await ctx.send("Reaction Role Menu description updated.")
            else:
                await ctx.send("Reaction Role Menu description cleared.")

        except asyncio.TimeoutError:
            await ctx.send("Description update timed out.")
        except Exception as e:
            logger.error(f"Error in handle_description_menu: {e}", exc_info=True)
            await ctx.send("An error occurred while updating the description.")

    async def export_menu(self, ctx: commands.Context, menu_id: str) -> None:
        """
        Exports a Reaction Role Menu to a JSON file.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu to export.
        """
        try:
            # Validate UUID format
            try:
                uuid_obj = uuid.UUID(menu_id)
            except ValueError:
                await ctx.send("Invalid `menu_id` format. Please provide a valid UUID.")
                return

            # Fetch menu records
            records = await self.db_handler.fetch_records(
                "reaction_role_menus",
                {"menu_id": menu_id, "guild_id": ctx.guild.id}
            )
            if not records:
                await ctx.send(f"No reaction role menu found with ID `{menu_id}`.")
                return

            # Organize menu data
            menu_data = {
                "menu_id": menu_id,
                "name": records[0]['name'],
                "description": records[0]['description'],
                "guild_id": records[0]['guild_id'],
                "channel_id": records[0]['channel_id'],
                "message_id": records[0]['message_id'],
                "reactions": {record['emoji']: record['role_id'] for record in records}
            }

            # Convert to JSON
            json_data = json.dumps(menu_data, indent=4)
            json_bytes = json_data.encode()

            # Create a file-like object
            file = discord.File(io.BytesIO(json_bytes), filename=f"reaction_role_menu_{menu_id}.json")

            await ctx.send(f"Here is the exported JSON for Reaction Role Menu `{menu_data['name']}`:", file=file)

        except Exception as e:
            logger.error(f"Error in export_menu method: {e}", exc_info=True)
            await ctx.send("An error occurred while exporting the reaction role menu.")

    async def import_menu(self, ctx: commands.Context) -> None:
        """
        Imports a Reaction Role Menu from a JSON file.

        :param ctx: The command context.
        """
        import io  # Ensure import is available

        try:
            await ctx.send("Please upload the JSON file containing the Reaction Role Menu to import.")

            def file_check(m):
                return m.author == ctx.author and m.channel == ctx.channel and len(m.attachments) > 0

            try:
                message = await self.client.wait_for('message', check=file_check, timeout=300)  # 5 minutes
                attachment = message.attachments[0]
                if not attachment.filename.endswith('.json'):
                    await ctx.send("Invalid file format. Please upload a `.json` file.")
                    return

                json_bytes = await attachment.read()
                menu_data = json.loads(json_bytes.decode())
            except asyncio.TimeoutError:
                await ctx.send("Import timed out. Please try again.")
                return
            except json.JSONDecodeError:
                await ctx.send("Failed to decode JSON. Please ensure the file is a valid JSON.")
                return

            # Validate required fields
            required_fields = ["menu_id", "name", "guild_id", "channel_id", "message_id", "reactions"]
            if not all(field in menu_data for field in required_fields):
                await ctx.send("JSON is missing required fields. Please check the file and try again.")
                return

            # Ensure the menu is being imported into the correct guild
            if menu_data["guild_id"] != ctx.guild.id:
                await ctx.send("This menu is intended for a different server. Cannot import.")
                return

            # Validate roles and emojis
            for emoji, role_id in menu_data["reactions"].items():
                role = ctx.guild.get_role(role_id)
                if not role:
                    await ctx.send(f"Role with ID `{role_id}` not found. Import aborted.")
                    return
                if not self.is_valid_emoji(emoji, ctx.guild):
                    await ctx.send(f"The emoji `{emoji}` is invalid or not accessible by the bot. Import aborted.")
                    return

            # Assign a new UUID for the imported menu to avoid conflicts
            new_menu_id = uuid.uuid4()

            # Insert records into the database
            try:
                async with self.db_handler.transaction():
                    for emoji, role_id in menu_data["reactions"].items():
                        await self.db_handler.insert_record(
                            "reaction_role_menus",
                            {
                                "menu_id": str(new_menu_id),
                                "guild_id": ctx.guild.id,
                                "channel_id": menu_data["channel_id"],
                                "message_id": menu_data["message_id"],
                                "name": menu_data["name"],
                                "description": menu_data.get("description", ""),
                                "emoji": emoji,
                                "role_id": role_id
                            }
                        )
            except Exception as e:
                logger.error(f"Failed to insert imported reaction role menu records: {e}")
                await ctx.send("An error occurred while importing the reaction role menu. Rolling back.")
                await self.db_handler.rollback()
                return

            await ctx.send(f"Reaction Role Menu `{menu_data['name']}` imported successfully with new ID: `{new_menu_id}`.")

        except Exception as e:
            logger.error(f"Error in import_menu method: {e}", exc_info=True)
            await ctx.send("An unexpected error occurred while importing the reaction role menu.")

    async def delete_menu(self, ctx: commands.Context, menu_id: str) -> None:
        """
        Deletes a specific Reaction Role Menu.

        :param ctx: The command context.
        :param menu_id: The UUID of the menu to delete.
        """
        try:
            # Validate UUID format
            try:
                uuid_obj = uuid.UUID(menu_id)
            except ValueError:
                await ctx.send("Invalid `menu_id` format. Please provide a valid UUID.")
                return

            # Fetch existing menu records
            records = await self.db_handler.fetch_records(
                "reaction_role_menus",
                {"menu_id": menu_id, "guild_id": ctx.guild.id}
            )
            if not records:
                await ctx.send(f"No reaction role menu found with ID `{menu_id}`.")
                return

            # Confirm deletion
            await ctx.send(f"Are you sure you want to delete the Reaction Role Menu `{records[0]['name']}`? Type `yes` to confirm.")

            def confirm_check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() == 'yes'

            try:
                confirmation = await self.client.wait_for('message', check=confirm_check, timeout=60)  # 1 minute
            except asyncio.TimeoutError:
                await ctx.send("Deletion timed out. Menu was not deleted.")
                return

            # Fetch unique message details to remove reactions if possible
            unique_messages = {}
            for record in records:
                key = (record['channel_id'], record['message_id'])
                if key not in unique_messages:
                    unique_messages[key] = []
                unique_messages[key].append(record['emoji'])

            # Attempt to remove reactions from the message
            for (channel_id, message_id), emojis in unique_messages.items():
                channel = ctx.guild.get_channel(channel_id)
                if not channel:
                    continue
                try:
                    message = await channel.fetch_message(message_id)
                    for emoji in emojis:
                        try:
                            await message.clear_reaction(emoji)
                        except discord.HTTPException:
                            logger.warning(f"Failed to remove reaction {emoji} from message {message_id}.")
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    logger.warning(f"Message {message_id} not found or inaccessible in channel {channel_id}.")

            # Delete all entries with the given menu_id
            await self.db_handler.delete_records(
                "reaction_role_menus",
                {"menu_id": menu_id, "guild_id": ctx.guild.id}
            )

            await ctx.send(f"Reaction Role Menu `{menu_id}` has been deleted.")

        except Exception as e:
            logger.error(f"Error in delete_menu method: {e}", exc_info=True)
            await ctx.send("An error occurred while deleting the reaction role menu.")

    async def handle_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        """
        Handles the addition of a reaction by assigning the corresponding role.

        :param payload: The raw reaction event payload.
        """
        if payload.user_id == self.client.user.id:
            return  # Ignore bot's own reactions

        try:
            records = await self.db_handler.fetch_records(
                "reaction_role_menus",
                {"guild_id": payload.guild_id, "message_id": payload.message_id, "emoji": str(payload.emoji)}
            )
            if not records:
                return  # No matching reaction role menu

            guild = self.client.get_guild(payload.guild_id)
            if not guild:
                logger.warning(f"Guild ID {payload.guild_id} not found.")
                return

            member = guild.get_member(payload.user_id)
            if not member:
                logger.warning(f"Member ID {payload.user_id} not found in guild {guild.id}.")
                return

            for record in records:
                role = guild.get_role(record['role_id'])
                if role:
                    if role in member.roles:
                        continue  # User already has the role
                    if not role.is_assignable():
                        logger.warning(f"Role {role.name} is not assignable by the bot.")
                        continue
                    try:
                        await member.add_roles(role, reason="Reaction role assignment")
                        logger.info(f"Assigned role {role.name} to user {member.display_name}.")
                    except discord.Forbidden:
                        logger.error(f"Insufficient permissions to assign role {role.name} to {member.display_name}.")
                    except discord.HTTPException as e:
                        logger.error(f"HTTPException when assigning role: {e}")
                else:
                    logger.warning(f"Role ID {record['role_id']} not found in guild {guild.id}.")

        except Exception as e:
            logger.error(f"Error in handle_reaction_add: {e}", exc_info=True)

    async def handle_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        """
        Handles the removal of a reaction by removing the corresponding role.

        :param payload: The raw reaction event payload.
        """
        if payload.user_id == self.client.user.id:
            return  # Ignore bot's own reactions

        try:
            records = await self.db_handler.fetch_records(
                "reaction_role_menus",
                {"guild_id": payload.guild_id, "message_id": payload.message_id, "emoji": str(payload.emoji)}
            )
            if not records:
                return  # No matching reaction role menu

            guild = self.client.get_guild(payload.guild_id)
            if not guild:
                logger.warning(f"Guild ID {payload.guild_id} not found.")
                return

            member = guild.get_member(payload.user_id)
            if not member:
                logger.warning(f"Member ID {payload.user_id} not found in guild {guild.id}.")
                return

            for record in records:
                role = guild.get_role(record['role_id'])
                if role:
                    if role not in member.roles:
                        continue  # User does not have the role
                    try:
                        await member.remove_roles(role, reason="Reaction role removal")
                        logger.info(f"Removed role {role.name} from user {member.display_name}.")
                    except discord.Forbidden:
                        logger.error(f"Insufficient permissions to remove role {role.name} from {member.display_name}.")
                    except discord.HTTPException as e:
                        logger.error(f"HTTPException when removing role: {e}")
                else:
                    logger.warning(f"Role ID {record['role_id']} not found in guild {guild.id}.")

        except Exception as e:
            logger.error(f"Error in handle_reaction_remove: {e}", exc_info=True)

    # Pagination helper
    async def paginate(self, ctx: commands.Context, embeds: List[discord.Embed]):
        """
        Sends multiple embeds as paginated messages.

        :param ctx: The context of the command.
        :param embeds: A list of discord.Embed objects to paginate.
        """
        paginator = discord.ui.View(timeout=180)  # 3 minutes

        prev_button = discord.ui.Button(label="Previous", style=discord.ButtonStyle.gray)
        next_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.gray)

        current = 0

        async def update_embed(interaction: discord.Interaction):
            await interaction.response.edit_message(embed=embeds[current], view=paginator)

        async def prev_callback(interaction: discord.Interaction):
            nonlocal current
            if current > 0:
                current -= 1
                await update_embed(interaction)

        async def next_callback(interaction: discord.Interaction):
            nonlocal current
            if current < len(embeds) - 1:
                current += 1
                await update_embed(interaction)

        prev_button.callback = prev_callback
        next_button.callback = next_callback

        paginator.add_item(prev_button)
        paginator.add_item(next_button)

        await ctx.send(embed=embeds[current], view=paginator)

    # Helper methods

    def extract_role_id(self, role_mention: str) -> Optional[int]:
        """
        Extracts the role ID from a role mention string.

        :param role_mention: The role mention string.
        :return: The role ID as an integer, or None if extraction fails.
        """
        try:
            if role_mention.startswith('<@&') and role_mention.endswith('>'):
                return int(role_mention[3:-1])
            elif role_mention.isdigit():
                return int(role_mention)
            else:
                return None
        except ValueError:
            return None

    def is_valid_emoji(self, emoji: str, guild: discord.Guild) -> bool:
        """
        Validates whether an emoji is valid and accessible by the bot.

        :param emoji: The emoji string.
        :param guild: The guild where the emoji is being used.
        :return: True if valid, False otherwise.
        """
        # Check if it's a custom emoji
        if emoji.startswith('<:') and emoji.endswith('>'):
            try:
                emoji_id = int(emoji.split(':')[-1][:-1])
                return guild.get_emoji(emoji_id) is not None
            except ValueError:
                return False
        else:
            # It's a Unicode emoji; assume valid
            return True

    # Additional helper methods can be added here.


async def setup(client: commands.Bot, db_handler: DatabaseHandler) -> None:
    """
    Loads the ReactionRoleMenu cog.

    :param client: The instance of the Discord bot.
    :param db_handler: Instance of the DatabaseHandler to interact with the database.
    """
    await client.add_cog(ReactionRoleMenu(client, db_handler))
