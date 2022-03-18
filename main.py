from re import T
import psycopg2
from sshtunnel import SSHTunnelForwarder
from datetime import date

cs_username = ""
cs_password = ""
dbName = "p320_18"



# create a login_info.txt file with two lines: a line containing your username on the first and password on the second
def get_login_info():
    f = open("login_info.txt","r")
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
        print("usage:\n\tcreate a new account: create [username] [password] [first name] [last name] [email]\n\tlogin [username] [password]")
        cmd = input()
        parsed_cmd = cmd.split()
        cmd_sz = len(parsed_cmd)
        if len(parsed_cmd) == 0:
            print("no command passed in")
            continue
        action = parsed_cmd[0]
        
        if action == "create" and cmd_sz == 6:
            user = parsed_cmd[1]
            pwd = parsed_cmd[2]
            f_name = parsed_cmd[3]
            l_name = parsed_cmd[4]
            email = parsed_cmd[5]
            if create_user(curs,user,pwd,f_name,l_name,email):    
                print("created user")
            else:
                print("failed to create user")
        elif action == "login" and cmd_sz == 3:
            user = parsed_cmd[1]
            pwd = parsed_cmd[2]
            if user_exists(curs,user,pwd):
                print("logged in as {fuser}".format(fuser=user))
                break
            else:
                print("failed to log in as {fuser}".format(fuser=user))
        else:
            print("invalid command")
        
        
def run_program(curs):
    while True:
        cmd = input()
        parsed_cmd = cmd.split()


def create_user(curs,user,pwd,f_name,l_name,email):
    if user_exists(curs,user,pwd):
        print("user already exists in data base")
        return False
        
    date_obj = date.today()
    today = date_obj.strftime("%d/%m/%Y")
    
    #insert query 
    query = "INSERT INTO p320_18.\"User\"(\"Username\", \"Password\", \"First Name\", \"Last Name\", \"Email\",\"Creation Date\") VALUES  ( %s,%s,%s,%s,%s,TO_DATE(%s,'DD/MM/YYYY'))"
    
    params = (user,pwd,f_name,l_name,email,today,)
    try:
        curs.execute(query, params)
        
    except:
        print("CREATE_USER FAILED QUERY")
        return False

    return True

def user_exists(curs,user,pwd):
    query = "SELECT \"Username\", \"Password\" FROM p320_18.\"User\""
    try:
        curs.execute(query)
    except:
        print("USER_EXISTS FAILED QUERY")
        return False
    res = curs.fetchall()
    for u,p in res:
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