import os
import discord
import random
from discord.ext import commands

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='$', intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")


@bot.event
async def on_ready():
    print("Atom is ready.")


async def give_remove_role(member: discord.Member, role: discord.Role):
    if role in member.roles:
        await member.remove_roles(role)
    elif role not in member.roles:
        await member.add_roles(role)

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    # do not process the bot's own messages
    if message.author == bot.user:
        return

    if not message.guild:
        studyTime = None
        for guild in bot.guilds:
            if guild.id == 740958427039268954:
                studyTime = guild
                break

        if message.content[:6] == "vent: " and message.author in studyTime.members:
            vent = discord.utils.get(studyTime.channels, id=746864872221966468)
            await vent.send(message.content[6:])
            await message.author.send("Message successfully moved to #vent")

            modlog = discord.utils.get(studyTime.channels, id=822349297915789352)
            await modlog.send(f'{message.author} - {message.author.id}\n{message.content[6:]}')

    # move verification pictures from vp-input to the staff-only channel vp-pending
    elif message.channel.id == 782844189456990298:
        if message.attachments != []:
            vpPending = discord.utils.get(message.guild.channels, id=782845929854205994)
            # sends the mention, content, and then the first picture they sent to #vp-pending
            image = await message.attachments[0].to_file()
            await vpPending.send(message.author.mention + ":\n" + message.content, file=image)

        await message.delete(delay=1)

    # assign major roles
    elif message.channel.id == 781280160828751902:
        if message.content.isnumeric():
            roleNumber = int(message.content)
            roles = message.guild.roles

            # limit usage to roles in between "Agricultural Business Management" and "Textile Technology"
            lowerBound = roles.index(discord.utils.get(message.guild.roles, id=781388693322858546))
            upperBound = roles.index(discord.utils.get(message.guild.roles, id=781388300149587989))

            if upperBound >= upperBound - roleNumber >= lowerBound:
                # get role based on position index
                # starts from top role, Agricultural Business Management, and moves to bottom role, Textile Technology
                requestedRole = roles[upperBound-roleNumber]
                await give_remove_role(message.author, requestedRole)
                await message.channel.send(f'Changed {message.author.nick}\'s status for the role "{requestedRole}"',
                                           delete_after=3)
            else:
                await message.channel.send(f'Index "{roleNumber}" is out of range.', delete_after=3)

        await message.delete(delay=3)

        
# helper method for verify_user
async def find_user_vp(member: discord.Member, channel: discord.TextChannel):
    # find the last sent message from {member} in {channel} if one exists
    messages = await channel.history().flatten()  # get the messages in {channel} as :list:
    for message in messages:
        if str(member.mention) in message.content:
            return message
    return None


# verifies members into NCSU Study Time by removing the role Unverified, Adding the role Member
# optionally changes the member's nickname
# sends an automated greeting message to #general upon successful verification
@bot.command(name="verify", aliases=["v"])
@commands.has_any_role('Manager', 'Corporate', 'CEO')
async def verify_user(ctx, member: discord.Member, nickname=None):
    # only attempts to verify if the passed member is actually in the server
    if member in ctx.guild.members:
        # get necessary roles
        unverifiedRole = discord.utils.get(ctx.guild.roles, id=752977608060436509)
        memberRole = discord.utils.get(ctx.guild.roles, id=766382355568525376)

        # get necessary channels
        general = discord.utils.get(ctx.guild.channels, id=740958427039268957)
        vpPending = discord.utils.get(ctx.guild.channels, id=782845929854205994)
        vpArchive = discord.utils.get(ctx.guild.channels, id=770117019709341716)

        # find {member}'s verification picture in #vp-pending
        vp = await find_user_vp(member, vpPending)

        if vp is not None:
            # move {vp}'s content and image to #vp-archive
            image = await vp.attachments[0].to_file()
            await vpArchive.send(vp.content, file=image)
            await vp.delete(delay=1)

            # verifies {member} by removing Unverified, adding Member, and changing nick to {nickname}
            if unverifiedRole in member.roles:
                await member.add_roles(memberRole)
                await member.remove_roles(unverifiedRole)

            # if a nickname is provided, changes {member}'s nickname to {nickname}
            if nickname is not None:
                await member.edit(nick=nickname)
                await ctx.send(f'Successfully verified {member} with the nickname "{nickname}"')
            else:
                await ctx.send(f'Successfully verified {member}')

            # list of possible greeting messages to be randomly chosen
            greetings = [f"Welcome to the server, {member.mention}!",
                         f"Welcome {member.mention}!",
                         f"Glad to have you, {member.mention}",
                         f"Hello and welcome to {member.mention}!",
                         f"{member.mention} just arrived! Say hi!",
                         f"{member.mention} is here to party!",
                         f"Welcome, {member.mention}. We've been expecting you.",
                         f"Swoooosh. {member.mention} just landed.",
                         f"{member.mention} just slid into the server.",
                         f"Oh shit, it's {member.mention}. Everyone hide!",
                         f"Hellooooo. Is it {member.mention} you're looking fooor.",
                         f"It's dangerous to go alone, {member.mention}. Good thing you're here now!",
                         f"Never gonna give {member.mention} up. Never gonna let {member.mention} down.",
                         f"It's {member.mention}! Praise the sun!",
                         f"A new challenger approaches: {member.mention}!",
                         f"Brace yourselves. {member.mention} just joined the server.",
                         f"A wild {member.mention} appeared!",
                         f"{member.mention} just joined. Everyone look busy!",
                         f"Hello there. General {member.mention}!",
                         f"{member.mention}, this is a Wendy's drive-thru",
                         f"Hi {member.mention}! ||GET OUT WHILE YOU STILL CAN||",
                         f"I hope you stay longer than @SevenYoshis#7432, {member.mention}",
                         f"Hey, {member.mention}. You're finally awake.",
                         f"You aren't a bug, {member.mention}, you're a feature!",
                         f"Wait, is that *the* {member.mention}?",
                         f"{member.mention} joined. Yipee.",
                         f"Hi {member.mention}! Make sure to pick up the Computer Science role at your earliest convenience!"]

            # sends an automated greeting message to #general upon succesful verification
            await general.send(random.choice(greetings))
        else:
            await ctx.send(f'Unable to locate a verification picture for {member}.')
    else:
        await ctx.send(f'{member} does not exist or is not a member of {ctx.guild.name}.')


async def find_category(ctx, categoryName):
    # try to match {categoryName} to a category in {ctx.guild}
    for category in ctx.guild.categories:
        if categoryName.lower() == category.name.lower():
            return category
    return None


@bot.command(name='archive', aliases=["a"])
@commands.has_role('CEO')
async def archive_text_category(ctx, categoryName, appendText):
    category = await find_category(ctx, categoryName)

    if category is not None:
        for channel in category.channels:
            # create new channel and sync its permissions to its {category}'s
            await ctx.guild.create_text_channel(name=channel.name, category=category, sync_permissions=True)

            # move to (archived) sC, rename, and sync permissions of original channel
            studyChannels = discord.utils.get(ctx.guild.categories, id=773996462262190090)
            await channel.edit(category=studyChannels, name=f'{appendText} - {channel.name}', sync_permissions=True)

        await ctx.send(f'Successfully archived the category "{category}"')
    else:
        await ctx.send(f'The category "{categoryName}" does not exist.')


bot.run(TOKEN)
