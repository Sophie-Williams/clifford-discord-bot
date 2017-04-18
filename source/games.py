import discord
from discord.ext import commands
from helpers import db, is_staff, is_game_abv, is_game_name


# ********************************************** #
# GROUPED COMMANDS : GAMES ********************* #
# ********************************************** #

class Games:
    def __init__(self, bot):
        self.bot = bot

    # COMMAND: !games
    @commands.group(pass_context=True)
    async def games(self, ctx):
        """Manages games for the roster."""

        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid command passed. Must be *add*, *edit*, *list*, or *remove*.')

    # COMMAND: !games add
    @games.command(name='add', pass_context=True)
    async def games_add(self, ctx, game_abv: str, *, game_name: str):
        """Adds a game to the list of games available in the roster."""

        # Is the user allowed? (Must be staff)
        if not is_staff(ctx.message.author):
            await self.bot.say('{0.mention}, you must be a staff member to use this command.'
                               .format(ctx.message.author))
            return

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
            sql = "INSERT INTO games (`abv`,`name`) VALUES (%s, %s)"
            cur = db.cursor()
            cur.execute(sql, (game_abv, game_name))
            db.commit()
            cur.close()
        except Exception as e:
            await self.bot.say('{0.mention}, there was an error adding the game to the games list. '
                               .format(ctx.message.author) + str(e))
            return

        # Display Success Message
        await self.bot.say('{0.mention}, the game was successfully added to the games list!'.format(ctx.message.author))

    # COMMAND: !games edit
    @games.command(name='edit', pass_context=True)
    async def games_edit(self, ctx, game_abv: str, *, game_name: str):
        """Updates a game in the list of games available in the roster."""

        # Is the user allowed? (Must be staff)
        if not is_staff(ctx.message.author):
            await self.bot.say('{0.mention}, you must be a staff member to use this command.'
                               .format(ctx.message.author))
            return

        # Is there anything to update?
        if not (is_game_abv(game_abv) or is_game_name(game_name)):
            await self.bot.say('{0.mention}, either the abbreviation of game must exist to update.'
                               .format(ctx.message.author))
            return

        # Handle Database
        try:
            sql = "UPDATE games SET `abv` = %s, `name = %s WHERE `abv` = %s OR `name` = %s"
            cur = db.cursor()
            cur.execute(sql, (game_abv, game_name, game_abv, game_name))
            db.commit()
            cur.close()
        except Exception as e:
            await self.bot.say('{0.mention}, there was an error updating the game in the games list. '
                               .format(ctx.message.author) + str(e))
            return

        # Display Success Message
        await self.bot.say('{0.mention}, the game was successfully updated in the games list!'
                           .format(ctx.message.author))

    # COMMAND: !games remove
    @games.command(name='remove', pass_context=True)
    async def games_remove(self, ctx, *, game_or_abv: str):
        """Removes a game from the list of games available in the roster."""

        # Is the user allowed? (Must be staff)
        if not is_staff(ctx.message.author):
            await self.bot.say('{0.mention}, you must be a staff member to use this command.'
                               .format(ctx.message.author))
            return

        # Is there anything to update?
        if not (is_game_abv(game_or_abv) or is_game_name(game_or_abv)):
            await self.bot.say('{0.mention}, either the abbreviation of game must exist to update.'
                               .format(ctx.message.author))
            return

        # Handle Database
        try:
            sql = "DELETE FROM games WHERE `abv` = %s OR `name` = %s"
            cur = db.cursor()
            cur.execute(sql, (game_or_abv, game_or_abv))
            db.commit()
            cur.close()
        except Exception as e:
            await self.bot.say("{0.mention}, there was an error deleting the game from the games list."
                               .format(ctx.message.author) + str(e))
            return

        # Display Success Message
        await self.bot.say('{0.mention}, the game was successfully deleted from the games list!'
                           .format(ctx.message.author))

    # COMMAND: !games list
    @games.command(name='list', pass_context=True)
    async def games_list(self, ctx):
        """Sends a message to the user with the current games and abbreviations for use in the roster."""

        # Handle Database
        try:
            sql = "SELECT `abv`, `name` FROM games ORDER BY `name`"
            cur = db.cursor()
            cur.execute(sql)
            result = cur.fetchall()
            cur.close()
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, "{0.mention}, there was an error getting the list of games"
                                                             " for you. I'm sorry! ".format(ctx.message.author) + str(e))
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
        await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    bot.add_cog(Games(bot))