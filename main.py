import mysql.connector as msc
from dotenv import load_dotenv
import os


def main():
    load_dotenv()
    usr = os.getenv("dbuser")
    dbase = os.getenv("dbname")
    psswd = os.getenv("dbpasswd")

    conn = msc.connect(host="localhost", user=usr, passwd=psswd, database=dbase)
    
    if conn.is_connected():
        print("Hello, world!")
        

main()