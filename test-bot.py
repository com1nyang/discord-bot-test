import discord
import os
from discord.ext import commands
from discord import ui, ButtonStyle, Embed
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 슬롯 상태 관리
slots = [None] * 5
slot_message = None


class MyView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_buttons()

    def add_buttons(self):
        buttons = [
            ("안녕", ButtonStyle.green, "안녕하세요!"),
            ("요일", ButtonStyle.blurple, f"오늘은 {self.get_day_of_week()}입니다."),
            ("시간", ButtonStyle.gray, f"현재 시간은 {self.get_time()}입니다."),
            ("정보", ButtonStyle.primary, "이것은 테스트 봇입니다."),
            ("도움말", ButtonStyle.red, "사용 가능한 명령어: 안녕, 요일, 시간, 정보, 도움말"),
        ]

        for label, style, response in buttons:
            self.add_item(MyButton(label, style, response))

    @staticmethod
    def get_day_of_week():
        weekday_list = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        weekday = weekday_list[datetime.today().weekday()]
        date = datetime.today().strftime("%Y년 %m월 %d일")
        return f"{date}({weekday})"

    @staticmethod
    def get_time():
        return datetime.today().strftime("%H시 %M분 %S초")


class MyButton(ui.Button):
    def __init__(self, label, style, response):
        super().__init__(label=label, style=style)
        self.response = response

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(self.response)


class SlotButton(ui.Button):
    def __init__(self, index):
        super().__init__(label=f"슬롯 {index + 1}: 비어있음", style=ButtonStyle.blurple)
        self.index = index

    async def callback(self, interaction: discord.Interaction):
        global slots, slot_message
        user = interaction.user.name

        # 슬롯에 사용자 등록/해제
        if slots[self.index] is None:
            slots[self.index] = user
        else:
            if slots[self.index] == user:
                slots[self.index] = None
            else:
                await interaction.response.send_message("⚠️ 해당 슬롯은 이미 다른 사용자가 차지했습니다!", ephemeral=True)
                return

        # 슬롯 상태 갱신
        if slot_message:
            await slot_message.edit(embed=generate_slot_embed(), view=SlotView())

        await interaction.response.defer()


class ResetButton(ui.Button):
    def __init__(self):
        super().__init__(label="🔄 슬롯 초기화", style=ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):
        global slots, slot_message
        # 슬롯 초기화
        slots = [None] * 5
        if slot_message:
            await slot_message.edit(embed=generate_slot_embed(), view=SlotView())
        await interaction.response.defer()


class SlotView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for i in range(5):
            label = f"슬롯 {i + 1}: {slots[i] if slots[i] else '비어있음'}"
            button = SlotButton(i)
            button.label = label
            button.style = ButtonStyle.green if slots[i] else ButtonStyle.blurple
            self.add_item(button)

        # 슬롯이 가득 찼을 때 초기화 버튼 추가
        if all(slots):
            self.add_item(ResetButton())


def generate_slot_embed():
    """슬롯 상태를 보여주는 Embed 생성."""
    description = "\n".join([f"슬롯 {i + 1}: {slots[i] if slots[i] else '비어있음'}" for i in range(5)])
    embed = Embed(title="🎯 롤 자랭 슬롯 상태", description=description, color=0x00FF00)
    return embed


@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    channel = bot.get_channel(int(os.getenv('CHANNEL_ID')))
    if channel:
        embed = Embed(title="🤖 Bot Control Panel", description="아래 버튼을 클릭해보세요!", color=0x3498db)
        view = MyView()
        await channel.send(embed=embed, view=view)

    # 등록된 슬래시 명령어를 싱크(동기화)
    try:
        synced = await bot.tree.sync()
        print(f"🔄 슬래시 명령어 동기화 완료: {synced}")
    except Exception as e:
        print(f"⚠️ 슬래시 명령어 동기화 실패: {e}")


@bot.tree.command(name="자랭", description="롤 자랭 슬롯을 보여줍니다.")
async def 자랭(interaction: discord.Interaction):
    global slot_message
    embed = generate_slot_embed()
    view = SlotView()

    # 슬롯 메시지를 처음 생성하거나 업데이트
    if slot_message:
        await slot_message.edit(embed=embed, view=view)
        await interaction.response.send_message("🎯 슬롯 상태가 업데이트되었습니다!", ephemeral=False)
    else:
        slot_message = await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("🎯 슬롯을 표시했습니다!", ephemeral=False)



bot.run(token)
