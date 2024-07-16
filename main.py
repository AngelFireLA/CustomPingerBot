import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


@bot.tree.command(name="pingforumrole", description="Ping users with a specific role in this forum post")
@app_commands.describe(role="The role to ping")
@app_commands.checks.has_permissions(administrator=True)
async def ping_forum_role(interaction: discord.Interaction, role: discord.Role):
    # Check if the command is used in a forum post
    if not isinstance(interaction.channel, discord.Thread) or not isinstance(interaction.channel.parent,
                                                                             discord.ForumChannel):
        await interaction.response.send_message("This command can only be used in a forum post.", ephemeral=True)
        return

    # Get all members who have the specified role
    role_members = role.members

    # Get all members who have posted in this thread
    thread_members = set()
    async for message in interaction.channel.history(limit=None):
        thread_members.add(message.author)

    # Find the intersection of role members and thread members
    members_to_ping = set(role_members) & thread_members

    if not members_to_ping:
        await interaction.response.send_message(f"No users with the {role.name} role have posted in this thread.",
                                                ephemeral=True)
        return

    # Create the ping message
    ping_message = " ".join([member.mention for member in members_to_ping])

    await interaction.response.send_message(
        f"{ping_message}")


@ping_forum_role.error
async def ping_forum_role_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You must be an administrator to use this command.", ephemeral=True)
    else:
        await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)


bot.run(TOKEN)