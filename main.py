import psycopg2
from sshtunnel import SSHTunnelForwarder


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
    login_user(curs)
    # query usernames and passwords and make sure it exists
    
def login_user(curs):
    while True:
        print("\tusage:\n\tcreate a new account: create [username] [password]\n\tlogin [username] [password]")
        cmd = input()
        parsed_cmd = cmd.split()
        if len(parsed_cmd) != 3:
            print("Incorrect length")
            continue
        action = parsed_cmd[0]
        user = parsed_cmd[1]
        pwd = parsed_cmd[2]
        
        if action == "create":
            if create_user(curs,user,pwd):
                print("created user")
            else:
                print("failed to create user")
        elif action == "login":
            if user_exists(curs,user,pwd):
                print("logged in as {fuser}".format(fuser=user))
                break
            else:
                print("failed to log in as {fuser}".format(fuser=user))
        else:
            print("invalid command")
        
        cmd = input()
        parsed_cmd = cmd.split()
        
            
def user_exists(curs,user,pwd):
    query = "SELECT \"Username\", \"Password\" FROM p320_18.\"User\""
    curs.execute(query)
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