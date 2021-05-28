# 1.1 добавил логи

import asyncio
import random
import string
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import settings

load_dotenv()
tt = str.maketrans(dict.fromkeys(string.punctuation))  # удаление знаков препинания: word = word.translate(tt)
muted_users_list = []
banned_users_list = []
invite_author: str
bot = commands.Bot(command_prefix=settings.prefix, intents=discord.Intents.all())
commands_clear = settings.commands_clear
bot.remove_command('help')
role_position = 7  # нужно для размещения ролей при использовании .color


@bot.event
async def on_ready():
    print('----------')
    print('Bot Connected')
    await bot.change_presence(status=discord.Status.dnd,
                              activity=discord.Activity(type=discord.ActivityType.listening, name='_Ziggi_'))
    print('----------')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        content = message.content.split()
        for word in content:
            word = word.translate(tt)
            if word in commands_clear:
                await asyncio.sleep(5)
                await message.delete()
    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(settings.chat_id)
    role = discord.utils.get(member.guild.roles, id=settings.human_id)
    color1 = 'f37e03'
    color1 = int(color1, 16)
    global invite_author
    await member.add_roles(role)
    print(f'{member.mention} присоединился к серверу.')
    emb = discord.Embed(description=f'{member.mention} присоединился к серверу. Добро пожаловать! 🎉',
                        color=color1)
    emb.set_footer(text=invite_author, icon_url=invite_author.avatar_url)

    await channel.send(embed=emb)


@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(settings.chat_id)
    color1 = 'f37e03'
    color1 = int(color1, 16)
    await channel.send(
        embed=discord.Embed(description=f'{member.mention} покинул сервер. 😧',
                            color=color1))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.channel.send(f'{ctx.author.mention}, такой команды не смуществует.')


# ----------------------------------------------------------------------------------------------------------------------
# @bot.command()  # cog load
# @commands.has_permissions(administrator=True)
# async def load(ctx, extension):
#     await ctx.message.delete()
#     bot.load_extension(f'cogs.{extension}')
#     await ctx.send('Cogs is loaded...')
#     print(f'{extension} has been loaded.')
#
#
# @bot.command()  # cog unload
# @commands.has_permissions(administrator=True)
# async def unload(ctx, extension):
#     await ctx.message.delete()
#     bot.unload_extension(f'cogs.{extension}')
#     await ctx.send('Cogs is unloaded...')
#     print(f'{extension} has been unloaded.')
#
#
# @bot.command()  # cog reload
# @commands.has_permissions(administrator=True)
# async def reload(ctx, extension):
#     await ctx.message.delete()
#     bot.unload_extension(f'cogs.{extension}')
#     bot.load_extension(f'cogs.{extension}')
#     await ctx.send('Cogs is reloaded...')
#     print(f'{extension} has been reloaded.')
#
#
# for filename in os.listdir('./cogs'):
#     if filename.endswith('.py'):
#         bot.load_extension(f'cogs.{filename[:-3]}')
#

# ----------------------------------------------------------------------------------------------------------------------
@bot.command() # test test test
@commands.has_permissions(administrator=True)
async def test(ctx):
    await ctx.send('test')


@bot.command() #
@commands.has_permissions(administrator=True)
async def testc(ctx):
    guild = ctx.guild
    channel = discord.utils.get(guild.text_channels, name="log-zbh")
    await ctx.send(f'test {channel}')


@bot.command()  # voice mute
@commands.has_permissions(administrator=True)
async def vmute(ctx, member: discord.Member, mute_time=float(), reason=''):
    await ctx.message.delete()
    mute_role = discord.utils.get(ctx.message.guild.roles, name='mute')
    await member.add_roles(mute_role)  # выдаю мут пользователю
    muted_users_list.append(member)
    current_channel = member.voice.channel
    channel = discord.utils.get(ctx.message.guild.voice_channels, name='technical')
    await member.edit(voice_channel=channel)  # перекидываем человека в technical
    await member.edit(voice_channel=current_channel)  # и обратно
    if reason == '':
        print(f'{member.name} получил мут.\nДлительность мута в минутах: {mute_time}.')
        await ctx.send(f'{member.mention} получил мут.')
    else:
        print(f'{member.name} получил мут. Длительность мута в минутах: {mute_time}. Причина: {reason}.')
        await ctx.send(f'{member.mention} получил мут.\nДлительность мута в минутах: {mute_time}.\nПричина: {reason}.')
    await asyncio.sleep(mute_time * 60)
    if member in muted_users_list:
        await member.remove_roles(mute_role)
        await member.edit(voice_channel=channel)
        await member.edit(voice_channel=current_channel)
        muted_users_list.remove(member)
        print(f'С {member.name} снят мут.')
        await ctx.send(f'С {member.mention} снят мут.')
        return
    else:
        return


