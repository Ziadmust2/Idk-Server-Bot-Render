import discord
from discord.ext import commands
import random
import json
import os
import webserver

# -----------------------------
# Config
# -----------------------------
TOKEN = os.environ['MTQ2NzEyNTQwNzAwNTU0MDM2NQ.GF5vGJ.eew6N_2V8QHfepFjr6kLJ6-I-G5eoi_n9xnvOM']  # Set this in your environment
MATH_CHANNEL_ID = 1467118980530704519  # Replace with your math channel ID

# Points milestones and roles
ROLE_MILESTONES = {
    50: "Math Novice",
    100: "Math Pro",
    200: "Math Master"
}

# -----------------------------
# Data
# -----------------------------
points_file = "points.json"
if os.path.exists(points_file):
    with open(points_file, "r") as f:
        points_data = json.load(f)
else:
    points_data = {}

active_questions = {}

def save_points():
    with open(points_file, "w") as f:
        json.dump(points_data, f)

# -----------------------------
# Bot setup
# -----------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required to give roles
bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------------
# Events
# -----------------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# -----------------------------
# Commands
# -----------------------------

# 1️⃣ Math question
@bot.command()
async def math(ctx):
    if ctx.channel.id != MATH_CHANNEL_ID:
        return  # ignore commands outside math channel

    a = random.randint(1, 20)
    b = random.randint(1, 20)
    op = random.choice(["+", "-", "*"])
    answer = eval(f"{a}{op}{b}")
    active_questions[ctx.author.id] = answer
    await ctx.send(f"🧮 **Math Question**\nWhat is **{a} {op} {b}** ?")

# 2️⃣ Answer
@bot.command()
async def answer(ctx, *, user_answer):
    if ctx.channel.id != MATH_CHANNEL_ID:
        return

    correct = active_questions.get(ctx.author.id)
    if correct is None:
        await ctx.send("❌ You don’t have an active math question.")
        return

    try:
        user_answer = float(user_answer.strip())
    except ValueError:
        await ctx.send("❌ Please type a valid number!")
        return

    if float(user_answer) == float(correct):
        uid = str(ctx.author.id)
        points_data[uid] = points_data.get(uid, 0) + 10
        save_points()
        del active_questions[ctx.author.id]
        await ctx.send(f"✅ Correct! You earned **10 points**\n🏆 Total: **{points_data[uid]}**")
        await check_roles(ctx)
    else:
        await ctx.send("❌ Wrong answer. Try again!")

# 3️⃣ Check points
@bot.command(name="points")
async def points_command(ctx):
    uid = str(ctx.author.id)
    await ctx.send(f"🪙 **Your points:** {points_data.get(uid, 0)}")

# 4️⃣ Leaderboard
@bot.command()
async def leaderboard(ctx):
    if not points_data:
        await ctx.send("No points yet 😴")
        return

    sorted_users = sorted(points_data.items(), key=lambda x: x[1], reverse=True)
    text = "🏆 **Leaderboard**\n"
    for i, (uid, score) in enumerate(sorted_users[:10], start=1):
        try:
            user = await bot.fetch_user(int(uid))
            text += f"{i}. {user.name} — {score} points\n"
        except:
            text += f"{i}. Unknown User — {score} points\n"
    await ctx.send(text)

# -----------------------------
# Helper: assign roles for milestones
# -----------------------------
async def check_roles(ctx):
    uid = str(ctx.author.id)
    score = points_data.get(uid, 0)
    member = ctx.author
    guild = ctx.guild

    for milestone, role_name in ROLE_MILESTONES.items():
        if score >= milestone:
            role = discord.utils.get(guild.roles, name=role_name)
            if role and role not in member.roles:
                await member.add_roles(role)
                await ctx.send(f"🎉 Congrats! You earned the **{role_name}** role!")

# -----------------------------
# Run bot
# -----------------------------
bot.run("DISCORD_TOKEN")
