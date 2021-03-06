import discord
from discord.ext import commands
from helpers import db
from datetime import datetime, timedelta
import random


# Check if User Has Been Initialized with Scales
def has_scales(member: discord.Member):
    # Query Database
    with db.cursor() as cursor:
        sql = "SELECT 1 as `has_scales` FROM scales WHERE `username` = %s"
        cursor.execute(sql, (str(member),))
        entry = cursor.fetchone()
        cursor.close()

    # Return the Result (True/False)
    return entry['has_scales'] == 1


# Initialize User with Scales
def start_scales(member: discord.Member):

    if not has_scales(member):
        # Initialize to Zero
        with db.cursor() as cursor:
            sql = "INSERT INTO scales (`username`) VALUES (%s)"
            cursor.execute(sql, (str(member),))
            db.commit()
            cursor.close()


# Get User's Current Scales
def get_scales(member: discord.Member):
    # Query Database
    with db.cursor() as cursor:
        sql = "SELECT `total` FROM scales WHERE `username` = %s"
        print(str(member))
        cursor.execute(sql, (str(member),))
        entry = cursor.fetchone()
        cursor.close()


    # Return the Number of Scales
    if entry['total'] is not None:
        return entry['total']
    else:
        return 0


# Add Scales to User's Total
def add_scales(member: discord.Member, scales: int):

    # Get Users Current Scales
    current_scales = get_scales(member)
    new_scales = current_scales + scales

    # Give Points to User
    with db.cursor() as cursor:
        sql = "UPDATE scales SET `total` = %s WHERE username = %s"
        cursor.execute(sql, (new_scales, str(member)))
        db.commit()
        cursor.close()


# Used for Roulette
allowed_bets = ["even", "odd", "red", "black"]
dictionary_even_odd = {}
for i in list(range(0, 37)):
    allowed_bets.append(str(i))
    if i == 0:
        dictionary_even_odd[i] = "zero"
    elif i % 2 == 0:
        dictionary_even_odd[i] = "even"
    else:
        dictionary_even_odd[i] = "odd"
dictionary_red_black = {}
red = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
for i in list(range(0, 37)):
    if i == 0:
        dictionary_red_black[i] = "none"
    elif i in red:
        dictionary_red_black[i] = "red"
    else:
        dictionary_red_black[i] = "black"


# ********************************************** #
# GROUPED COMMANDS : SCALES ******************** #
# ********************************************** #

