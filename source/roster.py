import discord
from discord.ext import commands
from helpers import db, is_game_abv


# ********************************************** #
# GROUPED COMMANDS : ROSTER ******************** #
# ********************************************** #

class Roster:
    def __init__(self, bot):
        self.bot = bot

    # COMMAND: !roster
    @commands.group(pass_context=True, invoke_without_subcommand=True)
    async def roster(self, ctx, game_abv: str):
        """Handles Roster Management."""

        # Does Game Abbreviation Exist?
        if not is_game_abv(game_abv):
            await self.bot.say('Invalid roster command passed. Must be *add*, *edit*, *list*, or *remove*, or a valid '
                               'game abbreviation must be passed to display a roster.')
            return

        # Handle Database
        try:
            sql = "SELECT `discord_account`, `game_account` FROM roster WHERE `game_abv` = %s ORDER BY `discord_account`"
            cur = db.cursor()
            cur.execute(sql, (game_abv,))
            result = cur.fetchall()
            cur.close()
        except Exception:
            await self.bot.send_message(ctx.message.channel, "{0.mention}, there was an error getting the roster for"
                                                             " you. I'm sorry!".format(ctx.message.author))
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
        await self.bot.send_message(ctx.message.channel, embed=embed)

    # COMMAND: !roster add
    @roster.command(name='add', pass_context=True)
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
            sql = "INSERT INTO roster (`discord_account`,`game_abv`,`game_account`) VALUES (%s, %s, %s)"
            cur = db.cursor()
            cur.execute(sql, (username, game_abv, ign))
            db.commit()
            cur.close()
        except Exception:
            await self.bot.say('{0.message.author.mention}, there was an error adding your information to the roster.'
                               .format(ctx))
            return

        # Display Success Message
        await self.bot.say('{0.message.author.mention}, your information was successfully added to the roster!'
                           .format(ctx))

    # COMMAND: !roster edit
    @roster.command(name='edit', pass_context=True)
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
            sql = "UPDATE roster SET `game_account` = %s WHERE `discord_account` = %s AND `game_abv` = %s"
            cur = db.cursor()
            cur.execute(sql, (ign, username, game_abv))
            db.commit()
            cur.close()
        except Exception:
            await self.bot.say('{0.message.author.mention}, there was an error updating your roster information.'
                               .format(ctx))
            return

        # Display Success Message
        await self.bot.say('{0.message.author.mention}, your roster information was successfully updated!'.format(ctx))

    # COMMAND: !roster remove
    @roster.command(name='remove', pass_context=True)
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
            sql = "DELETE FROM roster WHERE `discord_account` = %s AND `game_abv` = %s AND `game_account` = %s"
            cur = db.cursor()
            cur.execute(sql, (username, game_abv, ign))
            db.commit()
            cur.close()
        except Exception:
            await self.bot.say('{0.message.author.mention}, there was an error deleting your roster information.'
                               .format(ctx))
            return

        # Display Success Message
        await self.bot.say('{0.message.author.mention}, your roster information was successfully deleted!'.format(ctx))

    # COMMAND: !roster list
    @roster.command(name='list', pass_context=True)
    async def roster_list(self, ctx, game_abv: str):
        """Sends a message to the user with the current roster for the specified game."""

        # Does Game Abbreviation Exist?
        if not is_game_abv(game_abv):
            await self.bot.say('{0.mention}, this abbreviation does not exist. Use !games display for a list of '
                               'acceptable game abbreviations.'.format(ctx.message.author))
            return

        # Handle Database
        try:
            sql = "SELECT `discord_account`, `game_account` FROM roster WHERE `game_abv` = %s ORDER BY `discord_account`"
            cur = db.cursor()
            cur.execute(sql, (game_abv,))
            result = cur.fetchall()
            cur.close()
        except Exception:
            await self.bot.send_message(ctx.message.channel, "{0.mention}, there was an error getting the roster for"
                                                             " you. I'm sorry!".format(ctx.message.author))
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
        await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    bot.add_cog(Roster(bot))
