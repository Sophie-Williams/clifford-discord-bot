import discord
import MySQLdb


# Define MySQL DB and Cursor Object
db = MySQLdb.connect(host="localhost",
                     user="discord_secure",
                     passwd="password-here",
                     db="discord")


# ********************************************** #
# FUNCTIONS ************************************ #
# ********************************************** #

# Check for Game Abbreviations
def is_game_abv(game_abv: str):
    try:
        sql = "SELECT 1 FROM games WHERE `abv` = %s LIMIT 1"
        cur = db.cursor()
        result = cur.execute(sql, (game_abv,))
        cur.close()
    except Exception as e:
        print('Exception: ' + str(e))
        result = 0

    # If we got a result, true, else false
    return result == 1


# Check for Game Names
def is_game_name(game_name: str):
    try:
        sql = "SELECT 1 FROM games WHERE `name` = %s LIMIT 1"
        cur = db.cursor()
        result = cur.execute(sql, (game_name,))
        cur.close()
    except Exception as e:
        print('Exception: ' + str(e))
        result = 0

    # If we got a result, true, else false
    return result == 1


# Get Game Name
def get_game_name(game_abv: str):
    try:
        sql = "SELECT `name` FROM games WHERE `abv` = %s"
        cur = db.cursor()
        cur.execute(sql, (game_abv,))
        result = cur.fetchone()
        cur.close()
        return result[0]
    except Exception as e:
        print('Exception: ' + str(e))
        return


# Get Game Icon
def get_game_icon(game_abv: str):
    try:
        sql = "SELECT `icon_url` FROM games WHERE `abv` = %s"
        cur = db.cursor()
        cur.execute(sql, (game_abv,))
        result = cur.fetchone()
        cur.close()
        return result[0]
    except Exception as e:
        print('Exception: ' + str(e))
        return


# Check for Staff Member Status
def is_staff(member: discord.Member):

    # Return True or False if User is a Staff Member
    return 'Staff' in [r.name for r in member.roles]
