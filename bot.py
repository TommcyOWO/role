import discord
from discord.ext import commands
from discord.commands import Option

import json

bot = commands.Bot(intents=discord.Intents.all())

@bot.command()
async def here(ctx):
    await ctx.send(F"{ctx.author}你好,你現在在{ctx.guild.name}的{ctx.channel.mention}")


@bot.slash_command(description="設置反應身分組")
async def reaction_role(ctx,
                        內容: Option(str, "嵌入訊息內容"),
                        role: Option(discord.Role, "要領取的身分組"),
                        emoji: Option(discord.PartialEmoji, "要添加的反應")):  # 斜線指令選項
    await ctx.defer()  # 延遲回覆
    if not ctx.author.guild_permissions.administrator:  # 如果使用者沒管理權限
        await ctx.respond("只有管理員能使用此指令")
        return  # 結束運行
    embed = discord.Embed(title="領取身分組", description=內容)
    message = await ctx.send(embed=embed)  # 傳送領取訊息
    await message.add_reaction(emoji)  # 加入第一個反應
    with open("role.json", "r") as file:  # 用閱讀模式開啟資料儲存檔案
        data = json.load(file)  # data = 資料裡的字典{}
    with open("role.json", "w") as file:  # 用write模式開啟檔案
        data[str(message.id)] = {"role": role.id, "emoji": emoji.id}  # 新增字典資料
        json.dump(data, file, indent=4)  # 上載新增後的資料
    await ctx.respond("設置完畢", delete_after=3)


@bot.event
async def on_raw_reaction_add(payload):  # 偵測到添加反應
    with open("role.json", "r") as file:  # 用read模式開啟檔案
        data = json.load(file)  # 讀取檔案內容
    if not str(payload.message_id) in data:  # 如果檔案裡沒有資料
        return  # 結束運行
    if data[str(payload.message_id)]["emoji"] != payload.emoji.id:  # 判斷添加的反應是否是設置的反應
        return  # 結束運行
    guild = await bot.fetch_guild(payload.guild_id)  # 取得群組
    role = guild.get_role(data[str(payload.message_id)]["role"])  # 取得身分組
    await payload.member.add_roles(role, reason="反應身分組系統")  # 給予身份組
    try:
        await payload.member.send(F"已給予 {role}", delete_after=10)  # 私訊給予訊息
    except:
        pass


@bot.event
async def on_raw_reaction_remove(payload):  # 偵測到添加反應
    with open("role.json", "r") as file:  # 用read模式開啟檔案
        data = json.load(file)  # 讀取檔案內容
    if not str(payload.message_id) in data:  # 如果檔案裡沒有資料
        return  # 結束運行
    if data[str(payload.message_id)]["emoji"] != payload.emoji.id:  # 判斷添加的反應是否是設置的反應
        return  # 結束運行
    guild = await bot.fetch_guild(payload.guild_id)  # 取得群組
    role = guild.get_role(data[str(payload.message_id)]["role"])  # 取得身分組
    member = await guild.fetch_member(payload.user_id)
    await member.remove_roles(role, reason="反應身分組系統")  # 移除身分組
    try:
        await member.send(F"已移除 {role}", delete_after=10)  # 私訊給予訊息
    except:
        pass

with open("config.json", "r") as file:
    data = json.load(file)
TOKEN = data["token"]
bot.run(TOKEN)
