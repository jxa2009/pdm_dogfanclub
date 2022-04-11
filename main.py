"""
Tools Domain Main file
"""

import datetime
from shutil import register_unpack_format
import psycopg2
from sshtunnel import SSHTunnelForwarder
from datetime import date

cs_username = ""
cs_password = ""
dbName = "p320_18"
current_username = ""


# create a login_info.txt file with two lines: a line containing your username on the first and password on the second
def get_login_info():
    """
    Gets the login info from 'login_info.txt'
    to log into the database

    Arguments:
        None

    Returns:
        None
    """
    f = open("login_info.txt", "r")
    global cs_username, cs_password
    cs_username = f.readline().strip()
    cs_password = f.readline().strip()
    return


def command_parser(curs):
    """
    Is called by the main function and calls
    both of the command parser functions

    Arguments:
        curs: the connection cursor

    Returns
        None
    """
    print("Welcome to the tools management system")
    # query usernames and passwords and make sure it exists
    login_user(curs)
    run_program(curs)


def login_user(curs):
    """
    While loop used parsing input to create a new user
    or let an existing user login

    Arguments:
        curs: the connection cursor

    Returns:
        None
    """
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
    """
    While loop that parses a user's commands and
    calls the correct functions for these commands

    Arguments:
        curs:   the connection cursor

    Returns:
        None
    """
    while True:
        # print the command you're gonna add here and how to use it

        print("usage:")
        print("\tcategory new [category_name]")
        print("\t         add [tool_barcode] [category_id]")
        print("\n\tsearch barcode  [tool_barcode]")
        print("\t       name     [tool_name]")
        print("\t       category [tool_category]")
        print("\n\tcatalog add")
        print("\t        edit")
        print("\t        delete")
        print("\n\tcatalog search barcode  [tool_barcode]")
        print("\t        search name     [tool_name]")
        print("\t        search category [tool_category]")
        print("\n\trequests incoming")
        print("\t         outgoing")
        print("\n\tborrow [tool_barcode]")
        
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
                find_tool_by_barcode(curs, barcode, catalog=False)

            elif sub_action == "name":
                name = parsed_cmd[2]
                find_tool_by_name(curs, name, catalog=False)

            elif sub_action == "category":
                category = parsed_cmd[2]
                find_tool_by_category(curs, category, catalog=False)

            else:
                print("invalid search parameter")

        elif action == "borrow":
            barcode = parsed_cmd[1]
            update_request(curs, barcode)

        elif action == "catalog":
            sub_action = parsed_cmd[1]

            if sub_action == "edit":
                print("what would you like to edit? (toolname,shareable,description) type one of these ")

                cmd2 = input()
                parsed_cmd2 = cmd2.split()
                action = parsed_cmd2[0]

                if (action == "toolname"):
                    print("What toolname would you like to change for toolname(barcode))? ")
                    cmd2 = input()
                    print("What would you like new toolname to be (the new toolname))? ")
                    cmd3 = input()

                    toolbarcode = cmd2
                    newtoolname = cmd3
                    edit_new_toolname(curs, int(toolbarcode), newtoolname)
                    print("Added new toolname success")


                elif (action == "shareable"):
                    print("What toolname would you like to change for shareable(barcode)? ")
                    cmd2 = input()
                    print("What would you like new shareable status to be (the new status shareable or unshareble)? ")
                    cmd3 = input()

                    toolbarcode = cmd2
                    newshareable = cmd3
                    edit_shareable(curs, int(toolbarcode), newshareable)

                    print("Added newshareable succes")


                elif (action == "description"):
                    print("What toolname would you like to change for description(barcode)? ")
                    cmd2 = input()
                    print("What would you like new description to be (the new description)? ")
                    cmd3 = input()

                    toolbarcode = cmd2
                    newdescription = cmd3
                    edit_description(curs, toolbarcode, newdescription)
                    print("Added newdescription success")

                else:
                    print("invalid command")

            elif sub_action == "delete":
                print("type the barcode of the tool you would like to delete(barcode)")
                cmd2 = input()
                delete_new_toolname(curs, int(cmd2))
                print("delete tool success")

            elif sub_action == "add":
                print("What tool would you like to add (barcode)")
                cmd2 = input()
                add_new_toolname_User(curs, int(cmd2))
                print("Added tool success")

            elif sub_action == "search" and cmd_sz == 4:
                sub_action2 = parsed_cmd[2]

                if sub_action2 == "barcode":
                    barcode = parsed_cmd[3]
                    find_tool_by_barcode(curs, barcode, catalog=True)

                elif sub_action2 == "name":
                    name = parsed_cmd[3]
                    find_tool_by_name(curs, name, catalog=True)

                elif sub_action2 == "category":
                    category = parsed_cmd[3]
                    find_tool_by_category(curs, category, catalog=True)

                else:
                    print("invalid search parameter")

            else:
                print("invalid command")

        #incoming requests
        elif action == "requests":
            sub_action = parsed_cmd[1]
            
            if sub_action == "incoming":
                print("incoming request")
                incoming_request(curs, )

            elif sub_action == "outgoing":
                print("outgoing requests")
                outgoing_request(curs, )
        
        elif (action == "exit"):
            break
        else:
            print("invalid command")


