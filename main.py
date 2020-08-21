import random
import discord
import model
import dsctoken

client = discord.Client()
spot = ['試練', 'スカイフック', '調査キャンプ', '製錬所', 'カウントダウン', 'エピセンター', 'フラグメント', '列車庫', '溶岩湖', 'ハーベスター', '仕分け工場', 'ラバシティー', '火力発電所', 'ザ・ツリー', 'ザ・ドーム', '展望', '発射場', 'ブラストウォール', '間欠泉']

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.role_mentions:
        return
    
    overwrites = {
        message.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        message.guild.me: discord.PermissionOverwrite(view_channel=True)
    }

    for role in message.role_mentions:
        overwrites[role] = discord.PermissionOverwrite(view_channel=True)

    ctgr = await message.guild.create_category(random.choice(spot), overwrites=overwrites)
    tx_ch = await ctgr.create_text_channel(name='チャット')
    await ctgr.create_voice_channel(name='わいわい')

    model.add(str(message.guild.id), str(ctgr.id))

    await message.channel.send('{}を作りました。'.format(tx_ch.mention), delete_after=30)
    await check(message.guild, ctgr)

@client.event
async def on_voice_state_update(member, before, after):
    if after.channel is not None:
        return
    if before.channel.members:
        return
    ctgr = before.channel.category

    if ctgr is None:
        return

    db_ids = [ category.category_id for category in model.get_categories()]
    if str(ctgr.id) in db_ids:
        await delete_channel(ctgr)

async def delete_channel(ctgr):
    for channel in ctgr.channels:
        await channel.delete()
    ctgr_id = ctgr.id
    await ctgr.delete()
    model.delete_category(str(ctgr_id))

async def check(guild, ex_ctgr):
    for ctgr in guild.categories:
        if ctgr == ex_ctgr:
            continue
        db_ids = [ category.category_id for category in model.get_categories()]
        if str(ctgr.id) in db_ids:
            for vc in ctgr.voice_channels:
                if not vc.members:
                    await delete_channel(ctgr)


client.run(dsctoken.tkn)