@bot.command()  # voice unmute
@commands.has_permissions(administrator=True)
async def unvmute(ctx, member: discord.Member):
    await ctx.message.delete()
    mute_role = discord.utils.get(ctx.message.guild.roles, name='mute')
    current_channel = member.voice.channel
    channel = discord.utils.get(ctx.message.guild.voice_channels, name='technical')
    if member in muted_users_list:
        await member.remove_roles(mute_role)
        await member.edit(voice_channel=channel)
        await member.edit(voice_channel=current_channel)
        muted_users_list.remove(member)
        print(f'С {member.name} снят мут!')
        await ctx.send(f'С {member.mention} снят мут!')
        return
    else:
        await ctx.send(f'У {member.mention} не было мута.')
        return


@bot.command()  # clear
@commands.has_permissions(administrator=True)
async def clear(ctx, amount=str(100)):
    await ctx.message.delete()
    if amount == 'all':  # не пиши тут числа, будет работать не правильно
        await ctx.channel.purge(limit=100)
        print('Сообщения успешно удалены.')
        await ctx.channel.send('Сообщения успешно удалены.')
    else:
        amount3 = int(amount)
        if amount3 < 0:
            amount3 = amount3 * -1
        # amount1 = int(amount)
        # amount2 = amount1 ** 2
        # amount3 = amount2 ** 0.5
        if 0 <= amount3 <= 100:
            await ctx.channel.purge(limit=int(amount3))
            await ctx.channel.send('Сообщения успешно удалены.')
            print('Сообщения успешно удалены.')
        else:
            amount3 = 100
            await ctx.channel.purge(limit=int(amount3))
            await ctx.channel.send('Сообщения успешно удалены.')


@bot.command()  # kick
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason=''):
    await ctx.message.delete()
    await member.kick(reason=reason)
    if reason == '':
        await ctx.channel.send(f'{member.name} был кикнут с сервера.')
        print(f'{member.name} был кикнут с сервера.')
    elif reason != '':
        await ctx.channel.send(f'{member.name} был кикнут с сервера. Причина: {reason}.')
        print(f'{member.name} был кикнут с сервера. Причина: {reason}.')


@bot.command()  # ban
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason=''):
    await ctx.message.delete()
    await member.ban(reason=reason)
    banned_users_list.append(member.name)
    if reason == '':
        await ctx.channel.send(f'{member.name} был забанен на сервере.')
        print(f'{member.name} был забанен на сервере.')
    elif reason != '':
        await ctx.channel.send(f'{member.name} был забанен на сервере. Причина: {reason}.')
        print(f'{member.name} был забанен на сервере. Причина: {reason}.')


@bot.command()  # ban list
async def banlist(ctx):
    await ctx.message.delete()
    if not banned_users_list:
        await ctx.channel.send('Список забаненных пуст.')
        print('Список забаненных пуст.')
    else:
        await ctx.channel.send(banned_users_list)
        print('Отправлен список забаненных')
    return


@bot.command()  # unban
@commands.has_permissions(administrator=True)
async def unban(ctx):
    await ctx.message.delete()
    banned_users = await ctx.guild.bans()
    for ban_entry in banned_users:
        user = ban_entry.user
        banned_users_list.remove(user.name)
        await ctx.guild.unban(user)
        await ctx.channel.send(f'{user.name} разбанен.')
        return


