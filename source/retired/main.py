import discord
from discord.ext import commands
import random
import MySQLdb

# ********************************************** #
# DEFINITIONS ********************************** #
# ********************************************** #

# Bot Description
description = '''Official Zealot Gaming Discord bot!'''

# Define Bot
bot = commands.Bot(command_prefix='!', description='Official Zealot Gaming Discord Bot')

# Define MySQL DB and Cursor Object
db = MySQLdb.connect(host="localhost",
                     user="discord_secure",
                     passwd="password-here",
                     db="discord")


# ********************************************** #
# FUNCTIONS ************************************ #
# ********************************************** #

# Check for Game Abbreviations
def is_game_abv(game_abv: str):
    try:
        sql = "SELECT 1 FROM games WHERE `abv` = %s LIMIT 1"
        cur = db.cursor()
        result = cur.execute(sql, (game_abv,))
        cur.close()
    except Exception as e:
        print('Exception: ' + str(e))
        result = 0

    # If we got a result, true, else false
    return result == 1


# Check for Game Names
def is_game_name(game_name: str):
    try:
        sql = "SELECT 1 FROM games WHERE `name` = %s LIMIT 1"
        cur = db.cursor()
        result = cur.execute(sql, (game_name,))
        cur.close()
    except Exception as e:
        print('Exception: ' + str(e))
        result = 0

    # If we got a result, true, else false
    return result == 1


# Check for Staff Member Status
def is_staff(member: discord.Member):

    # Return True or False if User is a Staff Member
    return 'Staff' in [r.name for r in member.roles]


# ********************************************** #
# BOT EVENTS *********************************** #
# ********************************************** #

# Bot Start Event	
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.change_presence(game=discord.Game(name='Zealot Gaming'))


# Welcome Message
@bot.event
async def on_member_join(member):
    channel = bot.get_channel('108369515502411776')
    fmt = "Everyone welcome {0.mention} to Zealot Gaming! Have a great time here! :wink: " \
          "http://puu.sh/nG6Qe.wav".format(member)
    await bot.send_message(channel, fmt)


# Goodbye Message
@bot.event
async def on_member_remove(member):
    channel = bot.get_channel('108369515502411776')
    fmt = ":wave: Goodbye {0}, we're sad to see you go!".format(member.name)
    await bot.send_message(channel, fmt)


# ********************************************** #
# UN-GROUPED BOT COMMANDS ********************** #
# ********************************************** #

# COMMAND: !hello
@bot.command(pass_context=True)
async def hello(ctx):
    # we do not want the bot to reply to itself
    if ctx.message.author == bot.user:
        return
    else:
        msg = 'Hello {0.message.author.mention}'.format(ctx)
        await bot.send_message(ctx.message.channel, msg)


# COMMAND: !carlito
@bot.command()
async def carlito():
    """The legendary message of Carlito, maz00's personal cabana boy."""
    await bot.say("wew men :ok_hand::skin-tone-1: that's some good shit:100: some good shit :100: that's some good shit"
                  " right there :100: :ok_hand::skin-tone-1: right there :ok_hand::skin-tone-1: :100: sign me the FUCK "
                  "up:100: :100: :ok_hand::skin-tone-1: :eggplant:")


# COMMAND: !eightball
@bot.command(pass_context=True)
async def eightball(ctx, question: str):
    """Rolls a magic 8-ball to answer any question you have."""

    if question is None:
        await bot.say('{0.message.author.mention}, you did not ask a question.'.format(ctx))
        return

    # Answers List (Classic 8-Ball, 20 Answers)
    answers = ['It is certain.',
               'It is decidedly so',
               'Without a doubt.',
               'Yes, definitely.',
               'You may rely on it.',
               'As I see it, yes.',
               'Most likely.',
               'Outlook good.',
               'Yes.',
               'Signs point to yes.',
               'Reply hazy; try again.',
               'Ask again later.',
               'Better not tell you now.',
               'Cannot predict now.',
               'Concentrate, then ask again.',
               'Do not count on it.',
               'My reply is no.',
               'My sources say no.',
               'Outlook not so good.',
               'Very doubtful.']

    # Send the Answer
    await bot.say('{0.message.author.mention}, '.format(ctx) + random.choice(answers))


