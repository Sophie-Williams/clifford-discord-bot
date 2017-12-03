import discord
from discord.ext import commands
from helpers import db, is_game_abv, get_game_icon, get_game_name


# ********************************************** #
# GROUPED COMMANDS : ROSTER ******************** #
# ********************************************** #

class Roster:
    def __init__(self, bot):
        self.bot = bot

    # COMMAND: !roster
    @commands.group(invoke_without_command=True, pass_context=True)
    async def roster(self, ctx, *, game_abv: str):
        """Handles Roster Management."""

        # Does Game Abbreviation Exist?
        if not is_game_abv(game_abv):
            await self.bot.say('Invalid roster command passed. Must be *add*, *edit*, or *remove*; or a valid game '
                               'abbreviation must be passed to display a roster.')
            return

        # Handle Database
        try:
            with db.cursor() as cursor:
                sql = "SELECT `discord_account`, `game_account` FROM roster WHERE `game_abv` = %s ORDER BY `discord_account`"
                cursor.execute(sql, (game_abv,))
                result = cursor.fetchall()
                cursor.close()
        except Exception:
            await self.bot.send_message(ctx.message.channel, "{0.mention}, there was an error getting the roster for"
                                                             " you. I'm sorry!".format(ctx.message.author))
            return

        # Create Variables for Embed Table
        accounts = ''
        names = ''
        i = 1

        for row in result:
            accounts += ('**' + str(i) + '**. ' + row['discord_account'] + '\n')
            names += ('**' + str(i) + '**. ' + row['game_account'] + '\n')
            i += 1

        # Create Embed Table
        gameName = get_game_name(game_abv)
        gameIcon = get_game_icon(game_abv)
        embed = discord.Embed(title=gameName + " Roster", colour=discord.Colour(0x55ff),
                              description="*The official roster for Zealot Gaming members who play " + gameName + ".*")
        embed.set_author(name="Zealot Gaming", url="http://www.zealotgaming.com",
                         icon_url="http://www.zealotgaming.com/discordicons/logos/zg.png")
        embed.set_thumbnail(url="http://www.zealotgaming.com/discordicons/logos/" + gameIcon)
        embed.add_field(name="Discord Account", value=accounts, inline=True)
        embed.add_field(name="In-Game Name", value=names, inline=True)

        # Send Table to Channel
        await self.bot.send_message(ctx.message.channel, embed=embed)

    # COMMAND: !roster add
    @roster.command(name='add', pass_context=True, aliases=['insert'])
    async def roster_add(self, ctx, game_abv: str, *, ign: str):
        """Adds username to roster.
           User a game abbreviation from the games list. Only one entry per game. Include all in-game names if necessary."""

        username = str(ctx.message.author)

        # Does Game Abbreviation Exist?
        if not is_game_abv(game_abv):
            await self.bot.say('{0.mention}, this abbreviation does not exist. Use !games display for a list of '
                               'acceptable game abbreviations.'.format(ctx.message.author))
            return

        # Handle Database
        try:
            with db.cursor() as cursor:
                sql = "INSERT INTO roster (`discord_account`,`game_abv`,`game_account`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (username, game_abv, ign))
                db.commit()
                cursor.close()
        except Exception:
            await self.bot.say('{0.message.author.mention}, there was an error adding your information to the roster.'
                               .format(ctx))
            return

        # Display Success Message
        await self.bot.say('{0.message.author.mention}, your information was successfully added to the roster!'
                           .format(ctx))

    # COMMAND: !roster edit
    @roster.command(name='edit', pass_context=True, aliases=['update'])
    async def roster_edit(self, ctx, game_abv: str, *, ign: str):
        """Updates a roster entry for a specific game.
           If the either Game Name or your in-Game Name have spaces, put them in quotes."""

        username = str(ctx.message.author)

        # Does Game Abbreviation Exist?
        if not is_game_abv(game_abv):
            await self.bot.say('{0.mention}, this abbreviation does not exist. Use !games display for a list of '
                               'acceptable game abbreviations.'.format(ctx.message.author))
            return

        # Handle Database
        try:
            with db.cursor() as cursor:
                sql = "UPDATE roster SET `game_account` = %s WHERE `discord_account` = %s AND `game_abv` = %s"
                cursor.execute(sql, (ign, username, game_abv))
                db.commit()
                cursor.close()
        except Exception:
            await self.bot.say('{0.message.author.mention}, there was an error updating your roster information.'
                               .format(ctx))
            return

        # Display Success Message
        await self.bot.say('{0.message.author.mention}, your roster information was successfully updated!'.format(ctx))

    # COMMAND: !roster remove
    @roster.command(name='remove', pass_context=True, aliases=['delete'])
    async def roster_remove(self, ctx, game_abv: str, *, ign: str):
        """Removes a user's entries in the roster for the specified game."""

        username = str(ctx.message.author)

        # Does Game Abbreviation Exist?
        if not is_game_abv(game_abv):
            await self.bot.say('{0.mention}, this abbreviation does not exist. Use !games display for a list of '
                               'acceptable game abbreviations.'.format(ctx.message.author))
            return

        # Handle Database
        try:
            with db.cursor() as cursor:
                sql = "DELETE FROM roster WHERE `discord_account` = %s AND `game_abv` = %s AND `game_account` = %s"
                cursor.execute(sql, (username, game_abv, ign))
                db.commit()
                cursor.close()
        except Exception:
            await self.bot.say('{0.message.author.mention}, there was an error deleting your roster information.'
                               .format(ctx))
            return

        # Display Success Message
        await self.bot.say('{0.message.author.mention}, your roster information was successfully deleted!'.format(ctx))


def setup(bot):
    bot.add_cog(Roster(bot))
