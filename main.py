import mysql.connector as msc
from dotenv import load_dotenv
import os
from pyfiglet import Figlet


def main():
    load_dotenv()
    usr = os.getenv("dbuser")
    dbase = os.getenv("dbname")
    psswd = os.getenv("dbpasswd")
    fig = Figlet(font="small")
    print("\n", fig.renderText("Expense Tracker"))

    conn = msc.connect(host="localhost", user=usr, passwd=psswd, database=dbase)
    #if conn.is_connected():
    #    print("Hello, world!")

    try:
        print(get_operation())
    except KeyboardInterrupt:
        print()

def get_operation():
    menu = """
    (1) Add transaction.
    (2) Monthly expenditure table.
    (3) Transaction list.
    (4) Financial analysis graph.
    (5) Consult AI.
    q to exit
    """
    print(menu)
    while True:
        x = input(":").strip().lower()
        if x=='q':
            raise KeyboardInterrupt
        elif x in "12345":
            return x
        else:
            print("Please choose existing option")
        

        

main()