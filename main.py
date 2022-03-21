import psycopg2
from sshtunnel import SSHTunnelForwarder
from datetime import date

cs_username = ""
cs_password = ""
dbName = "p320_18"
current_username = ""


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
                global current_username
                current_username = user
                
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
        print("\n\t modify [add,edit,delete]")
        
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
                borrow_tools(curs, barcode)
                print("Successfully made the request")
        elif action == "modify":
            sub_action = parsed_cmd[1]

            if sub_action == "edit":
                print("what would you like to edit? (toolname,shareable,description) type one of these ")

                cmd2 = input()
                parsed_cmd2 = cmd2.split()
                action = parsed_cmd2[0]

                if (action == "toolname"):
                    print ("What toolname would you like to change for toolname( the old toolname)? ")
                    cmd2 = input()
                    print ("What would you like new toolname to be (the new toolname))? ")
                    cmd3 = input()

                    toolname = cmd2
                    newtoolname = cmd3
                    edit_new_toolname(curs, toolname, newtoolname)
                    print("Added new toolname success")


                elif (action == "shareable"):
                    print ("What toolname would you like to change for shareable(toolname)? ")
                    cmd2 = input()
                    print ("What would you like new shareable status to be (the new status shareable or unshareble)? ")
                    cmd3 = input()

                    toolname = cmd2
                    newshareable = cmd3
                    edit_shareable(curs, toolname, newshareable)

                    print("Added newshareable succes")


                elif (action == "description"):
                    print ("What toolname would you like to change for description(toolname)? ")
                    cmd2 = input()
                    print ("What would you like new description to be (the new description)? ")
                    cmd3 = input()

                    toolname = cmd2
                    newdescription = cmd3
                    edit_description(curs, toolname, newdescription)
                    print("Added newdescription success")

                else:
                    print("invalid command")
            elif sub_action == "delete":
                print("type the name of the tool you would like to delete")
                cmd2 = input()
                delete_new_toolname(curs, cmd2)
                print("delete tool success")

            elif sub_action == "add":
                print("What tool would you like to add")
                cmd2 = input()
                add_new_toolname_User(curs, cmd2)

                print("Added tool succes")


            else:
                print("invalid command")
        elif (action == "exit"):
            break
        else:
            print("invalid command")


def edit_new_toolname(curs, toolname, newtoolname):
    global current_username
    try:
        query = "UPDATE p320_18.\"Tools\" SET \"Tool Name\" = %s WHERE p320_18.\"Tools\".\"Tool Name\" = %s AND p320_18.\"Tools\".\"Username  \" = %s;"
        params = (newtoolname, toolname, current_username,)
        curs.execute(query, params)
    except:
        print("edit_new_toolname failure")
        return False
    return True


def edit_shareable(curs, toolname, newshareable):
    global current_username
    try:
        query = "UPDATE p320_18.\"Tools\" SET \"Shareable\" = %s WHERE p320_18.\"Tools\".\"Tool Name\"  = %s AND p320_18.\"Tools\".\"Username \" = %s;"
        params = (newshareable, toolname, current_username,)
        curs.execute(query, params)
    except:
        print("edit_shareable failure")
        return False
    return True


def edit_description(curs, toolname, newdescription):
    global current_username
    try:
        query = "UPDATE p320_18.\"Tools\" SET \"Description\" = %s WHERE p320_18.\"Tools\".\"Tool Name\" = %s AND p320_18.\"Tools\".\"Username \"= %s ;"
        params = (newdescription, toolname, current_username,)
        curs.execute(query, params)
    except:
        print("edit_description failure")
        return False
    return True


def delete_new_toolname(curs, toolname):
    global current_username
    try:
        query = "UPDATE p320_18.\"Tools\" SET \"Username\" = %s WHERE p320_18.\"Tools\".\"Tool Name\" = %s AND p320_18.\"Tools\".\"Username  \" = %s ;"
        params = (NULL, toolname, current_username,)  # how to check if no user is here
        curs.execute(query, params)
    except:
        print("delete_new_toolname failure")
        return False
    return True


