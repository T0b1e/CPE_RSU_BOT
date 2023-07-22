import discord
from config import TOKEN
#from discord.ui import Select, View
import json
from discord import app_commands
from discord.ext import commands
from keep_alive import keep_alive

keep_alive()

activity = discord.Activity(type=discord.ActivityType.competing,
                            name="/identify")
bot = commands.Bot(command_prefix="!",
                   activity=activity,
                   status=discord.Status.online,
                   intents=discord.Intents.all())


def check_id(data, student_id, batch):
  fullname = "ไม่มีชื่ออยู่ในระบบ"
  found = False
  for item in data:
    if item["id"] == student_id:
      fullname = item["name"]
      found = True
      break
  if not found:
    batch = "ระบุปีการศึกษาให้ถูกต้อง"
  return fullname, found, batch


@bot.event
async def on_ready():
  print(f'Logged in as {bot.user}!')
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} Command")
  except Exception as e:
    print(e)


class verify(discord.ui.View):

  def __init__(self, batch: str):
    super().__init__()
    self.batch = batch

  @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
  async def yes(self, interaction: discord.Interaction,
                button: discord.ui.Button):
    role = discord.utils.get(interaction.guild.roles, name=self.batch)
    await interaction.user.add_roles(role)
    await interaction.response.send_message(
      "✅ ข้อมูลได้รับการยืนยันเรียบร้อย! ✅", ephemeral=True)

  @discord.ui.button(label="No", style=discord.ButtonStyle.red)
  async def no(self, interaction: discord.Interaction,
               button: discord.ui.Button):
    await interaction.response.send_message(
      "❌ ข้อมูลผิดพลาด! โปรดลองใหม่อีกครั้ง ❌", ephemeral=True)


@bot.tree.command(name="identify")
@app_commands.describe(batch="คุณอยู่ปีการศึกษาอะไร?")
@app_commands.choices(batch=[
  discord.app_commands.Choice(name="65", value=1),
  discord.app_commands.Choice(name="66", value=2)
])
@app_commands.describe(student_id="รหัสนักศึกษาของคุณคืออะไร?")
async def identify(interaction: discord.Interaction,
                   batch: discord.app_commands.Choice[int], student_id: str):
  if str(interaction.channel_id) == "1115992063654232064":
    embed = discord.Embed(title="**IDENTITY CONFIRMATION**",
                          color=discord.Color.blue())
    found = False
    years = "25"
    print(batch)
    with open('Y65.json') as file:
      data = json.load(file)
      fullname, found, batch = check_id(data, student_id, batch.name)
    if found:
      r_batch = "65"
    elif not found:
      r_batch = "66"
      with open('Y66.json') as file:
        data2 = json.load(file)
        fullname, found, r_batch = check_id(data2, student_id, r_batch)
    if not found:
      years = ""
    print(r_batch)
    embed.add_field(name="ชื่อ - นามสกุล : " + fullname, value="", inline=True)
    embed.add_field(name="รหัสนักศึกษา : " + student_id,
                    value="",
                    inline=False)
    embed.add_field(name="ปีการศึกษา : " + years + r_batch,
                    value="",
                    inline=False)
    embed.add_field(
      name=
      f"Discord ID : {interaction.user.display_name}#{interaction.user.discriminator}",
      value="".join(interaction.user.mention),
      inline=True)
    embed.set_thumbnail(url=interaction.user.avatar.url)
    embed.set_footer(text="Powered By L3ooK")
    if years == "":
      await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
      channel = await bot.fetch_channel(1120832999487979530)
      await interaction.response.send_message(embed=embed,
                                              view=verify(str(r_batch)),
                                              ephemeral=True)
      await channel.send(embed=embed)
  else:
    await interaction.response.send_message("ไม่สามารถใช้คำสั่งในห้องนี้ได้!",
                                            ephemeral=True)


bot.run(TOKEN)