# COMMAND: !roll
@bot.command()
async def roll(dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)


# COMMAND: !choose
@bot.command()
async def choose(*choices: str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))


# COMMAND: !joined
@bot.command()
async def joined(member: discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))


# COMMAND: !get_roles
@bot.command()
async def get_roles(member: discord.Member):
    """Lists a User's Roles"""

    total = 0
    role_list = ''

    for role in member.roles:
        if total > 0:
            role_list += ', '
        role_list += str(role)
        total += 1

    await bot.say('{0.name} is a member of these roles: '.format(member) + role_list)


# COMMAND: !get_channel_id
@bot.command(pass_context=True)
async def get_channel_id(ctx):
    """Lists the ID of the channel the message is sent in."""

    # Is the user allowed? (Must be staff)
    if not is_staff(ctx.message.author):
        await bot.say('{0.mention}, you must be a staff member to use this command.'.format(ctx.message.author))
        return

    await bot.say('Channel ID is {0.id}'.format(ctx.message.channel))


# COMMAND: !join
@bot.command(pass_context=True)
async def join(ctx, *, role_name: str):
    """Allows a user to join a public group."""

    # List of Allowed Public Roles
    allowed_roles = ['Europe',
                     'North America',
                     'Oceania',
                     'Overwatch',
                     'League of Legends',
                     'Co-op',
                     'Minna-chan']

    if role_name not in allowed_roles:
        await bot.say('{0.mention}, you may only join allowed public groups.'.format(ctx.message.author))
        return

    # Define role, then add role to member.
    try:
        role = discord.utils.get(ctx.message.server.roles, name=role_name)
        await bot.add_roles(ctx.message.author, role)
    except Exception as e:
        await bot.send_message(ctx.message.channel, "{0.mention}, there was an error getting the roster for you. "
                                                    "I'm sorry! : ".format(ctx.message.author) + str(e))
        return

    # Success Message
    await bot.say('{0.mention}, you have successfully been added to the group **{1}**.'
                  .format(ctx.message.author, role_name))


# ********************************************** #
# GROUPED COMMANDS : EVENTS ******************** #
# ********************************************** #

# COMMAND: !events
@bot.group(pass_context=True)
async def events(ctx):
    """Manage events and attendance!"""

    if ctx.invoked_subcommand is None:
        await bot.say('Invalid command passed. Must be *add*, *description*, *edit*, *register*, or *remove*.')


# COMMAND: !events add
@events.command(name='add', pass_context=True)
async def events_add(ctx, date: str, time: str, *, title: str):
    """Add an event to the Events List!
       Date **must** be in YYYY/MM/DD format. Time **must** be in UTC."""

    # Set #events Channel
    event_channel = bot.get_channel('296694692135829504')

    # Is the user allowed? (Must be staff)
    if not is_staff(ctx.message.author):
        await bot.say('{0.mention}, you must be a staff member to use this command.'.format(ctx.message.author))
        return

    # Make sure we have a date.
    if date is None:
        await bot.say('Error: You must enter a date in YYYY/MM/DD format.')
        return

    # Make sure we have a time.
    if time is None:
        await bot.say('Error: You must enter a time in HH:MM format in UTC timezone.')
        return

    # Make sure we have a title.
    if date is None:
        await bot.say('Error: You must enter a title for the event.')
        return

    # Add Event to Database
    try:
        sql = "INSERT INTO events (`date`,`time`,`title`) VALUES (%s, %s, %s)"
        cur = db.cursor()
        cur.execute(sql, (date, time, title))
        event_id = cur.lastrowid

        msg_text = "**Title**: {0} \n**Event ID**: {1} \n**Date & Time**: {2} at {3} (UTC)"

        # Add Message to Events Channel and Save Message ID
        message = await bot.send_message(event_channel, msg_text.format(title, event_id, date, time))

        cur.execute('UPDATE events SET `message_id` = %s WHERE `event_id` = %s', (message.id, event_id))
        db.commit()
        cur.close()

    except Exception as e:
        await bot.say('{0.mention}, there was an error adding the event to the list. '.format(ctx.message.author)
                      + str(e))
        return

    # Success Message
    await bot.say('{0.mention}, your event was successfully added. The event ID is: {1}.'
                  .format(ctx.message.author, event_id))


