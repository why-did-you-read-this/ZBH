# 1.1 добавил логи

import asyncio
import random
import string
import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import settings
import re
from discord_components import DiscordComponents, Button, ButtonStyle

load_dotenv()  # не удалять
tt = str.maketrans(dict.fromkeys(string.punctuation))  # удаление знаков препинания: word = word.translate(tt)
muted_users_list = []
banned_users_list = []
invite_author: str
bot = commands.Bot(command_prefix=settings.prefix, intents=discord.Intents.all(), case_insensitive=True)
bot.remove_command('help')
role_position = 7  # нужно для размещения ролей при использовании .color
color1 = int('f37e03', 16)
time_regex = re.compile(r"(\d{1,5}(?:[.,]?\d{1,5})?)([smhd])")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


intervals = (
    ('д', 86400), # 60 * 60 * 24
    ('ч', 3600),  # 60 * 60
    ('м', 60),
    ('с', 1)
)


def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        matches = time_regex.findall(argument.lower())
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k] * float(v)
            except KeyError:
                raise commands.BadArgument(f"{k} не является форматом времени! Используйте s/m/h/d !")
            except ValueError:
                raise commands.BadArgument(f"{v} не является числом!")
        return time


@bot.event
async def on_ready():
    print('----------')
    print('Bot Connected')
    await bot.change_presence(status=discord.Status.dnd,
                              activity=discord.Activity(type=discord.ActivityType.listening, name='_Ziggi_'))
    print('----------')


@bot.event
async def on_message(message):
    log_channel = discord.utils.get(message.guild.text_channels, name="log-zbh")
    if message.author == bot.user:
        content = message.content.split()
        for word in content:
            word = word.translate(tt)
            if word in settings.commands_clear:
                await asyncio.sleep(5)
                await message.delete()
    if not message.author.bot:
        emb = discord.Embed(description=message.content,
                            color=color1)
        emb.set_footer(text=message.author, icon_url=message.author.avatar_url)
        await log_channel.send(embed=emb)
        print(f'[M] {message.author.name} >>> {message.content}')
    await bot.process_commands(message)


@bot.event
async def on_member_update(before, after):  # ##########################################################################
    log_channel = discord.utils.get(before.guild.text_channels, name="log-zbh")
    emb = discord.Embed(
        title='Изменён ник',
        description='Изменён ник',
        colour=color1
    )
    fields = [
        ('Было', before.display_name, False),
        ('Стало', after.display_name, False)
    ]
    for name, value, inline in fields:
        emb.add_field(name=name, value=value, inline=inline)
    # await log_channel.send(embed=emb)


@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="💬┊chat")
    role = discord.utils.get(member.guild.roles, name='Human')
    global invite_author
    await member.add_roles(role)
    print(f'{member.mention} присоединился к серверу.')
    emb = discord.Embed(description=f'{member.mention} присоединился к серверу. Добро пожаловать! 🎉', color=color1)
    emb.set_footer(text=invite_author, icon_url=invite_author.avatar_url)

    await channel.send(embed=emb)


@bot.event
async def on_member_remove(member: discord.Member):
    channel = discord.utils.get(member.guild.text_channels, name="💬┊chat")
    emb = discord.Embed(description=f'{member.name} покинул сервер. 😧', color=color1)
    emb.set_footer(text=member.name, icon_url=member.avatar_url) # error?
    await channel.send(embed=emb)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(f'{ctx.author.mention}, такой команды не смуществует.')


# ----------------------------------------------------------------------------------------------------------------------


@bot.command()  # voice mute
@commands.has_permissions(administrator=True)
async def vmute(ctx, member: discord.Member, mute_time: TimeConverter, *, reason=None):
    log_channel = discord.utils.get(ctx.guild.text_channels, name="log-zbh")
    await ctx.message.delete()
    mute_role = discord.utils.get(ctx.message.guild.roles, name='mute')
    await member.add_roles(mute_role)  # выдаю мут пользователю
    muted_users_list.append(member)
    current_channel = member.voice.channel
    channel = discord.utils.get(ctx.message.guild.voice_channels, name='technical')
    await member.edit(voice_channel=channel)  # перекидываем человека в technical
    await member.edit(voice_channel=current_channel)  # и обратно
    mute_time = round(mute_time)
    mute_time2 = display_time(mute_time)
    if reason is None:
        print(f'{member.name} получил мут. Длительность мута: {mute_time2}.')
        await ctx.send(f'{member.mention} получил мут.\nДлительность мута: {mute_time2}.')
        await log_channel.send(f'{member.mention} получил мут.\nДлительность мута: {mute_time2}.')
    else:
        print(f'{member.name} получил мут. Длительность мута: {mute_time2}. Причина: {reason}.')
        await ctx.send(f'{member.mention} получил мут.\nДлительность мута: {mute_time2}.\nПричина: {reason}.')
        await log_channel.send(f'{member.mention} получил мут.\nДлительность мута: {mute_time2}.\nПричина:'
                               f' {reason}.')
    await asyncio.sleep(mute_time)
    if member in muted_users_list:
        await member.remove_roles(mute_role)
        await member.edit(voice_channel=channel)
        await member.edit(voice_channel=current_channel)
        muted_users_list.remove(member)
        print(f'С {member.name} снят мут.')
        await ctx.send(f'С {member.mention} снят мут.')
        await log_channel.send(f'С {member.mention} снят мут.')
        return
    else:
        pass