def add_new_toolname_User(curs, toolname):
    global current_username
    try:
        query = "UPDATE p320_18.\"Tools\" SET \"Username\" = %s WHERE p320_18.\"Tools\".\"Tool Name\" = %s AND  p320_18.\"Tools\".\"Username\" IS NULL ;"
        params = (current_username, toolname,)
        curs.execute(query, params)
    except:
        print("add_new_toolname_User failure")
        return False
    return True


def category_id_exists(curs, category_id):
    query = "SELECT \"Category ID\" FROM p320_18.\"Categories\""
    curs.execute(query)
    res = curs.fetchall()
    for row in res:
        id = str(row[0])
        if id == category_id:
            return True
    return False


def category_name_exists(curs, category_name):
    # SELECT "Category Name" FROM p320_18."Categories" check if category exists before trying to insert
    query = "SELECT \"Category Name\" FROM p320_18.\"Categories\""
    curs.execute(query)
    res = curs.fetchall()
    for row in res:
        name = row[0]
        if name == category_name:
            return True
    return False


# return all the categories a tool belongs to
def get_tools_categories(curs, tool_barcode):
    query = "SELECT \"Category ID\" FROM p320_18.\"Tool Categories\" WHERE p320_18.\"Tool Categories\".\"Tool Barcode\" = 156"
    params = (tool_barcode,)

    curs.execute(query, params)

    res = curs.fetchall()

    return res


def add_category_to_tool(curs, tool_barcode, category_id):
    if not category_id_exists(curs, category_id):
        return False

    tool_categories = get_tools_categories(curs, tool_barcode)

    for row in tool_categories:
        curr_id = row[0]
        if category_id == str(curr_id):
            print("tool is already in category")
            return False

    # make sure tool already not allocated to the caategory
    try:
        query = "INSERT INTO p320_18.\"Tool Categories\"(\"Tool Barcode\",\"Category ID\") VALUES (%s, %s)"
        params = (tool_barcode, category_id,)
        curs.execute(query, params)
    except:
        print("add_category_tool failure")
        return False
    return True


def add_new_category(curs, name):
    if category_name_exists(curs, name):
        return False

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
    except:
        print("FIND_TOOL_BY_BARCODE FAILED QUERY")
        return False

    res = curs.fetchone()
    if res != None:
        print("\n" + res[0] + "\n")
    else:
        print("\nthere is no tool with barcode: " + barcode + "\n")
    return True


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
        query = "SELECT \"Tool Barcode\" FROM p320_18.\"Request\" WHERE \"Status\" = 'Accepted';"
        params = (int(barcode),)
        curs.execute(query, params)
        result = curs.fetchall()
        print("List of Tools")
        for row in result:
            print(row)
            print("\n")
    except:
        print("BORROW_TOOLS QUERY FAILED")
        return False
    return True


def find_tool_by_name(curs, name):
    try:
        query = "SELECT \"Tool Name\" FROM p320_18.\"Tools\" WHERE \"Tool Name\" LIKE %s ORDER BY \"Tool Name\" ASC;"
        params = ('%' + name + '%',)
        curs.execute(query, params)
    except:
        print("FIND_TOOL_BY_NAME FAILED QUERY")
        return False

    res = curs.fetchall()
    if len(res) > 0:
        print("\n")
        for tool in res:
            print(tool[0] + "\n")
    else:
        print("\nthere is no tool that contains the name: " + name + "\n")
    return True


def find_tool_by_category(curs, category):
    try:
        query = "SELECT \"Tool Name\" FROM p320_18.\"Tools\" WHERE \"Tool Barcode\" IN (SELECT \"Tool Barcode\" FROM  p320_18.\"Tool Categories\" WHERE \"Category ID\" = (SELECT \"Category ID\" FROM p320_18.\"Categories\" WHERE \"Category Name\" = %s)) ORDER BY \"Tool Name\" ASC;"
        params = (category,)
        curs.execute(query, params)
    except:
        print("FIND_TOOL_BY_CATEGORY FAILED QUERY")
        return False

    res = curs.fetchall()
    if len(res) > 0:
        print("\n")
        for tool in res:
            print(tool[0] + '\n')
    else:
        print("\nthere are no tools in the category: " + category + "\n")
    return True


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
            conn.commit()
            conn.close()
    except:
        print("Connection failed")


main()