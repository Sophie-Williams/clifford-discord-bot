import discord
from discord.ext import commands
from helpers import db, is_staff
import time


# ********************************************** #
# GROUPED COMMANDS : SCALES ******************** #
# ********************************************** #

class Scales:
    def __init__(self, bot):
        self.bot = bot

    # Check if User Has Been Initialized with Scales
    @staticmethod
    def has_scales(member: discord.Member):
        # Query Database
        sql = "SELECT 1 FROM scales WHERE `username` = %s"
        cur = db.cursor()
        cur.execute(sql, (str(member),))
        entry = cur.fetchone()
        cur.close()

        # Return the Result (True/False)
        return entry[0] == 1

    # Initialize User with Scales
    @staticmethod
    def start_scales(member: discord.Member):

        if not has_scales(member):
            # Initialize to Zero
            sql = "INSERT INTO scales (`username`) VALUES (%s)"
            cur = db.cursor()
            cur.execute(sql, (str(member),))
            db.commit()
            cur.close()

    # Get User's Current Scales
    @staticmethod
    def get_scales(member: discord.Member):
        # Query Database
        sql = "SELECT `total` FROM scales WHERE `username` = %s"
        cur = db.cursor()
        cur.execute(sql, (str(member),))
        entry = cur.fetchone()
        cur.close()

        # Return the Number of Scales
        if entry[0] is not None:
            return entry[0]
        else:
            return 0

    # Add Scales to User's Total
    @staticmethod
    def add_scales(member: discord.Member, scales: int):

        # Get Users Current Scales
        current_scales = get_scales(member)
        new_scales = current_scales + scales

        # Give Points to User
        sql = "UPDATE scales SET `total` = %s WHERE username = %s"
        cur = db.cursor()
        cur.execute(sql, (new_scales, str(member)))

    # COMMAND: !claim
    @commands.command(name='claim', pass_context=True)
    async def claim_scales(self, ctx):
        """Allows users to claim their daily scales."""

        # Has the user already claimed scales today?
        today = time.strftime("%Y/%m/%d")

        # Is the user allowed? (Must be Staff)
        if not is_staff(ctx.message.author):
            await self.bot.say('{0.mention}, you must be a staff member to use this command.'
                               .format(ctx.message.author))
            return

        if role_name not in allowed_roles:
            await self.bot.say('{0.mention}, you may only assign users to public roles, Squire, Knight, or Zealot.'
                               .format(ctx.message.author))
            return

        # Define role, then add role to member.
        try:
            role = discord.utils.get(ctx.message.server.roles, name=role_name)
            user = discord.utils.get(ctx.message.server.members, name=username)
            await self.bot.add_roles(user, role)
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, "{0.mention}, there was an granting the role to the user. "
                                        .format(ctx.message.author) + str(e))
            return

        # Success Message
        await self.bot.say('{0.mention}, you have successfully added **{1}** to the group **{2}**.'
                           .format(ctx.message.author, username, role_name))


def setup(bot):
    bot.add_cog(Scales(bot))