@bot.command()  # invite
async def invite(ctx):
    await ctx.message.delete()
    channel = discord.utils.get(ctx.guild.channels, id=773951770485325875)
    link = await channel.create_invite(max_uses=1, unique=True, max_age=300)
    await ctx.message.author.send(f'**Приглашение действует 5 минут**\n{link}')
    global invite_author
    invite_author = ctx.message.author
    await asyncio.sleep(300)
    invite_author = ''


@bot.command()  # ping
async def ping(ctx):
    await ctx.message.delete()
    await ctx.channel.send(f'Пинг: {round(bot.latency, 2)}')


@bot.command()  # random color
async def rc(ctx):
    await ctx.message.delete()
    rgb = ""
    for _ in "RGB":
        i = random.randrange(0, 256)
        rgb += i.to_bytes(1, "big").hex()
    rgb1 = int(rgb, 16)
    emb = discord.Embed(color=rgb1, title='Код цвета:', description=rgb)
    emb.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
    await ctx.send(embed=emb)


@bot.command()  # color
async def color(ctx, *, clr):
    await ctx.message.delete()
    clr1 = str(clr)
    clr2 = int(clr1, 16)
    guild = ctx.guild
    role_name = f'ZBH-clr-{clr1}'
    if discord.utils.get(ctx.author.roles, name=f'ZBH-clr-{clr1}'):
        await ctx.channel.send('У вас уже установлен этот цвет.')
        print(f'цвет {role_name} уже есть у {ctx.author.nick}')
        return None  # если уже есть этот цвет
    else:
        guild_role_list = [r.name for r in guild.roles if r != ctx.guild.default_role]
        user_role_list = [r.name for r in ctx.author.roles if r != ctx.guild.default_role]
        for role123 in user_role_list:
            if 'ZBH-clr-' in role123:
                role123 = discord.utils.get(ctx.message.guild.roles, name=role123)
                await ctx.author.remove_roles(role123)

        if role_name in guild_role_list:
            role_id = (discord.utils.get(guild.roles, name=role_name))
            role_id1 = role_id.id
            clr_role = discord.utils.get(guild.roles, id=role_id1)
            await clr_role.edit(position=role_position)
            await ctx.author.add_roles(clr_role)
        else:
            await guild.create_role(name=f'ZBH-clr-{clr1}', color=clr2, permissions=settings.perms)
            role_id = (discord.utils.get(guild.roles, name=role_name))
            print(role_id)
            role_id1 = role_id.id
            clr_role = discord.utils.get(guild.roles, id=role_id1)
            await clr_role.edit(position=role_position)
            await ctx.author.add_roles(clr_role)


@bot.command() # help
async def help(ctx):
    await ctx.message.delete()
    p = settings.prefix
    color1 = 'f37e03'
    color1 = int(color1, 16)
    emb = discord.Embed(description="Навигация по командам \n'одинарные кавычки' в командах писать не нужно",
                        color=color1)
    emb.add_field(name=f"{p}color 'код цвета'", value='Изменение цвета', inline=False)
    emb.add_field(name=f"{p}rc", value='Рандомный цвет', inline=False)
    emb.add_field(name=f"{p}invite", value='Получить ссылку-приглашение', inline=False)
    emb.add_field(name=f"{p}banlist", value='Получить список забаненных пользователей', inline=False)
    emb.add_field(name=f"{p}В разработке...", value='...', inline=False)

    await ctx.channel.send(embed=emb)


# }-------------------------------------------------------ERRORS-------------------------------------------------------{
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.errors.CommandError):
        await ctx.channel.send(f'{ctx.author.mention}, не правильный тип данных.')
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.send(f'{ctx.author.mention}, у вас не достаточно прав.')


@color.error
async def color_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.channel.send(f'{ctx.author.mention}, вы не указали код цвета.')


@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.send(f'{ctx.author.mention}, у вас не достаточно прав.')


@vmute.error
async def vmute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.send(f'{ctx.author.mention}, у вас не достаточно прав.')


@unvmute.error
async def unvmute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.send(f'{ctx.author.mention}, у вас не достаточно прав.')


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.send(f'{ctx.author.mention}, у вас не достаточно прав.')


bot.run(os.getenv("DISCORD_TOKEN"))
