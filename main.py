import psycopg2
from sshtunnel import SSHTunnelForwarder


db_username = ""
db_password = ""
dbName = "p320_18"



# create a login_info.txt file with two lines: a line containing your username on the first and password on the second
def get_login_info():
    f = open("login_info.txt","r")
    global db_username, db_username
    db_username = f.readline().strip()
    db_username = f.readline().strip()
    
def command_parser():
    print("Welcome to the tools management system. Please login:")

    # query usernames and passwords and make sure it exists



#function that queries username and password from the database
# returns true if exists, false else
def account_exists():
    username = input("Username: ")
    password = input("Password: ")


def main():
    get_login_info()
    try:
        with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                                ssh_username=db_username,
                                ssh_password=db_username,
                                remote_bind_address=('localhost', 5432)) as server:
            server.start()
            print("SSH tunnel established")
            params = {
                'database': dbName,
                'user': db_username,
                'password': db_username,
                'host': 'localhost',
                'port': server.local_bind_port
            }


            conn = psycopg2.connect(**params)
            curs = conn.cursor()

            print("Database connection established")

            command_parser()

            
            conn.close()
            print("Database connection closed")
    except:
        print("Connection failed")

main()