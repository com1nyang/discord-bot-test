import discord

# 필요한 인텐트만 명시 (메시지 읽기만 필요할 경우)
intents = discord.Intents.default()
intents.messages = True  # 메시지 이벤트 처리
intents.guilds = True    # 서버 관련 이벤트 처리
intents.message_content = True  # 메시지 내용 읽기 (Developer Portal에서 활성화 필요)

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower() == "print":
        await message.channel.send("HelloWorld!")

client.run("MTMzOTU4NDY2Mjg5NjY0MDAxMA.GUecAC.jh8T2TJEqRSGEaTJVNOKxDSOlGiSbsPrJlMSaY")