@bot.command()  # voice unmute
@commands.has_permissions(administrator=True)
async def unvmute(ctx, member: discord.Member):
    log_channel = discord.utils.get(ctx.guild.text_channels, name="log-zbh")
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
        await log_channel.send(f'С {member.mention} снят мут!')
        return
    else:
        print(f'У {member.mention} не было мута.')
        await ctx.send(f'У {member.mention} не было мута.')
        return


@bot.command()  # clear
@commands.has_permissions(administrator=True)
async def clear(ctx, amount=str(100)):
    await ctx.message.delete()
    if amount == 'all':  # не пиши тут числа, будет работать не правильно
        await ctx.channel.purge(limit=100)
        await ctx.send('Сообщения успешно удалены.')
    else:
        amount3 = int(amount)
        if amount3 < 0:
            amount3 = amount3 * -1
        if 0 <= amount3 <= 100:
            await ctx.channel.purge(limit=int(amount3))
            await ctx.send('Сообщения успешно удалены.')
        else:
            amount3 = 100
            await ctx.channel.purge(limit=int(amount3))
            await ctx.send('Сообщения успешно удалены.')


@bot.command()  # kick
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason=''):
    log_channel = discord.utils.get(ctx.guild.text_channels, name="log-zbh")
    await ctx.message.delete()
    await member.kick(reason=reason)
    if reason == '':
        await ctx.send(f'{member.name} был кикнут с сервера.')
        await log_channel.send(f'{member.name} был кикнут с сервера.')
        print(f'{member.name} был кикнут с сервера.')
    elif reason != '':
        await ctx.send(f'{member.name} был кикнут с сервера. Причина: {reason}.')
        await log_channel.send(f'{member.name} был кикнут с сервера. Причина: {reason}.')
        print(f'{member.name} был кикнут с сервера. Причина: {reason}.')


@bot.command()  # ban
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason=''):
    log_channel = discord.utils.get(ctx.guild.text_channels, name="log-zbh")
    await ctx.message.delete()
    await member.ban(reason=reason)
    banned_users_list.append(member.name)
    if reason == '':
        await ctx.send(f'{member.name} был забанен на сервере.')
        await log_channel.send(f'{member.name} был забанен на сервере.')
        print(f'{member.name} был забанен на сервере.')
    else:
        await ctx.send(f'{member.name} был забанен на сервере. Причина: {reason}.')
        await log_channel.send(f'{member.name} был забанен на сервере.  Причина: {reason}.')
        print(f'{member.name} был забанен на сервере. Причина: {reason}.')


@bot.command()  # ban list
async def banlist(ctx):
    await ctx.message.delete()
    if not banned_users_list:
        await ctx.send('Список забаненных пуст.')
    else:
        await ctx.send(banned_users_list)
    return


@bot.command()  # unban
@commands.has_permissions(administrator=True)
async def unban(ctx):
    log_channel = discord.utils.get(ctx.guild.text_channels, name="log-zbh")
    await ctx.message.delete()
    banned_users = await ctx.guild.bans()
    for ban_entry in banned_users:
        user = ban_entry.user
        banned_users_list.remove(user.name)
        await ctx.guild.unban(user)
        await ctx.send(f'{user.name} разбанен.')
        await log_channel.send(f'{user.name} разбанен.')
        print(f'{user.name} разбанен.')
        return


@bot.command()  # invite
async def invite(ctx):
    lifetime = 300
    log_channel = discord.utils.get(ctx.guild.text_channels, name="log-zbh")
    await ctx.message.delete()
    channel = discord.utils.get(ctx.guild.channels, id=773951770485325875)
    link = await channel.create_invite(max_uses=1, unique=True, max_age=lifetime)
    await ctx.message.author.send(f'**Приглашение действует 5 минут**\n{link}')
    global invite_author
    invite_author = ctx.message.author
    await log_channel.send(f'{ctx.author.mention} создал приглашение.')
    print(f'{ctx.author.name} создал приглашение.')
    await asyncio.sleep(lifetime)
    invite_author = ''


@bot.command()  # ping
async def ping(ctx):
    await ctx.message.delete()
    await ctx.send(f'Пинг: {round(bot.latency, 2)}')


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
        await ctx.send('У вас уже установлен этот цвет.')
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


@bot.command()  # help
async def help(ctx):
    await ctx.message.delete()
    p = settings.prefix
    emb = discord.Embed(title="Список команд", description="'одинарные кавычки' в командах писать не нужно",
                        color=color1)
    emb.add_field(name=f"{p}color 'код цвета'", value='Изменение цвета', inline=False)
    emb.add_field(name=f"{p}rc", value='Рандомный цвет', inline=False)
    emb.add_field(name=f"{p}invite", value='Получить ссылку-приглашение', inline=False)
    emb.add_field(name=f"{p}banlist", value='Получить список забаненных пользователей', inline=False)
    emb.add_field(name=f"{p}ping", value='Узнать пинг бота', inline=False)
    emb.add_field(name=f"{p}В разработке...", value='...', inline=False)

    await ctx.send(embed=emb)


# }------------------------------------------------------ ERRORS ------------------------------------------------------{


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.errors.CommandError):
        await ctx.send(f'{ctx.author.mention}, не правильный тип данных.')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention}, у вас не достаточно прав.')


@color.error
async def color_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(f'{ctx.author.mention}, вы не указали код цвета.')


@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention}, у вас не достаточно прав.')


@vmute.error
async def vmute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention}, у вас не достаточно прав.')


@unvmute.error
async def unvmute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention}, у вас не достаточно прав.')


@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f'{ctx.author.mention}, у вас не достаточно прав.')


bot.run(os.getenv("DISCORD_TOKEN"))
