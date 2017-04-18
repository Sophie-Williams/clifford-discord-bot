import discord
from discord.ext import commands
from helpers import db, is_staff


# ********************************************** #
# MODERATOR COMMANDS *************************** #
# ********************************************** #

class Moderator:
    def __init__(self, bot):
        self.bot = bot

    # COMMAND: !give_role
    @commands.command(pass_context=True)
    async def give_role(self, ctx, username: str, *, role_name: str):
        """Assigns a role to a user."""

        # List of Roles Staff Can Add To.
        allowed_roles = ['Europe',
                         'North America',
                         'Oceania',
                         'Overwatch',
                         'League of Legends',
                         'Co-op',
                         'Minna-chan',
                         'Squire',
                         'Knight',
                         'Zealot']

        # Is the user allowed? (Must be Staff)
        if not is_staff(ctx.message.author):
            await self.bot.say('{0.mention}, you must be a staff member to use this command.'
                               .format(ctx.message.author))
            return

        if role_name not in allowed_roles:
            await self.bot.say('{0.mention}, you may only assign users to public roles, Squire, Knight, or Zealot'
                               .format(ctx.message.author))
            return

        # Define role, then add role to member.
        try:
            role = discord.utils.get(ctx.message.server.roles, name=role_name)
            user = discord.utils.get(ctx.message.server.members, name=username)
            await self.bot.add_roles(user, role)
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, "{0.mention}, there was an granting the role to the user."
                                                             " ".format(ctx.message.author) + str(e))
            return

        # Success Message
        await self.bot.say('{0.mention}, you have successfully added **{1}** to the group **{2}**'
                           '.'.format(ctx.message.author, username, role_name))

    # COMMAND: !kick
    @commands.command(name='kick', pass_context=True)
    async def mod_kick(self, ctx, username: str, *, reason: str):
        """Kicks a user from the server."""

        # User must be a staff member
        if not is_staff(ctx.message.author):
            await self.bot.say('{0.mention}, you must be a staff member to use this command.'
                               .format(ctx.message.author))
            return

        # Add to DB and Post Message
        try:
            # Variables Needed
            member = discord.utils.get(ctx.message.server.members, name=username)
            staffer = ctx.message.author

            # Handle Database
            sql = "INSERT INTO mod_log (`action`,`user`, `user_id`, `staff`, `staff_id`, `reason`) " \
                  "VALUES ('kick', %s, %s, %s, %s, %s)"
            cur = db.cursor()
            cur.execute(sql, (str(member), member.id, str(staffer), staffer.id, reason))

            # Save Last Row ID
            case_id = cur.lastrowid

            # Insert Message
            log_channel = self.bot.get_channel('303262467205890051')
            msg_text = "**Case #{0}** | Kick :boot: \n**User**: {1} ({2}) " \
                       "\n**Moderator**: {3} ({4}) \n**Reason**: {5}"

            # Add Message to Events Channel and Save Message ID
            case_message = await self.bot.send_message(log_channel, msg_text.format(case_id, str(member), member.id,
                                                                                    str(staffer), staffer.id, reason))
            cur.execute("UPDATE mod_log SET `message_id` = %s WHERE `case_id` = %s", (case_message.id, case_id))

            # Finish Database Stuff and Commit
            db.commit()
            cur.close()

            # Kick the Member
            await self.bot.kick(member)
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, "{0.mention}, there was an error when kicking the user."
                                                             " ".format(ctx.message.author) + str(e))

        await self.bot.say("{0.mention}, the user was successfully kicked. A log entry has been added."
                           .format(ctx.message.author))

    # COMMAND: !ban
    @commands.command(name='ban', pass_context=True)
    async def mod_ban(self, ctx, username: str, *, reason: str):
        """Bans a user from the server."""

        # User must be a staff member
        if not is_staff(ctx.message.author):
            await self.bot.say('{0.mention}, you must be a staff member to use this command.'
                               .format(ctx.message.author))
            return

        # Add to DB and Post Message
        try:
            # Variables Needed
            member = discord.utils.get(ctx.message.server.members, name=username)
            staffer = ctx.message.author

            # Handle Database
            sql = "INSERT INTO mod_log (`action`,`user`, `user_id`, `staff`, `staff_id`, reason) " \
                  "VALUES ('ban', %s, %s, %s, %s, %s)"
            cur = db.cursor()
            cur.execute(sql, (str(member), member.id, str(staffer), staffer.id, reason))

            # Save Last Row ID
            case_id = cur.lastrowid

            # Insert Message
            log_channel = self.bot.get_channel('303262467205890051')
            msg_text = "**Case #{0}** | Ban :hammer: \n**User**: {1} ({2}) " \
                       "\n**Moderator**: {3} ({4}) \n**Reason**: {5}"

            # Add Message to Events Channel and Save Message ID
            case_message = await self.bot.send_message(log_channel, msg_text.format(case_id, str(member), member.id,
                                                                                    str(staffer), staffer.id, reason))
            cur.execute("UPDATE mod_log SET `message_id` = %s WHERE `case_id` = %s", (case_message.id, case_id))

            # Finish Database Stuff and Commit
            db.commit()
            cur.close()

            # Kick the Member
            await self.bot.ban(member, 0)
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, "{0.mention}, there was an error when banning the user."
                                                        " ".format(ctx.message.author) + str(e))

        await self.bot.say("{0.mention}, the user was successfully banned. A log entry has been added."
                           .format(ctx.message.author))

    # COMMAND: !unban
    @commands.command(name='unban', pass_context=True)
    async def mod_unban(self, ctx, username: str, *, reason: str):
        """Unbans a user from the server."""

        # User must be a staff member
        if not is_staff(ctx.message.author):
            await self.bot.say('{0.mention}, you must be a staff member to use this command.'
                               .format(ctx.message.author))
            return

        # Add to DB and Post Message
        try:
            # Variables Needed
            member = discord.utils.get(self.bot.get_bans(ctx.message.server), name=username)
            staffer = ctx.message.author

            # Handle Database
            sql = "INSERT INTO mod_log (`action`,`user`, `user_id`, `staff`, `staff_id`, reason) " \
                  "VALUES ('unban', %s, %s, %s, %s, %s)"
            cur = db.cursor()
            cur.execute(sql, (str(member), member.id, str(staffer), staffer.id, reason))

            # Save Last Row ID
            case_id = cur.lastrowid

            # Insert Message
            log_channel = self.bot.get_channel('303262467205890051')
            msg_text = "**Case #{0}** | Unban :peace: \n**User**: {1} ({2}) " \
                       "\n**Moderator**: {3} ({4}) \n**Reason**: {5}"

            # Add Message to Events Channel and Save Message ID
            case_message = await self.bot.send_message(log_channel, msg_text.format(case_id, str(member), member.id,
                                                                                    str(staffer), staffer.id, reason))
            cur.execute("UPDATE mod_log SET `message_id` = %s WHERE `case_id` = %s", (case_message.id, case_id))

            # Finish Database Stuff and Commit
            db.commit()
            cur.close()

            # Kick the Member
            await self.bot.ban(member, 0)
        except Exception as e:
            await self.bot.send_message(ctx.message.channel, "{0.mention}, there was an error when unbanning the user."
                                                             " ".format(ctx.message.author) + str(e))

        await self.bot.say("{0.mention}, the user was successfully unbanned. A log entry has been added."
                           .format(ctx.message.author))


def setup(bot):
    bot.add_cog(Moderator(bot))
