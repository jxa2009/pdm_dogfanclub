from json import tool
import re
from unicodedata import category
import psycopg2
from sshtunnel import SSHTunnelForwarder
from datetime import date

cs_username = ""
cs_password = ""
dbName = "p320_18"


# create a login_info.txt file with two lines: a line containing your username on the first and password on the second
def get_login_info():
    f = open("login_info.txt", "r")
    global cs_username, cs_password
    cs_username = f.readline().strip()
    cs_password = f.readline().strip()
    return


def command_parser(curs):
    print("Welcome to the tools management system")
    # query usernames and passwords and make sure it exists
    login_user(curs)
    run_program(curs)


def login_user(curs):
    while True:
        print(
            "usage:\n\tcreate a new account: create [username] [password] [first name] [last name] [email]\n\tlogin [username] [password]")
        cmd = input()
        parsed_cmd = cmd.split()
        cmd_sz = len(parsed_cmd)
        if cmd_sz == 0:
            print("no command passed in")
            continue
        action = parsed_cmd[0]

        if action == "create" and cmd_sz == 6:
            user = parsed_cmd[1]
            pwd = parsed_cmd[2]
            f_name = parsed_cmd[3]
            l_name = parsed_cmd[4]
            email = parsed_cmd[5]
            if create_user(curs, user, pwd, f_name, l_name, email):
                print("created user")
            else:
                print("failed to create user")
        elif action == "login" and cmd_sz == 3:
            user = parsed_cmd[1]
            pwd = parsed_cmd[2]
            if user_exists(curs, user, pwd):
                print("logged in as {fuser}".format(fuser=user))

                query = "UPDATE p320_18.\"User\" SET \"Last Access Date\" = TO_DATE(%s,'DD/MM/YYYY') WHERE p320_18.\"User\".\"Username\" = %s;"

                date_obj = date.today()
                today = date_obj.strftime("%d/%m/%Y")
                params = (today, user,)
                try:
                    curs.execute(query, params)
                except:
                    print("failed to update")

                break
            else:
                print("failed to log in as {fuser}".format(fuser=user))
        else:
            print("invalid command")


def run_program(curs):
    while True:
        # print the command you're gonna add here and how to use it

        print("usage:")
        print("\tcategory new [category_name]")
        print("\t         add [tool_barcode] [category_id]")
        print("\n\tsearch barcode [tool_barcode]")
        print("\t       name [tool_name]")
        print("\t       category [tool_category]")
        print("\n\tdelete barcode [tool_barcode]")
        print("\n\tborrow barcode [tool_barcode]")

        cmd = input()
        parsed_cmd = cmd.split()
        cmd_sz = len(parsed_cmd)
        if cmd_sz == 0:
            print("no command passed in")
            continue
        action = parsed_cmd[0]
        if action == "category" and cmd_sz > 2:
            sub_action = parsed_cmd[1]

            if sub_action == "new" and cmd_sz == 3:
                name = parsed_cmd[2]
                if add_new_category(curs, name):
                    print("added category")
                else:
                    print("failed to add category")
            elif sub_action == "add" and cmd_sz == 4:
                tool_barcode = parsed_cmd[2]
                category_id = parsed_cmd[3]
                if add_category_to_tool(curs, tool_barcode, category_id):
                    print("successfully added category to tool")
                else:
                    print("failed to add category to tool")
            else:
                print("invalid command")

        elif action == "search" and cmd_sz == 3:
            sub_action = parsed_cmd[1]

            if sub_action == "barcode":
                barcode = parsed_cmd[2]
                find_tool_by_barcode(curs, barcode)

            elif sub_action == "name":
                name = parsed_cmd[2]
                find_tool_by_name(curs, name)

            elif sub_action == "category":
                category = parsed_cmd[2]
                find_tool_by_category(curs, category)

            else:
                print("invalid search parameter")

        elif action == "delete" and cmd_sz > 2:
            sub_action = parsed_cmd[1]
            if sub_action == "barcode":
                barcode = parsed_cmd[2]
                delete_tools_by_barcode(curs, barcode)
                print("Successfully deleted")
        elif action == "borrow" and cmd_sz > 2:
            sub_action = parsed_cmd[1]
            if sub_action == "barcode":
                barcode = parsed_cmd[2]
                borrow_tools(curs,barcode)
                print("Successfully made the request")
        else:
            print("invalid command")