class Scales:
    def __init__(self, bot):
        self.bot = bot

    # COMMAND: !daily
    @commands.command(name='daily', pass_context=True)
    async def daily_scales(self, ctx):
        """Allows users to claim their daily scales."""

        # Is the user initialized?
        member = ctx.message.author
        if not has_scales(member):
            start_scales(member)

        # Has the user already claimed scales today?
        today = datetime.now()
        today_date = today.date()

        # Get User's Last Claim Date
        with db.cursor() as cursor:
            sql = "SELECT `last_claimed_date` FROM scales WHERE username = %s"
            cursor.execute(sql, (str(member),))
            result = cursor.fetchone()
            db.commit()
            cursor.close()
        if result['last_claimed_date'] is not None:
            last_date = datetime.strptime(str(result['last_claimed_date']), "%Y-%m-%d").date()
        else:
            last_date = today_date - timedelta(1)

        # If they haven't claimed today, determine how many scales they should get

        if last_date >= today_date:
            await self.bot.say("{0.mention}, you already claimed scales today!".format(member))
            return

        # Determine number of points to award
        added_scales = random.randint(1, 5)

        # See if they will get double points
        if random.randint(1, 100) == random.randint(1, 100):
            added_scales *= 2

        # They only appear lucky if they get more than 5
        if added_scales > 5:
            bonus = True
        else:
            bonus = False

        # Grant the Scales to the User
        try:
            add_scales(member, added_scales)
            with db.cursor() as cursor:
                sql = "UPDATE scales SET `last_claimed_date` = %s WHERE `username` = %s"
                cursor.execute(sql, (datetime.strftime(today, "%Y-%m-%d"), str(member)))
                db.commit()
                cursor.close()
        except Exception as e:
            await self.bot.say("{0.mention}, there was an error awarding you your scales. ".format(member) + str(e))
            return

        # Send Message
        if bonus:
            await self.bot.say("{0.mention}, you got **lucky** and claimed **{1}** "
                               "<:clifford_scales:303675725527908353> (scales) today!".format(member, added_scales))
        else:
            await self.bot.say("{0.mention}, you claimed **{1}** <:clifford_scales:303675725527908353> (scales) today!"
                               .format(member, added_scales))

    # COMMAND: !scales
    @commands.command(name='scales', pass_context=True)
    async def user_scales(self, ctx):
        """Display's a users current scales."""

        member = ctx.message.author

        # Display User's Scales
        if has_scales(member):
            scales = get_scales(member)
            await self.bot.say("{0.mention}, you currently have **{1}** <:clifford_scales:303675725527908353> (scales)"
                               .format(member, scales))
        else:
            await self.bot.say("{0.mention}, you do not have any <:clifford_scales:303675725527908353> (scales)"
                               .format(member))

    # COMMAND: !giftscales
    @commands.command(name='giftscales', pass_context=True)
    async def gift_scales(self, ctx, give_amount: int, member_to: discord.Member):
        """Gift some of your scales to a friend."""

        member_from = ctx.message.author
        member_from_scales = get_scales(member_from)

        # Make Sure Member To Exists
        if not member_to:
            await self.bot.say("{0.mention}, you must supply a valid user on this server.".format(member_from))
            return

        # Prevent Stealing
        if give_amount < 0:
            await self.bot.say("{0.mention}, you cannot steal scales, you thief!".format(member_from))
            return

        if give_amount <= member_from_scales:
            add_scales(member_from, (-1 * give_amount))
            add_scales(member_to, give_amount)
            await self.bot.say("{0.mention}, you gifted **{1}** of your <:clifford_scales:303675725527908353> (scales) "
                               "to {2.mention}! How kind!".format(member_from, give_amount, member_to))
        else:
            await self.bot.say("{0.mention}, you do not have enough <:clifford_scales:303675725527908353> (scales) to "
                               "give {1.mention} that many!".format(member_from, member_to))

    # COMMAND: !promote
    @commands.command(name='promote', pass_context=True)
    async def promote_user(self, ctx):
        """Promote yourself to the next highest rank if you have enough scales. Knight requires Squire and 2000 scales, Zealot requires Knight and 8000 scales."""

        # Define member and server
        member = ctx.message.author
        server = ctx.message.server

        # Define Roles
        squire = discord.utils.get(server.roles, name='Squire')
        knight = discord.utils.get(server.roles, name='Knight')
        zealot = discord.utils.get(server.roles, name='Zealot')

        # Current Information
        current_scales = get_scales(member)
        current_roles = member.roles
        print(current_roles)

        # Promote based on Role and Scales
        try:
            if squire in member.roles:
                if current_scales >= 500:
                    add_scales(member, -500)
                    new_roles = [knight if x == squire else x for x in current_roles]
                    await self.bot.replace_roles(member, *new_roles)
                    await self.bot.say("{0.mention}, you have been promoted from **Squire** to **Knight** at the cost "
                                       "of 500 <:clifford_scales:303675725527908353> (scales). Congrats!"
                                       .format(member))
                    return
                else:
                    await self.bot.say("{0.mention}, you do not have enough <:clifford_scales:303675725527908353> "
                                       "(scales) for this promotion. **Knight** requires 500 scales; you have {1} "
                                       "scales.".format(member, current_scales))
            elif knight in member.roles:
                if current_scales >= 2000:
                    add_scales(member, -2000)
                    new_roles = [zealot if x == knight else x for x in current_roles]
                    await self.bot.replace_roles(member, *new_roles)
                    await self.bot.say("{0.mention}, you have been promoted from **Knight** to **Zealot** at the cost "
                                       "of 2000 <:clifford_scales:303675725527908353> (scales). Congrats!"
                                       .format(member))
                    return
                else:
                    await self.bot.say("{0.mention}, you do not have enough <:clifford_scales:303675725527908353> "
                                       "(scales) for this promotion. **Zealot** requires 2000 scales; you have {1} "
                                       "scales.".format(member, current_scales))
            elif zealot in member.roles:
                await self.bot.say("{0.mention}, you are already the highest member rank, **Zealot**! You cannot be "
                                   "promoted further.".format(member))
                return
            else:
                await self.bot.say("{0.mention}, you must be registered before you can be promote! Type `!register` to "
                                   "become a **Squire**!".format(member))
                return
        except Exception as e:
            await self.bot.say("There was an error promoting: " + str(e))

    # COMMAND !buy
    @commands.command(name='buy', pass_context=True, aliases=['purchase'])
    async def buy_group(self, ctx, group: int = 0):
        """Buy a special group from the list! Only 1-6 Available for Purchase."""

        # Set Basic Stuff
        member = ctx.message.author
        server = ctx.message.server
        current_scales = get_scales(member)

        # Dictionary for Groups
        store = {}
        allowed = [1, 2, 3, 4, 5, 6]
        store[1] = discord.utils.get(server.roles, name='Store 01 - Blue')
        store[2] = discord.utils.get(server.roles, name='Store 02 - Fuchsia')
        store[3] = discord.utils.get(server.roles, name='Store 03 - Green')
        store[4] = discord.utils.get(server.roles, name='Store 04 - Orange')
        store[5] = discord.utils.get(server.roles, name='Store 05 - Teal')
        store[6] = discord.utils.get(server.roles, name='Store 06 - Yellow')

        # Was a Group Entered?
        if group not in allowed or group is None:
            await self.bot.say("Available groups for purchase (500 scales) include: \n"
                               "**(01) Blue** - Hex: #3498DB \n"
                               "**(02) Fuchsia** - Hex: #E91E63 \n"
                               "**(03) Green** - Hex: #07A700 \n"
                               "**(04) Orange** - Hex: #E05203 \n"
                               "**(05) Teal** - Hex: #1ABC9C \n"
                               "**(06) Yellow** - Hex: #F1C40F")
        else:
            if current_scales >= 250:
                add_scales(member, -250)
                await self.bot.add_roles(member, store[group])
                await self.bot.say("{0.mention}, you have successfully purchased your new color group!".format(member))
            else:
                await self.bot.say("{0.mention}, you do not have enough scales to purchase a color group.".format(member))

    # COMMAND: !roulette
    @commands.command(name='roulette', pass_context=True)
    async def scales_roulette(self, ctx, bet_amount: int, bet_on: str):
        """Gamble some scales on Roulette! Allows only red/black, odd/even, or single number bets."""

        member = ctx.message.author

        # User must have scales
        if not has_scales(member):
            await self.bot.say("{0.mention}, you must have scales to play Roulette!".format(member))
            return

        # User must have scales to cover the bet.
        if bet_amount > get_scales(member):
            await self.bot.say("{0.mention}, you cannot bet more scales than you have!".format(member))
            return

        # Bet type must be allowed
        if bet_on not in allowed_bets:
            await self.bot.say("{0.mention}, bets must be *red*, *black*, *even*, *odd*, or a number 0-36."
                               .format(member))
            return

        # We Have the Scales, Roll!
        roll_result = random.randint(0, 36)
        if dictionary_red_black[roll_result] == "red":
            color = "Red"
        elif dictionary_red_black[roll_result] == "black":
            color = "Black"
        else:
            color = "Green"
        await self.bot.say(":game_die: The roulette wheel landed on **{0} {1}**! :slot_machine:"
                           .format(roll_result, color))

        # Set Payouts and Whatnot
        win = False
        scales_won = (bet_amount * -1)
        if (bet_on == "red" and dictionary_red_black[roll_result] == "red") or \
           (bet_on == "black" and dictionary_red_black[roll_result] == "black") or \
           (bet_on == "even" and dictionary_even_odd[roll_result] == "even") or \
           (bet_on == "odd" and dictionary_even_odd[roll_result] == "odd"):
            win = True
            scales_won = bet_amount
            payout_rate = "1:1"
        elif bet_on == str(roll_result):
            win = True
            scales_won = (bet_amount * 35)
            payout_rate = "35:1"

        # Finish and Output Message
        try:
            add_scales(member, scales_won)
            if win:
                await self.bot.say("{0.mention}, you won **{1}** <:clifford_scales:303675725527908353> (scales) playing"
                                   " Roulette! Payout for your bet was {2}.".format(member, scales_won, payout_rate))
            else:
                await self.bot.say("{0.mention}, you lost your scales <:clifford_scales:303675725527908353>."
                                   .format(member))
        except Exception as e:
            await self.bot.say("There was an error adding scales: " + str(e))


def setup(bot):
    bot.add_cog(Scales(bot))
