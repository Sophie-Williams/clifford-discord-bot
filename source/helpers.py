import discord
import pymysql.cursors


# Define MySQL DB and Cursor Object
db = pymysql.connect(host="localhost",
                     user="user_here",
                     passwd="password_here",
                     db="db_here",
                     charset='utf8',
                     cursorclass=pymysql.cursors.DictCursor)


# ********************************************** #
# FUNCTIONS ************************************ #
# ********************************************** #

# Check for Game Abbreviations
def is_game_abv(game_abv: str):
    try:
        with db.cursor() as cursor:
            sql = "SELECT 1 FROM games WHERE `abv` = %s LIMIT 1"
            cursor.execute(sql, (game_abv,))
            result = cursor.fetchone()[0]
            cursor.close()
    except Exception as e:
        print('Exception: ' + str(e))
        result = 0

    # If we got a result, true, else false
    return result == 1


# Check for Game Names
def is_game_name(game_name: str):
    try:
        with db.cursor() as cursor:
            sql = "SELECT 1 as `is_game` FROM games WHERE `name` = %s LIMIT 1"
            cursor.execute(sql, (game_name,))
            result = cursor.fetchone()['is_game']
            cursor.close()
    except Exception as e:
        print('Exception: ' + str(e))
        result = 0

    # If we got a result, true, else false
    return result == 1


# Get Game Name
def get_game_name(game_abv: str):
    try:
        with db.cursor() as cursor:
            sql = "SELECT `name` FROM games WHERE `abv` = %s"
            cursor.execute(sql, (game_abv,))
            result = cursor.fetchone()
            cursor.close()
            return result['name']
    except Exception as e:
        print('Exception: ' + str(e))
        return


# Get Game Icon
def get_game_icon(game_abv: str):
    try:
        with db.cursor() as cursor:
            sql = "SELECT `icon_url` FROM games WHERE `abv` = %s"
            cursor.execute(sql, (game_abv,))
            result = cursor.fetchone()
            cursor.close()
            return result['icon_url']
    except Exception as e:
        print('Exception: ' + str(e))
        return


# Check for Staff Member Status
def is_staff(member: discord.Member):

    # Return True or False if User is a Staff Member
    return 'Staff' in [r.name for r in member.roles]