def incoming_request(curs):
    global current_username
    exit = False
    while(not exit):
        exit_subaction = False
        try:
            query = "SELECT T.\"Tool Name\", R.\"Status\", R.\"Date Required\", R.\"Duration\", R.\"Tool Barcode\", R.\"Username\" FROM p320_18.\"Tools\" T, p320_18.\"Request\" R WHERE R.\"Tool Owner\" = %s AND R.\"Tool Barcode\" = T.\"Tool Barcode\";"
            params = (current_username,)
            curs.execute(query, params)
        except Exception as e:
            print(e)
            print("incoming_request failure")
            return False

        res = curs.fetchall()
        if len(res) > 0:
            print()
            for i in range(len(res)):
                print(str(i+1) + "\tTool Name:\t" + res[i][0] + "\n\tStatus:\t\t" + res[i][1] + "\n\tDate Required:\t" + res[i][2].strftime('%m/%d/%Y') + "\n\tDuration:\t" + str(res[i][3]) + " days\n")
        else:
            print("\nYou do not hav any incoming requests\n")
            return True

        while(not exit_subaction):
            reply = input("\nSelect a Tool request to manage by inputting the row number of the tool or type 'exit' to exit the request manager\n")
            if reply[:1] == 'e' or reply[:1] == 'E':
                print("Exiting request manager")
                exit_subaction = True
                exit = True
            elif reply.isnumeric():
                row = int(reply) - 1
                if row < len(res) and row >= 0:

                    if res[row][1] != 'Pending':
                        print("\nThis tool has already been " + res[row][1])
                        continue
                    else:
                        while(True):
                            reply2 = str(input("\nType 'accept' to accept the request, 'deny' to deny the request, or 'cancel' to exit\n").lower().strip())
                            if reply2[:1] == 'a' or reply2[:1] == 'A':
                                manage_request(curs, res[row][4], res[row][5], res[row][2], accept=True)
                                exit_subaction = True
                                break
                            elif reply2[:1] == 'd' or reply2[:1] == 'D':
                                manage_request(curs, res[row][4], res[row][5], res[row][2], accept=False)
                                exit_subaction = True
                                break
                            elif reply2[:1] == 'c' or reply2[:1] == 'C':
                                break
                            else:
                                print("Invalid command")
                else:
                    print("Invalid row")
            else:
                print("Invalid input")

    return True


def manage_request(curs, barcode, requester, date_required, accept):
    global current_username
    try:
        if accept:
            reply = input("\nExpected date returned?   (MM/DD/YYYY)\n")
            date_returned = datetime.datetime.strptime(reply, "%m/%d/%Y").date()
            query = "UPDATE p320_18.\"Request\" SET \"Status\" = %s, \"Date Returned\" = %s WHERE \"Tool Barcode\" = %s AND \"Username\" = %s AND \"Tool Owner\" = %s AND \"Date Required\" = %s;"
            params = ('Accepted', date_returned.strftime("%m/%d/%Y"), barcode, requester, current_username, date_required,)
        else:
            query = "UPDATE p320_18.\"Request\" SET \"Status\" = %s WHERE \"Tool Barcode\" = %s AND \"Username\" = %s AND \"Tool Owner\" = %s AND \"Date Required\" = %s;"
            params = ('Denied', barcode, requester, current_username, date_required,)
        curs.execute(query, params)
    except Exception as e:
        print(e)
        print("manage_request failure")
        return False

    if accept:
        print("Successfully accepted the tool request")
    else:
        print("Successfully denied the tool request")
    
    return True


