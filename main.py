import psycopg2
from sshtunnel import SSHTunnelForwarder
import base64


username = ""
password = ""
dbName = "p320_18"

def get_login_info():
    f = open("login_info.txt","r")
    global username, password
    username = f.readline().strip()
    password = f.readline().strip()
    
    
def main():
    get_login_info()
    try:
        with SSHTunnelForwarder(('starbug.cs.rit.edu', 22),
                                ssh_username=username,
                                ssh_password=password,
                                remote_bind_address=('localhost', 5432)) as server:
            server.start()
            print("SSH tunnel established")
            params = {
                'database': dbName,
                'user': username,
                'password': password,
                'host': 'localhost',
                'port': server.local_bind_port
            }


            conn = psycopg2.connect(**params)
            curs = conn.cursor()

            print("Database connection established")


            
            conn.close()
            print("Database connection closed")
    except:
        print("Connection failed")

main()