def add_category_to_tool(curs, tool_barcode, category_id):
    try:
        query = "INSERT INTO p320_18.\"Tool Categories\"(\"Tool Barcode\",\"Category ID\") VALUES (%s, %s)"
        params = (tool_barcode, category_id,)
        curs.execute(query, params)
    except:
        print("add_category_tool failure")
        return False
    return True


def add_new_category(curs, name):
    try:
        query = "SELECT Count(*) FROM p320_18.\"Categories\""
        curs.execute(query)
        res = curs.fetchone()
        num_categories = res[0]

        category_id = num_categories + 1
        query = "INSERT INTO p320_18.\"Categories\"(\"Category ID\",\"Category Name\") VALUES (%s,%s)"
        params = (category_id, name,)
        curs.execute(query, params)

        print("added category \"{category_name}\" with id \"{id}\"".format(category_name=name, id=category_id))
    except:
        print("add_new_category: failed query")
        return False
    return True


def find_tool_by_barcode(curs, barcode):
    try:
        query = "SELECT \"Tool Name\" FROM p320_18.\"Tools\" WHERE \"Tool Barcode\" = %s;"
        params = (int(barcode),)
        curs.execute(query, params)
        return True
    except:
        print("FIND_TOOL_BY_BARCODE FAILED QUERY")
        return False

    res = curs.fetchone()
    print("\n" + res[0] + "\n")
    return

def delete_tools_by_barcode(curs, barcode):
    try:
        query = "DELETE FROM p320_18.\"Tools\" WHERE \"Tool Barcode\" = %s AND \"Username is null\";"
        params = (int(barcode),)
        curs.execute(query, params)
    except:
        print("DELETE_TOOLS_BY_BARCODE QUERY FAILED")
        return False
    return True

def borrow_tools(curs, barcode):
    try:
        query = "SELECT \"Tool Barcode\" FROM p320_18.\"Request\" WHERE \"Status\" = Available;"
        params = (int(barcode),)
        curs.execute(query, params)
    except:
        print("BORROW_TOOLS QUERY FAILED")
        return False
    return True

def find_tool_by_name(curs, name):
    return


def find_tool_by_category(curs, category):
    return


def create_user(curs, user, pwd, f_name, l_name, email):
    if user_exists(curs, user, pwd):
        print("user already exists in data base")
        return False

    date_obj = date.today()
    today = date_obj.strftime("%d/%m/%Y")

    # insert query
    query = "INSERT INTO p320_18.\"User\"(\"Username\", \"Password\", \"First Name\", \"Last Name\", \"Email\",\"Creation Date\") VALUES  ( %s,%s,%s,%s,%s,TO_DATE(%s,'DD/MM/YYYY'))"

    params = (user, pwd, f_name, l_name, email, today,)
    try:
        curs.execute(query, params)

    except:
        print("CREATE_USER FAILED QUERY")
        return False

    return True


# returns true if user exists in data base.
def user_exists(curs, user, pwd):
    query = "SELECT \"Username\", \"Password\" FROM p320_18.\"User\""
    try:
        curs.execute(query)
    except:
        print("USER_EXISTS FAILED QUERY")
        return False
    res = curs.fetchall()
    for u, p in res:
        if u == user and p == pwd:
            return True
    return False


def main():
    get_login_info()

    try:
        with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                                ssh_username=cs_username,
                                ssh_password=cs_password,
                                remote_bind_address=('localhost', 5432)) as server:
            server.start()
            print("SSH tunnel established")
            params = {
                'database': dbName,
                'user': cs_username,
                'password': cs_password,
                'host': 'localhost',
                'port': server.local_bind_port
            }

            conn = psycopg2.connect(**params)
            curs = conn.cursor()
            command_parser(curs)
            print("Database connection established")
            conn.close()
    except:
        print("Connection failed")


main()