#outgoing request stub
def outgoing_request(curs, ):
    global current_username
    try:
        query = "UPDATE p320_18.\"Tools\" SET \"Tool Name\" = %s WHERE p320_18.\"Tools\".\"Tool Barcode\" = %s AND p320_18.\"Tools\".\"Username\" = %s;"
        params = (newtoolname, toolbarcode, current_username,)
        curs.execute(query, params)
    except Exception as e:
        print(e)
        print("outgoing_request failure")
        return False
    return True


def update_request(curs, barcode):
    """
    Checks to see if a request can be made. If so, add the request
    to the request table. If the tool is not sharable, deny the request.
    If the tool is unowned, prompt the user to add the tool to their catalog

    Argumets:
        curs:       the connection cursor
        barcode:    the barcode of the tool to be requested for

    Returns:
        True:       if queries pass
        False:      if queries fail
    """
    try:
        if not is_tool_owned(curs, barcode):
            print("\nThis tool is not owned.")
            
            while (True):
                reply = str(input("\nWould you like to add the tool to your catalog? (y/n):\n").lower().strip())
                if reply[:1] == 'y' or reply[:1] == 'Y':
                    add_new_toolname_User(curs, barcode)
                    print("\nTool successfully added")
                    return True
                elif reply[:1] == 'n' or reply[:1] == 'N':
                    print("Tool has not been added to your catalog")
                    return True
                else:
                    print("\nInvalid input. Please enter: 'yes' or 'no'")

        elif not is_tool_shareable(curs, barcode):
            print("\nThis tool is not sharable at the moment")
            return False

        print("\nDate Required?   (MM/DD/YYYY)")
        cmd1 = input()
        date1 = datetime.datetime.strptime(cmd1, "%m/%d/%Y").date()
        print("\nDuration in number of days?")
        cmd2 = input()

        # run this query to insert into table
        query1 = "INSERT INTO p320_18.\"Request\"(\"Tool Barcode\",\"Username\",\"Tool Owner\",\"Status\",\"Date Required\",\"Duration\") VALUES (%s, %s, %s, %s, TO_DATE(%s,'MM/DD/YYYY'), %s)"
        # run this query to get username associated with tool requested
        query2 = "SELECT \"Username\" FROM p320_18.\"Tools\" WHERE \"Tool Barcode\" = %s"

        params = (int(barcode),)
        curs.execute(query2, params)
        res = curs.fetchall()
        status = 'Pending'
        params2 = (int(barcode), current_username, res[0], status, date1.strftime("%m/%d/%Y"), int(cmd2),)
        curs.execute(query1, params2)
    except Exception as e:
        print(e)
        print("update_request failure")
        return False
    print("\nSuccessfully made the request")
    return True


def is_tool_owned(curs, barcode):
    """
    Determines if a tool has an owner

    Arguments:
        curs:       the connection cursor
        barcode:    the barcode of the tool to check
    
    Returns:
        True:       if the tool is owned by someone
        False:      if the tool is unowned
    """
    try:
        query = "SELECT \"Username\" FROM p320_18.\"Tools\" WHERE \"Tool Barcode\" = %s;"
        params = (barcode,)
        curs.execute(query, params)
    except Exception as e:
        print(e)
        print("is_tool_owned failed query")
        return False
    res = curs.fetchone()
    return not res[0] == None


def is_tool_shareable(curs, barcode):
    """
    Determines if a tool is shareable

    Aguments:
        curse:      the connection cursor
        barcode:    the barcode of the tool to check

    Returns:
        True:       if the tool is shareable
        False:      if the tool is unshareable
    """
    try:
        query = "SELECT \"Shareable\" FROM p320_18.\"Tools\" WHERE \"Tool Barcode\" = %s;"
        params = (barcode,)
        curs.execute(query, params)
    except Exception as e:
        print(e)
        print("is_tool_sharable failed query")
        return False
    res = curs.fetchone()
    return res[0] == 'Shareable'


def edit_new_toolname(curs, toolbarcode, newtoolname):
    """
    Updates the name of a user's tool

    Arguments:
        curs:           the connection cursor
        toolbarcode:    the barcode of the tool to be edited
        newtoolname:    the new tool name

    Returns:
        True:           if successfully updated the tool's name
        False:          if failed to update the tool's name
    """
    global current_username
    try:
        query = "UPDATE p320_18.\"Tools\" SET \"Tool Name\" = %s WHERE p320_18.\"Tools\".\"Tool Barcode\" = %s AND p320_18.\"Tools\".\"Username\" = %s;"
        params = (newtoolname, toolbarcode, current_username,)
        curs.execute(query, params)
    except Exception as e:
        print(e)
        print("edit_new_toolname failure")
        return False
    return True