# COMMAND: !events description
@events.command(name='description', pass_context=True)
async def events_description(ctx, event_id: int, *, desc: str):
    """Adds a Description to an Event Given an Event ID."""

    # EVENT CHANNEL ID: 296694692135829504
    event_channel = bot.get_channel('296694692135829504')

    # Is the user allowed? (Must be staff)
    if not is_staff(ctx.message.author):
        await bot.say('{0.mention}, you must be a staff member to use this command.'.format(ctx.message.author))
        return

    # Make sure we have a date.
    if event_id is None:
        await bot.say('Error: You must enter an event ID. Check the #events channel.')
        return

    # Make sure we have a date.
    if desc is None:
        await bot.say('Error: You must enter a description.')
        return

    try:
        sql = "UPDATE events SET `description` = %s WHERE `event_id` = %s"
        cur = db.cursor()
        cur.execute(sql, (desc, event_id))
        cur.execute("SELECT `message_id` FROM events WHERE `event_id` = %s", (event_id,))
        msg_id = cur.fetchone()
        message = await bot.get_message(event_channel, msg_id[0])

        msg_text = message.content + " \n**Description**: {0}".format(desc)

        # Update Message in Events Channel with Description
        await bot.edit_message(message, msg_text)

        db.commit()
        cur.close()
    except Exception as e:
        await bot.say('{0.mention}, there was an error adding a description to the event. '.format(ctx.message.author)
                      + str(e))
        return

    # Success Message
    await bot.say('{0.mention}, the event was successfully updated with a description.'.format(ctx.message.author))


# ********************************************** #
# GROUPED COMMANDS : GAMES ********************* #
# ********************************************** #

# COMMAND: !games
@bot.group(pass_context=True)
async def games(ctx):
    """Manages games for the roster."""

    if ctx.invoked_subcommand is None:
        await bot.say('Invalid command passed. Must be *add*, *edit*, *list*, or *remove*.')


# COMMAND: !games add
@games.command(name='add', pass_context=True)
async def games_add(ctx, game_abv: str, *, game_name: str):
    """Adds a game to the list of games available in the roster."""

    # Is the user allowed? (Must be staff)
    if not is_staff(ctx.message.author):
        await bot.say('{0.mention}, you must be a staff member to use this command.'.format(ctx.message.author))
        return

    # Does Game Abbreviation Exist?
    if is_game_abv(game_abv):
        await bot.say('{0.mention}, this abbreviation is already in use.'.format(ctx.message.author))
        return

    # Does Game Name Exist?
    if is_game_name(game_name):
        await bot.say('{0.mention}, this game is already in the list.'.format(ctx.message.author))
        return

    # Handle Database
    try:
        sql = "INSERT INTO games (`abv`,`name`) VALUES (%s, %s)"
        cur = db.cursor()
        cur.execute(sql, (game_abv, game_name))
        db.commit()
        cur.close()
    except Exception as e:
        await bot.say('{0.mention}, there was an error adding the game to the games list. '.format(ctx.message.author)
                      + str(e))
        return

    # Display Success Message
    await bot.say('{0.mention}, the game was successfully added to the games list!'.format(ctx.message.author))


