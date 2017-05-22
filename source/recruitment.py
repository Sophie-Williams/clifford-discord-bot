import discord
from discord.ext import commands
from helpers import db, is_game_abv


# ********************************************** #
# GROUPED COMMANDS : RECRUIT ******************* #
# ********************************************** #

class Recruitment:
    def __init__(self, bot):
        self.bot = bot

    # COMMAND: !recruit
    @commands.group(pass_context=True, invoke_without_command=True)
    async def recruit(self, ctx):
        """Handles Recruitment Post and Invites Management."""

        # Handle Database
        try:
            sql = "SELECT * FROM recruitment ORDER BY `game`"
            cur = db.cursor()
            cur.execute(sql)
            result = cur.fetchall()
            cur.close()
        except Exception:
            await self.bot.send_message(ctx.message.channel, "{0.mention}, there was an error getting the recruitment "
                                                             "list for you. I'm sorry!".format(ctx.message.author))
            return

        # Create Variables for Embed Table
        entries = ''
        game_abvs = ''
        links = ''

        for row in result:
            entries += (str(row[0]) + '\n')
            game_abvs += (str(row[1]) + '\n')
            links += (str(row[2]) + '\n')

        # Create Embed Table
        embed = discord.Embed()
        embed.add_field(name="ID", value=entries, inline=True)
        embed.add_field(name="Game", value=game_abvs, inline=True)
        embed.add_field(name="Link", value=links, inline=True)

        # Send Table to Channel
        await self.bot.send_message(ctx.message.channel, embed=embed)

    # COMMAND: !recruit add
    @recruit.command(name='add', pass_context=True, aliases=['insert'])
    @commands.has_role("Staff")
    async def recruit_add(self, ctx, game_abv: str, *, link: str):
        """Adds recruitment post link to the recruitment list. Use a game abbreviation from the games list."""

        # Does Game Abbreviation Exist?
        if not is_game_abv(game_abv) and not game_abv == 'all':
            await self.bot.say(
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
            await self.bot.say(
                '{0.message.author.mention}, there was an error adding your recruitment link to the list.'.format(ctx))
            return

        # Display Success Message
        await self.bot.say('{0.message.author.mention}, your information was successfully added to the recruitment '
                           'posts list!'.format(ctx))

    # COMMAND: !recruit edit
    @recruit.command(name='edit', pass_context=True, aliases=['update'])
    @commands.has_role("Staff")
    async def recruit_edit(self, ctx, entry_id: int, *, link: str):
        """Updates a recruitment post entry with the specified entry ID."""

        # Handle Database
        try:
            sql = "UPDATE recruitment SET `link` = %s WHERE `entry_id` = %s"
            cur = db.cursor()
            cur.execute(sql, (link, entry_id))
            db.commit()
            cur.close()
        except Exception:
            await self.bot.say('{0.message.author.mention}, there was an error updating the specified recruitment '
                               'entry.'.format(ctx))
            return

        # Display Success Message
        await self.bot.say('{0.message.author.mention}, the recruitment entry was successfully updated!'.format(ctx))

    # COMMAND: !recruit remove
    @recruit.command(name='remove', pass_context=True, aliases=['delete'])
    @commands.has_role("Staff")
    async def recruit_remove(self, ctx, entry_id: int):
        """Removes an entry for the recruitment posts list with the specified entry ID."""

        # Handle Database
        try:
            sql = "DELETE FROM recruitment WHERE `id` = %s"
            cur = db.cursor()
            cur.execute(sql, (entry_id,))
            db.commit()
            cur.close()
        except Exception:
            await self.bot.say('{0.message.author.mention}, there was an error deleting the specified recruitment '
                               'entry.'.format(ctx))
            return

        # Display Success Message
        await self.bot.say('{0.message.author.mention}, the recruitment entry was successfully deleted!'.format(ctx))

    # COMMAND: !recruit invite
    @recruit.command(name='invite')
    async def recruit_invite(self, duration: int):
        """Provides an invite link to the Discord server. Set duration to 0 for permanent invite."""

        # Default Duration 30 Minutes, Else Convert to Minutes
        if duration is None:
            duration = 1800
        else:
            duration *= 60

        # WELCOME CHANNEL ID: 141622052133142529
        welcome_channel = self.bot.get_channel('141622052133142529')

        # Create the Invite
        new_invite = await self.bot.create_invite(welcome_channel, max_age=duration, max_users=0, unique=False)

        # Send Message with Invite Link
        await self.bot.say('Your newly generated invite link is: {0.url}'.format(new_invite))


def setup(bot):
    bot.add_cog(Recruitment(bot))