def edit_shareable(curs, toolbarcode, newshareable):
    """
    Updates the Shareable attribute of a user's tool

    Arguments:
        curs:           the connection cursor
        toolbarcode:    the barcode of the tool to be edited
        newshareable:   the sharable attributte ('Shareable' or 'Unshareable' )

    Returns:
        True:           if succeffully updated the Shareable attribiute
        False:          if failed to update the Shareable attribiute
    """
    global current_username
    try:
        query = "UPDATE p320_18.\"Tools\" SET \"Shareable\" = %s WHERE p320_18.\"Tools\".\"Tool Barcode\"  = %s AND p320_18.\"Tools\".\"Username\" = %s;"
        params = (newshareable, toolbarcode, current_username,)
        curs.execute(query, params)
    except Exception as e:
        print(e)
        print("edit_shareable failure")
        return False
    return True


def edit_description(curs, toolbarcode, newdescription):
    """
    Updates the description of a user's tool with a new description

    Arguments:
        curs:           the connection cursor
        toolbarcode:    the barcode of the tool to be edited
        newdescription: the new description

    Returns:
        True:           if succeffully updated the description
        False:          if failed to update the description
    """
    global current_username
    try:
        query = "UPDATE p320_18.\"Tools\" SET \"Description\" = %s WHERE p320_18.\"Tools\".\"Tool Barcode\" = %s AND p320_18.\"Tools\".\"Username\"= %s ;"
        params = (newdescription, toolbarcode, current_username,)
        curs.execute(query, params)
    except Exception as e:
        print(e)
        print("edit_description failure")
        return False
    return True


def delete_new_toolname(curs, toolbarcode):
    """
    Removes a tool form a user's catalog

    Arguments:
        curse:          the connection cursor
        toolbarcode:    the barcode of the tool to be removed

    Returns:
        True:           if the tool was successfully removed for the user's catalog
        False:          if failed to remove the tool from the user's catalog
    """
    global current_username
    try:
        query = "UPDATE p320_18.\"Tools\" SET \"Username\" = NULL WHERE p320_18.\"Tools\".\"Tool Barcode\" = %s AND p320_18.\"Tools\".\"Username\" = %s ;"
        params = (toolbarcode, current_username,)
        curs.execute(query, params)
    except Exception as e:
        print(e)
        print("delete_new_toolname failure")
        return False
    return True


def add_new_toolname_User(curs, toolbarcode):
    """
    Adds a new tool to a user's catalog if that tool is not already owned

    Arguments:
        curs:           the connection cursor
        toolbarcode:    the barcode of the tool to be added

    Returns:
        True:           if the tool was successfully added to a user's catalog
        False:          if failed to add a tool to the user's catalog
    """
    global current_username
    try:
        query = "UPDATE p320_18.\"Tools\" SET \"Username\" = %s WHERE p320_18.\"Tools\".\"Tool Barcode\" = %s AND  p320_18.\"Tools\".\"Username\" IS NULL ;"
        params = (current_username, toolbarcode,)
        curs.execute(query, params)
    except Exception as e:
        print(e)
        print("add_new_toolname_User failure")
        return False
    return True


# This might need a (try: except:) around the query
def category_id_exists(curs, category_id):
    """
    Determnes if a category ID exists in the database

    Arguments:
        curs:           the connection cursor
        category_id:    the ID of he category to look for

    Returns:
        True:           if the category ID exists
        False:          if the category ID does not exist
    """
    query = "SELECT \"Category ID\" FROM p320_18.\"Categories\""
    curs.execute(query)
    res = curs.fetchall()
    for row in res:
        id = str(row[0])
        if id == category_id:
            return True
    return False


# This might need a (try: except:) around the query
def category_name_exists(curs, category_name):
    """
    Determines if a category exists in the database

    Arguments:
        curse:          the connection cursor
        category_name:  the name of the category to search for

    Returns:
        True:           if the category name exists in the database
        False:          if the category name does not exist in the database
    """
    # SELECT "Category Name" FROM p320_18."Categories" check if category exists before trying to insert
    query = "SELECT \"Category Name\" FROM p320_18.\"Categories\""
    curs.execute(query)
    res = curs.fetchall()
    for row in res:
        name = row[0]
        if name == category_name:
            return True
    return False