# COMMAND: !games edit
@games.command(name='edit', pass_context=True)
async def games_edit(ctx, game_abv: str, *, game_name: str):
    """Updates a game in the list of games available in the roster."""

    # Is the user allowed? (Must be staff)
    if not is_staff(ctx.message.author):
        await bot.say('{0.mention}, you must be a staff member to use this command.'.format(ctx.message.author))
        return

    # Is there anything to update?
    if not (is_game_abv(game_abv) or is_game_name(game_name)):
        await bot.say('{0.mention}, either the abbreviation of game must exist to update.'.format(ctx.message.author))
        return

    # Handle Database
    try:
        sql = "UPDATE games SET `abv` = %s, `name = %s WHERE `abv` = %s OR `name` = %s"
        cur = db.cursor()
        cur.execute(sql, (game_abv, game_name, game_abv, game_name))
        db.commit()
        cur.close()
    except Exception as e:
        await bot.say('{0.mention}, there was an error updating the game in the games list. '.format(ctx.message.author)
                      + str(e))
        return

    # Display Success Message
    await bot.say('{0.mention}, the game was successfully updated in the games list!'.format(ctx.message.author))


# COMMAND: !games remove
@games.command(name='remove', pass_context=True)
async def games_remove(ctx, *, game_or_abv: str):
    """Removes a game from the list of games available in the roster."""

    # Is the user allowed? (Must be staff)
    if not is_staff(ctx.message.author):
        await bot.say('{0.mention}, you must be a staff member to use this command.'.format(ctx.message.author))
        return

    # Is there anything to update?
    if not (is_game_abv(game_or_abv) or is_game_name(game_or_abv)):
        await bot.say('{0.mention}, either the abbreviation of game must exist to update.'.format(ctx.message.author))
        return

    # Handle Database
    try:
        sql = "DELETE FROM games WHERE `abv` = %s OR `name` = %s"
        cur = db.cursor()
        cur.execute(sql, (game_or_abv, game_or_abv))
        db.commit()
        cur.close()
    except Exception as e:
        await bot.say("{0.mention}, there was an error deleting the game from the games list."
                      " ".format(ctx.message.author) + str(e))
        return

    # Display Success Message
    await bot.say('{0.mention}, the game was successfully deleted from the games list!'.format(ctx.message.author))


# COMMAND: !games list
@games.command(name='list', pass_context=True)
async def games_list(ctx):
    """Sends a message to the user with the current games and abbreviations for use in the roster."""

    # Handle Database
    try:
        sql = "SELECT `abv`, `name` FROM games ORDER BY `name`"
        cur = db.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
    except Exception:
        await bot.send_message(ctx.message.channel, "{0.mention}, there was an error getting the list of games for you."
                                                    " I'm sorry!".format(ctx.message.author))
        return

    # Create Variables for Embed Table
    abvs = ''
    names = ''

    for row in result:
        abvs += (row[0] + '\n')
        names += (row[1] + '\n')

    # Create Embed Table
    embed = discord.Embed()
    embed.add_field(name="Abbreviation", value=abvs, inline=True)
    embed.add_field(name="Game Name", value=names, inline=True)

    # Send Table to User Privately
    await bot.send_message(ctx.message.channel, embed=embed)


# ********************************************** #
# GROUPED COMMANDS : ROSTER ******************** #
# ********************************************** #

# COMMAND: !roster
@bot.group(pass_context=True)
async def roster(ctx):
    """Handles Roster Management."""

    if ctx.invoked_subcommand is None:
        await bot.say('Invalid roster command passed. Must be *add*, *edit*, *list*, or *remove*.')


# COMMAND: !roster add
@roster.command(name='add', pass_context=True)
async def roster_add(ctx, game_abv: str, *, ign: str):
    """Adds username to roster.
       User a game abbreviation from the games list. Only one entry per game. Include all in-game names if necessary."""

    username = str(ctx.message.author)

    # Does Game Abbreviation Exist?
    if not is_game_abv(game_abv):
        await bot.say('{0.mention}, this abbreviation does not exist. Use !games display for a list of acceptable game '
                      'abbreviations.'.format(ctx.message.author))
        return

    # Handle Database
    try:
        sql = "INSERT INTO roster (`discord_account`,`game_abv`,`game_account`) VALUES (%s, %s, %s)"
        cur = db.cursor()
        cur.execute(sql, (username, game_abv, ign))
        db.commit()
        cur.close()
    except Exception:
        await bot.say('{0.message.author.mention}, there was an error adding your information to the roster.'.format(ctx))
        return

    # Display Success Message
    await bot.say('{0.message.author.mention}, your information was successfully added to the roster!'.format(ctx))


