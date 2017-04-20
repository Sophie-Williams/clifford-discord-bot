import discord
from discord.ext import commands
from helpers import db, is_staff


# ********************************************** #
# GROUPED COMMANDS : EVENTS ******************** #
# ********************************************** #

class Events:
    def __init__(self, bot):
        self.bot = bot

    # COMMAND: !events
    @commands.group(pass_context=True)
    async def events(self, ctx):
        """Manage events and attendance!"""

        if ctx.invoked_subcommand is None:
            await self.bot.say('Invalid command passed. Must be *add*, *description*, *edit*, *register*, or *remove*.')

    # COMMAND: !events add
    @events.command(name='add', pass_context=True, aliases=['create'])
    async def events_add(self, ctx, date: str, time: str, *, title: str):
        """Add an event to the Events List!
           Date **must** be in YYYY/MM/DD format. Time **must** be in UTC."""

        # Set #events Channel
        event_channel = self.bot.get_channel('296694692135829504')

        # Is the user allowed? (Must be staff)
        if not is_staff(ctx.message.author):
            await self.bot.say('{0.mention}, you must be a staff member to use this command.'
                               .format(ctx.message.author))
            return

        # Make sure we have a date.
        if date is None:
            await self.bot.say('Error: You must enter a date in YYYY/MM/DD format.')
            return

        # Make sure we have a time.
        if time is None:
            await self.bot.say('Error: You must enter a time in HH:MM format in UTC timezone.')
            return

        # Make sure we have a title.
        if date is None:
            await self.bot.say('Error: You must enter a title for the event.')
            return

        # Add Event to Database
        try:
            sql = "INSERT INTO events (`date`,`time`,`title`) VALUES (%s, %s, %s)"
            cur = db.cursor()
            cur.execute(sql, (date, time, title))
            event_id = cur.lastrowid

            msg_text = "**Title**: {0} \n**Event ID**: {1} \n**Date & Time**: {2} at {3} (UTC)"

            # Add Message to Events Channel and Save Message ID
            message = await self.bot.send_message(event_channel, msg_text.format(title, event_id, date, time))

            cur.execute('UPDATE events SET `message_id` = %s WHERE `event_id` = %s', (message.id, event_id))
            db.commit()
            cur.close()

        except Exception as e:
            await self.bot.say('{0.mention}, there was an error adding the event to the list. '
                               .format(ctx.message.author)
                          + str(e))
            return

        # Success Message
        await self.bot.say('{0.mention}, your event was successfully added. The event ID is: {1}.'
                           .format(ctx.message.author, event_id))

    # COMMAND: !events description
    @events.command(name='description', pass_context=True, aliases=['desc', 'describe'])
    async def events_description(self, ctx, event_id: int, *, desc: str):
        """Adds a Description to an Event Given an Event ID."""

        # EVENT CHANNEL ID: 296694692135829504
        event_channel = self.bot.get_channel('296694692135829504')

        # Is the user allowed? (Must be staff)
        if not is_staff(ctx.message.author):
            await self.bot.say('{0.mention}, you must be a staff member to use this command.'
                               .format(ctx.message.author))
            return

        # Make sure we have a date.
        if event_id is None:
            await self.bot.say('Error: You must enter an event ID. Check the #events channel.')
            return

        # Make sure we have a date.
        if desc is None:
            await self.bot.say('Error: You must enter a description.')
            return

        try:
            sql = "UPDATE events SET `description` = %s WHERE `event_id` = %s"
            cur = db.cursor()
            cur.execute(sql, (desc, event_id))
            cur.execute("SELECT `message_id` FROM events WHERE `event_id` = %s", (event_id,))
            msg_id = cur.fetchone()
            message = await self.bot.get_message(event_channel, msg_id[0])

            msg_text = message.content + " \n**Description**: {0}".format(desc)

            # Update Message in Events Channel with Description
            await self.bot.edit_message(message, msg_text)

            db.commit()
            cur.close()
        except Exception as e:
            await self.bot.say('{0.mention}, there was an error adding a description to the event. '
                               .format(ctx.message.author) + str(e))
            return

        # Success Message
        await self.bot.say('{0.mention}, the event was successfully updated with a description.'
                           .format(ctx.message.author))


def setup(bot):
    bot.add_cog(Events(bot))