# This might need a (try: except:) around the query
def get_tools_categories(curs, tool_barcode):
    """
    Returns a list of all the categories a tool belongs to

    Arguments:
        curs:           the connection cusor
        tool_barcode:   the barcode of the specified tool

    Returns:
        The list of all the categories a tool belongs to
    """
    query = "SELECT \"Category ID\" FROM p320_18.\"Tool Categories\" WHERE p320_18.\"Tool Categories\".\"Tool Barcode\" = %s"
    params = (tool_barcode,)

    curs.execute(query, params)

    res = curs.fetchall()

    return res


def add_category_to_tool(curs, tool_barcode, category_id):
    """
    Adds the specified category to the tool with the specified barcode

    Arguments:
        curs:           the connection cursor
        tool_barcode:   the barcode of the tool to add the category to
        category_id:    the ID of category to add to the tool

    Returns:
        True:           if the category was successfully added to the tool
        False:          if failed adding the category to the tool
    """
    if not category_id_exists(curs, category_id):
        return False

    tool_categories = get_tools_categories(curs, tool_barcode)

    for row in tool_categories:
        curr_id = row[0]
        if category_id == str(curr_id):
            print("tool is already in category")
            return False
    # make sure tool already not allocated to the category
    try:
        query = "INSERT INTO p320_18.\"Tool Categories\"(\"Tool Barcode\",\"Category ID\") VALUES (%s, %s)"
        params = (tool_barcode, category_id,)
        curs.execute(query, params)
    except Exception as e:
        print(e)
        print("add_category_tool failure")
        return False
    return True


def add_new_category(curs, name):
    """
    Adds the specified category to the database

    Arguments:
        curs:   the connection cursor
        name:   the name of the category to be added

    Returns:
        True:   if category was succefully added
        False:  if failed to add category
    """
    # check if category exists before trying to insert
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
    except Exception as e:
        print(e)
        print("add_new_category: failed query")
        return False
    return True


def find_tool_by_barcode(curs, barcode, catalog):
    """
    Finds and prints the name of the tool that has the specified barcode

    Arguments:
        curs:       the connection cursor
        barcode:    the barcode to search for
        catalog:    True if searching through the user's catalog,
                    False if searching through the entire database

    Returns:
        True:   if successfully seached for a tool by barcode
        False:  if failed to search for a tool by barcode
    """
    global current_username
    try:
        if catalog:
            query = "SELECT \"Tool Name\", \"Shareable\", \"Description\" FROM p320_18.\"Tools\" WHERE \"Tool Barcode\" = %s AND \"Username\" = %s;"
            params = (int(barcode), current_username)
        else:
            query = "SELECT \"Tool Name\", \"Shareable\", \"Description\" FROM p320_18.\"Tools\" WHERE \"Tool Barcode\" = %s;"
            params = (int(barcode),)

        curs.execute(query, params)
    except Exception as e:
        print(e)
        print("FIND_TOOL_BY_BARCODE FAILED QUERY")
        return False

    res = curs.fetchone()
    if res != None:
        print("\nName: " + res[0] + "\n" + res[1] + "\n")
        if res[2] != None:
            print(res[2] + "\n")
    else:
        if catalog:
            print("\nYou do not own a tool with the barcode: " + barcode + "\n")
        else:
            print("\nThere is no tool with barcode: " + barcode + "\n")
    return True


def find_tool_by_name(curs, name, catalog):
    """
    Finds and prints the name of every tool that contains the specified string in the tool's name

    Arguments:
        curs:   the connection cursor
        name:   the string to search for
        catalog:    True if searching through the user's catalog,
                    False if searching through the entire database

    Returns:
        True:   if successfully seached for tools by name
        False:  if failed to search for tools by name
    """
    try:
        global current_username
        if catalog:
            query = "SELECT \"Tool Barcode\", \"Tool Name\", \"Shareable\", \"Description\" FROM p320_18.\"Tools\" WHERE \"Tool Name\" LIKE %s AND \"Username\" = %s ORDER BY \"Tool Name\" ASC;"
            params = ('%' + name + '%', current_username)
        else:
            query = "SELECT \"Tool Barcode\", \"Tool Name\", \"Shareable\", \"Description\" FROM p320_18.\"Tools\" WHERE \"Tool Name\" LIKE %s ORDER BY \"Tool Name\" ASC;"
            params = ('%' + name + '%',)
        curs.execute(query, params)
    except Exception as e:
        print(e)
        print("FIND_TOOL_BY_NAME FAILED QUERY")
        return False

    res = curs.fetchall()
    if len(res) > 0:
        print()
        for tool in res:
            print("Barcode: " + str(tool[0]) + "\n" + "Name: " + tool[1] + "\n" + tool[2])
            if tool[3] != None:
                print(tool[3])
            print()
    else:
        if catalog:
            print("\nYou do not own any tools that contain the name: " + name + "\n")
        else:
            print("\nThere are no tools that contain the name: " + name + "\n")
    return True