# COMMAND: !roster edit
@roster.command(name='edit', pass_context=True)
async def roster_edit(ctx, game_abv: str, *, ign: str):
    """Updates a roster entry for a specific game.
       If the either Game Name or your in-Game Name have spaces, put them in quotes."""

    username = str(ctx.message.author)

    # Does Game Abbreviation Exist?
    if not is_game_abv(game_abv):
        await bot.say('{0.mention}, this abbreviation does not exist. Use !games display for a list of acceptable game'
                      ' abbreviations.'.format(ctx.message.author))
        return

    # Handle Database
    try:
        sql = "UPDATE roster SET `game_account` = %s WHERE `discord_account` = %s AND `game_abv` = %s"
        cur = db.cursor()
        cur.execute(sql, (ign, username, game_abv))
        db.commit()
        cur.close()
    except Exception:
        await bot.say('{0.message.author.mention}, there was an error updating your roster information.'.format(ctx))
        return

    # Display Success Message
    await bot.say('{0.message.author.mention}, your roster information was successfully updated!'.format(ctx))


# COMMAND: !roster remove
@roster.command(name='remove', pass_context=True)
async def roster_remove(ctx, game_abv: str, *, ign: str):
    """Removes a user's entries in the roster for the specified game."""

    username = str(ctx.message.author)

    # Does Game Abbreviation Exist?
    if not is_game_abv(game_abv):
        await bot.say('{0.mention}, this abbreviation does not exist. Use !games display for a list of acceptable '
                      'game abbreviations.'.format(ctx.message.author))
        return

    # Handle Database
    try:
        sql = "DELETE FROM roster WHERE `discord_account` = %s AND `game_abv` = %s AND `game_account` = %s"
        cur = db.cursor()
        cur.execute(sql, (username, game_abv, ign))
        db.commit()
        cur.close()
    except Exception:
        await bot.say('{0.message.author.mention}, there was an error deleting your roster information.'.format(ctx))
        return

    # Display Success Message
    await bot.say('{0.message.author.mention}, your roster information was successfully deleted!'.format(ctx))


# COMMAND: !roster list
@roster.command(name='list', pass_context=True)
async def roster_list(ctx, game_abv: str):
    """Sends a message to the user with the current roster for the specified game."""

    # Does Game Abbreviation Exist?
    if not is_game_abv(game_abv):
        await bot.say('{0.mention}, this abbreviation does not exist. Use !games display for a list of acceptable game '
                      'abbreviations.'.format(ctx.message.author))
        return

    # Handle Database
    try:
        sql = "SELECT `discord_account`, `game_account` FROM roster WHERE `game_abv` = %s ORDER BY `discord_account`"
        cur = db.cursor()
        cur.execute(sql, (game_abv,))
        result = cur.fetchall()
        cur.close()
    except Exception:
        await bot.send_message(ctx.message.channel, "{0.mention}, there was an error getting the roster for you. "
                                                    "I'm sorry!".format(ctx.message.author))
        return

    # Create Variables for Embed Table
    accounts = ''
    names = ''

    for row in result:
        accounts += (row[0] + '\n')
        names += (row[1] + '\n')

    # Create Embed Table
    embed = discord.Embed()
    embed.add_field(name="Discord Account", value=accounts, inline=True)
    embed.add_field(name="In-Game Name", value=names, inline=True)

    # Send Table to Channel
    await bot.send_message(ctx.message.channel, embed=embed)


# ********************************************** #
# GROUPED COMMANDS : RECRUIT ******************* #
# ********************************************** #

# COMMAND: !recruit
@bot.group(pass_context=True)
async def recruit(ctx):
    """Handles Recruitment Post and Invites Management."""

    if ctx.invoked_subcommand is None:
        await bot.say('Invalid recruitment command passed. Must be *add*, *edit*, *invite*, *list*, or *remove*.')


