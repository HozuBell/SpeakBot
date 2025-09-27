import discord
from discord import app_commands
from gtts import gTTS
import os
import asyncio
from dotenv import load_dotenv

# Load biến môi trường từ file .env (local)
load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID")) if os.getenv("GUILD_ID") else None

if not TOKEN:
    raise RuntimeError("⚠️ Chưa tìm thấy TOKEN! Hãy đặt trong .env (local) hoặc Railway → Variables")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    try:
        if GUILD_ID:
            await tree.sync(guild=discord.Object(id=GUILD_ID))
            print(f"✅ Slash commands synced to guild {GUILD_ID}")
        else:
            await tree.sync()
            print("✅ Slash commands synced globally (có thể mất vài phút mới hiện)")
    except Exception as e:
        print(f"⚠️ Lỗi khi sync slash commands: {e}")

    print(f"🤖 Bot đã đăng nhập: {client.user}")

# Lệnh /say
@tree.command(
    name="say",
    description="Bot sẽ đọc văn bản bằng TTS",
    guild=discord.Object(id=GUILD_ID) if GUILD_ID else None
)
async def say(interaction: discord.Interaction, text: str):
    await interaction.response.defer()

    # Tạo file mp3 TTS
    tts = gTTS(text=text, lang="vi")
    filename = "tts.mp3"
    tts.save(filename)

    # Nếu user đang trong voice channel → bot join và phát
    if interaction.user.voice and interaction.user.voice.channel:
        channel = interaction.user.voice.channel
        voice_client = await channel.connect()

        voice_client.play(discord.FFmpegPCMAudio(filename))

        # Chờ phát xong
        while voice_client.is_playing():
            await asyncio.sleep(1)

        await voice_client.disconnect()
    else:
        await interaction.followup.send("⚠️ Bạn phải vào voice channel trước!")

    # Gửi file mp3 lên kênh text
    await interaction.followup.send(file=discord.File(filename))
    os.remove(filename)

client.run(TOKEN)
