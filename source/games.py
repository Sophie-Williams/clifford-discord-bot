import discord
from discord.ext import commands
from helpers import db, is_game_abv, is_game_name


# ********************************************** #
# GROUPED COMMANDS : GAMES ********************* #
# ********************************************** #

class Games:
    def __init__(self, bot):
        self.bot = bot

    # COMMAND: !games
    @commands.group(pass_context=True, invoke_without_command=True)
    async def games(self, ctx):
        """Manages games for the roster."""

        # Handle Database
        try:
            with db.cursor() as cursor:
                sql = "SELECT `abv`, `name` FROM games ORDER BY `name`"
                cursor.execute(sql)
                result = cursor.fetchall()
                cursor.close()
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, "{0.mention}, there was an error getting the list of games"
                                                             " for you. I'm sorry! ".format(ctx.message.author) + str(
                e))
            return

        # Create Variables for Embed Table
        abvs = ''
        names = ''

        for row in result:
            abvs += (row['abv'] + '\n')
            names += (row['name'] + '\n')

        # Create Embed Table
        embed = discord.Embed(title="Games List", colour=discord.Colour(0x55ff),
                              description="*The list of available games for the roster commands, as well as their "
                                          "abbreviations for use in those commands.*")
        embed.set_author(name="Zealot Gaming", url="https://www.zealotgaming.com",
                         icon_url="http://www.zealotgaming.com/discord/logos/zg.png")
        embed.set_thumbnail(url="http://www.zealotgaming.com/discord/logos/zg.png")
        embed.add_field(name="Abbreviation", value=abvs, inline=True)
        embed.add_field(name="Game Name", value=names, inline=True)

        # Send Table to User Privately
        await self.bot.send_message(ctx.message.channel, embed=embed)

    # COMMAND: !games add
    @games.command(name='add', pass_context=True, aliases=['create', 'insert'])
    @commands.has_role("Staff")
    async def games_add(self, ctx, game_abv: str, *, game_name: str):
        """Adds a game to the list of games available in the roster."""

        # Does Game Abbreviation Exist?
        if is_game_abv(game_abv):
            await self.bot.say('{0.mention}, this abbreviation is already in use.'.format(ctx.message.author))
            return

        # Does Game Name Exist?
        if is_game_name(game_name):
            await self.bot.say('{0.mention}, this game is already in the list.'.format(ctx.message.author))
            return

        # Handle Database
        try:
            with db.cursor() as cursor:
                sql = "INSERT INTO games (`abv`,`name`) VALUES (%s, %s)"
                cursor.execute(sql, (game_abv, game_name))
                db.commit()
                cursor.close()
        except Exception as e:
            await self.bot.say('{0.mention}, there was an error adding the game to the games list. '
                               .format(ctx.message.author) + str(e))
            return

        # Display Success Message
        await self.bot.say('{0.mention}, the game was successfully added to the games list!'.format(ctx.message.author))

    # COMMAND: !games edit
    @games.command(name='edit', pass_context=True, aliases=['update', 'change'])
    @commands.has_role("Staff")
    async def games_edit(self, ctx, game_abv: str, *, game_name: str):
        """Updates a game in the list of games available in the roster."""

        # Is there anything to update?
        if not (is_game_abv(game_abv) or is_game_name(game_name)):
            await self.bot.say('{0.mention}, either the abbreviation of game must exist to update.'
                               .format(ctx.message.author))
            return

        # Handle Database
        try:
            with db.cursor() as cursor:
                sql = "UPDATE games SET `abv` = %s, `name = %s WHERE `abv` = %s OR `name` = %s"
                cursor.execute(sql, (game_abv, game_name, game_abv, game_name))
                db.commit()
                cursor.close()
        except Exception as e:
            await self.bot.say('{0.mention}, there was an error updating the game in the games list. '
                               .format(ctx.message.author) + str(e))
            return

        # Display Success Message
        await self.bot.say('{0.mention}, the game was successfully updated in the games list!'
                           .format(ctx.message.author))

    # COMMAND: !games remove
    @games.command(name='remove', pass_context=True, aliases=['delete'])
    @commands.has_role("Staff")
    async def games_remove(self, ctx, *, game_or_abv: str):
        """Removes a game from the list of games available in the roster."""

        # Is there anything to update?
        if not (is_game_abv(game_or_abv) or is_game_name(game_or_abv)):
            await self.bot.say('{0.mention}, either the abbreviation of game must exist to update.'
                               .format(ctx.message.author))
            return

        # Handle Database
        try:
            with db.cursor() as cursor:
                sql = "DELETE FROM games WHERE `abv` = %s OR `name` = %s"
                cursor.execute(sql, (game_or_abv, game_or_abv))
                db.commit()
                cursor.close()
        except Exception as e:
            await self.bot.say("{0.mention}, there was an error deleting the game from the games list."
                               .format(ctx.message.author) + str(e))
            return

        # Display Success Message
        await self.bot.say('{0.mention}, the game was successfully deleted from the games list!'
                           .format(ctx.message.author))

    # COMMAND: !games icon
    @games.command(name='icon', pass_context=True, aliases=['addicon'])
    @commands.has_role("Staff")
    async def games_icon(self, ctx, game_abv: str, *, icon: str):
        """Removes a game from the list of games available in the roster."""

        # Is there anything to update?
        if not (is_game_abv(game_abv)):
            await self.bot.say('{0.mention}, the abbreviation of game must exist to update.'
                               .format(ctx.message.author))
            return

        # Handle Database
        try:
            with db.cursor() as cursor:
                sql = "UPDATE games SET `icon_url` = %s WHERE `abv` = %s"
                cursor.execute(sql, (icon, game_abv))
                db.commit()
                cursor.close()
        except Exception as e:
            await self.bot.say("{0.mention}, there was an error adding the icon to the game."
                               .format(ctx.message.author) + str(e))
            return

        # Display Success Message
        await self.bot.say('{0.mention}, the icon was successfully added to the game!'
                           .format(ctx.message.author))


def setup(bot):
    bot.add_cog(Games(bot))