# COMMAND: !recruit add
@recruit.command(name='add', pass_context=True)
async def recruit_add(ctx, game_abv: str, *, link: str):
    """Adds recruitment post link to the recruitment list. Use a game abbreviation from the games list."""

    # Is the user allowed? (Must be staff)
    if not is_staff(ctx.message.author):
        await bot.say('{0.mention}, you must be a staff member to use this command.'.format(ctx.message.author))
        return

    # Does Game Abbreviation Exist?
    if not is_game_abv(game_abv):
        await bot.say(
            '{0.mention}, this abbreviation does not exist. Use !games display for a list of acceptable game '
            'abbreviations.'.format(ctx.message.author))
        return

    # Handle Database
    try:
        sql = "INSERT INTO recruitment (`game`,`link`) VALUES (%s, %s)"
        cur = db.cursor()
        cur.execute(sql, (game_abv, link))
        db.commit()
        cur.close()
    except Exception:
        await bot.say(
            '{0.message.author.mention}, there was an error adding your recruitment link to the list.'.format(ctx))
        return

    # Display Success Message
    await bot.say('{0.message.author.mention}, your information was successfully added to the recruitment '
                  'posts list!'.format(ctx))


# COMMAND: !recruit edit
@recruit.command(name='edit', pass_context=True)
async def roster_edit(ctx, entry_id: int, *, link: str):
    """Updates a recruitment post entry with the specified entry ID."""

    # Is the user allowed? (Must be staff)
    if not is_staff(ctx.message.author):
        await bot.say('{0.mention}, you must be a staff member to use this command.'.format(ctx.message.author))
        return

    # Handle Database
    try:
        sql = "UPDATE recruitment SET `link` = %s WHERE `entry_id` = %s"
        cur = db.cursor()
        cur.execute(sql, (link, entry_id))
        db.commit()
        cur.close()
    except Exception:
        await bot.say('{0.message.author.mention}, there was an error updating the specified '
                      'recruitment entry.'.format(ctx))
        return

    # Display Success Message
    await bot.say('{0.message.author.mention}, the recruitment entry was successfully updated!'.format(ctx))


# COMMAND: !recruit remove
@recruit.command(name='remove', pass_context=True)
async def recruit_remove(ctx, entry_id: int):
    """Removes an entry for the recruitment posts list with the specified entry ID."""

    # Is the user allowed? (Must be staff)
    if not is_staff(ctx.message.author):
        await bot.say('{0.mention}, you must be a staff member to use this command.'.format(ctx.message.author))
        return

    # Handle Database
    try:
        sql = "DELETE FROM recruitment WHERE `entry_id` = %s"
        cur = db.cursor()
        cur.execute(sql, (entry_id,))
        db.commit()
        cur.close()
    except Exception:
        await bot.say('{0.message.author.mention}, there was an error deleting the specified '
                      'recruitment entry.'.format(ctx))
        return

    # Display Success Message
    await bot.say('{0.message.author.mention}, the recruitment entry was successfully deleted!'.format(ctx))


# COMMAND: !recruit list
@recruit.command(name='list', pass_context=True)
async def recruit_list(ctx):
    """Lists all recruitment post entries in the system."""

    # Handle Database
    try:
        sql = "SELECT * FROM recruitment ORDER BY `game`"
        cur = db.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
    except Exception:
        await bot.send_message(ctx.message.channel, "{0.mention}, there was an error getting the recruitment list "
                                                    "for you. I'm sorry!".format(ctx.message.author))
        return

    # Create Variables for Embed Table
    entries = ''
    game_abvs = ''
    links = ''

    for row in result:
        entries += (row[0] + '\n')
        game_abvs += (row[1] + '\n')
        links += (row[2] + '\n')

    # Create Embed Table
    embed = discord.Embed()
    embed.add_field(name="ID", value=entries, inline=True)
    embed.add_field(name="Game", value=game_abvs, inline=True)
    embed.add_field(name="Link", value=links, inline=True)

    # Send Table to Channel
    await bot.send_message(ctx.message.channel, embed=embed)