def find_tool_by_category(curs, category, catalog):
    """
    Finds and print the name of all tools of a specified category

    Arguments:
        curs:       the connection cursor
        category:   the category to be searched for
        catalog:    True if searching through the user's catalog,
                    False if searching through the entire database

    Returns:
        True:       if successfully search for a category
        False:      if failed to search for a category
    """
    try:
        global current_username
        if catalog:
            query = "SELECT \"Tool Barcode\", \"Tool Name\", \"Shareable\", \"Description\" FROM p320_18.\"Tools\" WHERE \"Username\" = %s AND \"Tool Barcode\" IN (SELECT \"Tool Barcode\" FROM  p320_18.\"Tool Categories\" WHERE \"Category ID\" = (SELECT \"Category ID\" FROM p320_18.\"Categories\" WHERE \"Category Name\" = %s)) ORDER BY \"Tool Name\" ASC;"
            params = (current_username, category,)
        else:
            query = "SELECT \"Tool Barcode\", \"Tool Name\", \"Shareable\", \"Description\" FROM p320_18.\"Tools\" WHERE \"Tool Barcode\" IN (SELECT \"Tool Barcode\" FROM  p320_18.\"Tool Categories\" WHERE \"Category ID\" = (SELECT \"Category ID\" FROM p320_18.\"Categories\" WHERE \"Category Name\" = %s)) ORDER BY \"Tool Name\" ASC;"
            params = (category,)
        curs.execute(query, params)
    except Exception as e:
        print(e)
        print("FIND_TOOL_BY_CATEGORY FAILED QUERY")
        return False

    res = curs.fetchall()
    if len(res) > 0:
        print("\n")
        for tool in res:
            print("Barcode: " + str(tool[0]) + "\n" + "Name: " + tool[1] + "\n" + tool[2])
            if tool[3] != None:
                print(tool[3])
            print()
    else:
        if catalog:
            print("\nYou do not own any tools in the category: " + category + "\n")
        else:
            print("\nthere are no tools in the category: " + category + "\n")
    return True


def create_user(curs, user, pwd, f_name, l_name, email):
    """
    Creates a new user and adds it to the database

    Arguments:
        curs:   the connection cursor
        user:   the username of the new user
        pwd:    the password of the new user
        f_name: the firstname of the new user
        l_name: the last name of the new user
        email:  the email of the new user

    Returns:
        True:   if successfully created a new user
        False:  if faild creating a new user
    """
    if user_exists(curs, user, pwd):
        print("user already exists in data base")
        return False

    date_obj = date.today()
    today = date_obj.strftime("%d/%m/%Y")

    # insert query
    query = "INSERT INTO p320_18.\"User\"(\"Username\", \"Password\", \"First Name\", \"Last Name\", \"Email\",\"Creation Date\",\"Last Access Date\") VALUES  ( %s,%s,%s,%s,%s,TO_DATE(%s,'DD/MM/YYYY'),TO_DATE(%s,'DD/MM/YYYY'))"

    params = (user, pwd, f_name, l_name, email, today, today,)
    try:
        curs.execute(query, params)

    except Exception as e:
        print(e)
        print("CREATE_USER FAILED QUERY")
        return False

    return True


def user_exists(curs, user, pwd):
    """
    Returns True if the selected user is in the database
    Returns False otherwise

    Arguments:
        curs:   the connection cursor
        user:   the username of the user selected
        pwd:    the password of the user selected

    Returns:
        True:   if user is in the database
        False:  if user is not in the database
    """
    query = "SELECT \"Username\", \"Password\" FROM p320_18.\"User\""
    try:
        curs.execute(query)
    except Exception as e:
        print(e)
        print("USER_EXISTS FAILED QUERY")
        return False
    res = curs.fetchall()
    for u, p in res:
        if u == user and p == pwd:
            return True
    return False


def main():
    """
    Main function for the program
    Initializes the connection to the database

    Arguemnts:
        None

    Returns:
        None
    """
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
            print("Database connection established")
            command_parser(curs)
            conn.commit()
            conn.close()
    except Exception as e:
        print(e)
        print("Connection failed")


main()