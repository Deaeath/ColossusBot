from discord.ext import commands
from discord import Embed, Message
from typing import Optional
import aiohttp


class CatfishCommand(commands.Cog):
    """
    A Discord bot cog for performing reverse image searches using SerpAPI.
    """

    SERPAPI_KEY = "YOUR_SERPAPI_KEY"  # Replace with your SerpAPI key

    @commands.command(aliases=["catfishcheck", "reverseimage"])
    async def catfish(self, ctx: commands.Context, image_url: Optional[str] = None) -> None:
        """
        Perform a reverse image search using SerpAPI.

        Args:
            ctx (commands.Context): The context of the command invocation.
            image_url (Optional[str]): A URL pointing to the image to be searched.

        Returns:
            None: Sends the search results or an error message.
        """
        # Check for attached image in the command message
        if ctx.message.attachments:
            image_url = ctx.message.attachments[0].url

        # Use provided image URL
        elif image_url:
            pass

        # Check if it's a reply to a message and extract the image
        elif ctx.message.reference:
            referenced_message: Message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

            # Extract image from attachments
            if referenced_message.attachments:
                image_url = referenced_message.attachments[0].url
            # Extract image from message content if it contains a valid image URL
            elif referenced_message.content and (
                "http" in referenced_message.content
                and (".jpg" in referenced_message.content or ".png" in referenced_message.content)
            ):
                image_url = referenced_message.content

        # If no image was found at all
        if not image_url:
            embed = Embed(
                title="How to use this command?",
                description="Please attach an image, provide an image URL, or reply to a message containing an image.",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        await ctx.send("🔍 Checking image...")

        # Set up parameters for SerpAPI
        params = {
            "engine": "google_reverse_image",
            "image_url": image_url,
            "api_key": self.SERPAPI_KEY
        }

        # Perform the API request
        async with aiohttp.ClientSession() as session:
            async with session.get("https://serpapi.com/search", params=params) as response:
                data = await response.json()

        # Handle errors in the API response
        if "error" in data:
            embed = Embed(
                title="Error",
                description=f"Error: {data['error']}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        # Process and display search results
        search_results = data.get("image_results", [])
        if search_results:
            results = ""
            for idx, result in enumerate(search_results, start=1):
                results += f"[{idx}] [{result.get('title', 'No Title')}]({result.get('link', '')})\n"

            embed = Embed(
                title="🔍 Reverse Image Search Results",
                description=results,
                color=0x00FF00
            )
            await ctx.send(embed=embed)
        else:
            embed = Embed(
                title="No Matches Found",
                description="No matches were found for the provided image.",
                color=0xFFA500
            )
            await ctx.send(embed=embed)


async def setup(client: commands.Bot) -> None:
    """
    Add the CatfishCommand cog to the bot.

    Args:
        client (commands.Bot): The bot instance to which the cog will be added.

    Returns:
        None
    """
    await client.add_cog(CatfishCommand())