# COMMAND: !recruit invite
@recruit.command(name='invite')
async def recruit_invite(duration: int):
    """Provides an invite link to the Discord server. Set duration to 0 for permanent invite."""

    # Default Duration 30 Minutes, Else Convert to Minutes
    if duration is None:
        duration = 1800
    else:
        duration *= 60

    # WELCOME CHANNEL ID: 141622052133142529
    welcome_channel = bot.get_channel('141622052133142529')

    # Create the Invite
    new_invite = await bot.create_invite(welcome_channel, max_age=duration)

    # Send Message with Invite Link
    await bot.say('Your newly generated invite link is: {0.url}'.format(new_invite))


# ********************************************** #
# MODERATOR COMMANDS *************************** #
# ********************************************** #

# COMMAND: !give_role
@bot.command(pass_context=True)
async def give_role(ctx, username: str, *, role_name: str):
    """Assigns a role to a user."""

    # List of Roles Staff Can Add To.
    allowed_roles = ['Europe',
                     'North America',
                     'Oceania',
                     'Overwatch',
                     'League of Legends',
                     'Co-op',
                     'Minna-chan',
                     'Squire',
                     'Knight',
                     'Zealot']

    # Is the user allowed? (Must be Staff)
    if not is_staff(ctx.message.author):
        await bot.say('{0.mention}, you must be a staff member to use this command.'.format(ctx.message.author))
        return

    if role_name not in allowed_roles:
        await bot.say('{0.mention}, you may only assign users to public roles, Guest, or Registered Member'
                      .format(ctx.message.author))
        return

    # Define role, then add role to member.
    try:
        role = discord.utils.get(ctx.message.server.roles, name=role_name)
        user = discord.utils.get(ctx.message.server.members, name=username)
        await bot.add_roles(user, role)
    except Exception as e:
        await bot.send_message(ctx.message.channel, "{0.mention}, there was an granting the role to the user."
                                                    " ".format(ctx.message.author) + str(e))
        return

    # Success Message
    await bot.say('{0.mention}, you have successfully added **{1}** to the group **{2}**'
                  '.'.format(ctx.message.author, username, role_name))


# COMMAND: !kick
@bot.command(name='kick', pass_context=True)
async def mod_kick(ctx, username: str, *, reason: str):
    """Kicks a user from the server."""

    # User must be a staff member
    if not is_staff(ctx.message.author):
        await bot.say('{0.mention}, you must be a staff member to use this command.'.format(ctx.message.author))
        return

    # Add to DB and Post Message
    try:
        # Variables Needed
        member = discord.utils.get(ctx.message.server.members, name=username)
        staffer = ctx.message.author

        # Handle Database
        sql = "INSERT INTO mod_log (`action`,`user`, `user_id`, `staff`, `staff_id`, reason) " \
              "VALUES ('kick', %s, %s, %s, %s, %s)"
        cur = db.cursor()
        cur.execute(sql, (str(member), member.id, str(staffer), staffer.id, reason))

        # Save Last Row ID
        case_id = cur.lastrowid

        # Insert Message
        log_channel = bot.get_channel('303262467205890051')
        msg_text = "**Case #{0}** | Kick :boot: \n**User**: {1} ({2}) " \
                   "\n**Moderator**: {3} ({4}) \n**Reason**: {5}"

        # Add Message to Events Channel and Save Message ID
        case_message = await bot.send_message(log_channel, msg_text.format(case_id, str(member), member.id, str(staffer), staffer.id, reason))
        cur.execute("UPDATE mod_log SET `message_id` = %s WHERE `case_id` = %s", (case_message.id, case_id))

        # Finish Database Stuff and Commit
        db.commit()
        cur.close()

        # Kick the Member
        await bot.kick(member)
    except Exception as e:
        await bot.send_message(ctx.message.channel, "{0.mention}, there was an error when kicking the user."
                                                    " ".format(ctx.message.author) + str(e))

    await bot.say("{0.mention}, the user was successfully kicked. A log entry has been added.".format(ctx.message.author))


# ********************************************** #
# START THE BOT ******************************** #
# ********************************************** #


# Run the Bot
bot.run('token-here')
