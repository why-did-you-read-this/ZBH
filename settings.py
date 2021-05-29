import discord

commands_clear = [  # Не удаляй одни и те же слова в разных регистрах
    'Сообщения',
    'сообщения',
    'сообщений',
    'число',
    'удалить',
    'Список',
    'Cogs',
    'Пинг'
]
perms = discord.Permissions(send_messages=True, read_messages=True, add_reactions=True, administrator=False,
                            attach_files=True, ban_members=False, change_nickname=True, connect=True,
                            create_instant_invite=False, deafen_members=False, embed_links=True, external_emojis=True,
                            kick_members=False, manage_channels=False, manage_emojis=False, manage_guild=False,
                            manage_messages=False, manage_nicknames=True, manage_permissions=False, manage_roles=False,
                            manage_webhooks=False, mention_everyone=True, move_members=False, mute_members=False,
                            priority_speaker=False, read_message_history=True, send_tts_messages=True, speak=True,
                            stream=True, use_external_emojis=True, use_voice_activation=True, view_audit_log=False,
                            view_guild_insights=False)
prefix = '.'
chat_id = 773951770485325875
human_id = 773952519256014890
bot_id = 813379609499533353
