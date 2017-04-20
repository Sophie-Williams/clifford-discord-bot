import discord
from discord.ext import commands
from helpers import is_staff
import random


class General:
    def __init__(self, bot):
        self.bot = bot

    # ********************************************** #
    # UN-GROUPED BOT COMMANDS ********************** #
    # ********************************************** #

    # Load Extension
    @commands.command(pass_context=True)
    async def load(self, ctx, extension_name: str):
        """Loads an extension."""

        # Is the user allowed? (Must be staff)
        if not is_staff(ctx.message.author):
            await self.bot.say(
                '{0.mention}, you must be a staff member to use this command.'.format(ctx.message.author))
            return

        try:
            self.bot.load_extension(extension_name)
        except (AttributeError, ImportError) as ex:
            await self.bot.say("```py\n{}: {}\n```".format(type(ex).__name__, str(ex)))
            return
        await self.bot.say("{} loaded.".format(extension_name))

    # Unload Extension
    @commands.command(pass_context=True)
    async def unload(self, ctx, extension_name: str):
        """Unloads an extension."""

        # Is the user allowed? (Must be staff)
        if not is_staff(ctx.message.author):
            await self.bot.say(
                '{0.mention}, you must be a staff member to use this command.'.format(ctx.message.author))
            return

        self.bot.unload_extension(extension_name)
        await self.bot.say("{} unloaded.".format(extension_name))

    # COMMAND: !hello
    @commands.command(pass_context=True)
    async def hello(self, ctx):
        """Say hello to Clifford, and he will say hello to you."""
        # we do not want the bot to reply to itself
        if ctx.message.author == self.bot.user:
            return
        else:
            msg = 'Hello {0.message.author.mention}'.format(ctx)
            await self.bot.send_message(ctx.message.channel, msg)

    # COMMAND: !carlito
    @commands.command()
    async def carlito(self):
        """The legendary message of Carlito, maz00's personal cabana boy."""
        await self.bot.say(
            "wew men :ok_hand::skin-tone-1: that's some good shit:100: some good shit :100: that's some good shit"
            " right there :100: :ok_hand::skin-tone-1: right there :ok_hand::skin-tone-1: :100: sign me the FUCK "
            "up:100: :100: :ok_hand::skin-tone-1: :eggplant:")

    # COMMAND: !eightball
    @commands.command(pass_context=True)
    async def eightball(self, ctx, question: str):
        """Rolls a magic 8-ball to answer any question you have."""

        if question is None:
            await self.bot.say('{0.message.author.mention}, you did not ask a question.'.format(ctx))
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
        await self.bot.say('{0.message.author.mention}, '.format(ctx) + random.choice(answers))

    # COMMAND: !roll
    @commands.command()
    async def roll(self, dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await self.bot.say('Format has to be in NdN!')
            return

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await self.bot.say(result)

    # COMMAND: !get_channel_id
    @commands.command(pass_context=True)
    async def get_channel_id(self, ctx):
        """Lists the ID of the channel the message is sent in."""

        # Is the user allowed? (Must be staff)
        if not is_staff(ctx.message.author):
            await self.bot.say('{0.mention}, you must be a staff member to use this command.'.format(ctx.message.author))
            return

        await self.bot.say('Channel ID is {0.id}'.format(ctx.message.channel))

    # COMMAND: !join
    @commands.command(pass_context=True)
    async def join(self, ctx, *, role_name: str):
        """Allows a user to join a public group."""

        # List of Allowed Public Roles
        allowed_roles = ['Europe',
                         'North America',
                         'Oceania',
                         'Overwatch',
                         'League of Legends',
                         'Co-op',
                         'Minna-chan',
                         'Squire']

        if role_name not in allowed_roles:
            await self.bot.say('{0.mention}, you may only join allowed public groups. Check #info for a list of groups.'
                               .format(ctx.message.author))
            return

        # Define role, then add role to member.
        try:
            role = discord.utils.get(ctx.message.server.roles, name=role_name)
            await self.bot.add_roles(ctx.message.author, role)
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, "{0.mention}, there was an error getting the roster for "
                                                             "you. I'm sorry! : ".format(ctx.message.author) + str(e))
            return

        # Success Message
        await self.bot.say('{0.mention}, you have successfully been added to the group **{1}**'
                           '.'.format(ctx.message.author, role_name))


def setup(bot):
    bot.add_cog(General(bot))
