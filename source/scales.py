import discord
from discord.ext import commands
from helpers import db, is_staff
from datetime import datetime, timedelta
import random


# Check if User Has Been Initialized with Scales
def has_scales(member: discord.Member):
    # Query Database
    sql = "SELECT 1 FROM scales WHERE `username` = %s"
    cur = db.cursor()
    cur.execute(sql, (str(member),))
    entry = cur.fetchone()
    db.commit()
    cur.close()

    # Return the Result (True/False)
    if entry is not None:
        return entry[0] == 1
    else:
        return False


# Initialize User with Scales
def start_scales(member: discord.Member):

    if not has_scales(member):
        # Initialize to Zero
        sql = "INSERT INTO scales (`username`) VALUES (%s)"
        cur = db.cursor()
        cur.execute(sql, (str(member),))
        db.commit()
        cur.close()


# Get User's Current Scales
def get_scales(member: discord.Member):
    # Query Database
    sql = "SELECT `total` FROM scales WHERE `username` = %s"
    cur = db.cursor()
    cur.execute(sql, (str(member),))
    entry = cur.fetchone()
    db.commit()
    cur.close()

    # Return the Number of Scales
    if entry[0] is not None:
        return entry[0]
    else:
        return 0


# Add Scales to User's Total
def add_scales(member: discord.Member, scales: int):

    # Get Users Current Scales
    current_scales = get_scales(member)
    new_scales = current_scales + scales

    # Give Points to User
    sql = "UPDATE scales SET `total` = %s WHERE username = %s"
    cur = db.cursor()
    cur.execute(sql, (new_scales, str(member)))
    db.commit()
    cur.close()


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
        sql = "SELECT `last_claimed_date` FROM scales WHERE username = %s"
        cur = db.cursor()
        cur.execute(sql, (str(member),))
        result = cur.fetchone()
        db.commit()
        cur.close()
        if result[0] is not None:
            last_date = datetime.strptime(str(result[0]), "%Y-%m-%d").date()
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
            sql = "UPDATE scales SET `last_claimed_date` = %s WHERE `username` = %s"
            cur = db.cursor()
            cur.execute(sql, (datetime.strftime(today, "%Y-%m-%d"), str(member)))
            db.commit()
            cur.close()
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

        member = ctx.message.author

        # Display User's Scales
        if has_scales(member):
            scales = get_scales(member)
            await self.bot.say("{0.mention}, you currently have **{1}** <:clifford_scales:303675725527908353> (scales)"
                               .format(member, scales))
        else:
            await self.bot.say("{0.mention}, you do not have any <:clifford_scales:303675725527908353> (scales)"
                               .format(member))


def setup(bot):
    bot.add_cog(Scales(bot))
