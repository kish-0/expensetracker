import mysql.connector as msc
from dotenv import load_dotenv
import os
from pyfiglet import Figlet
from tabulate import tabulate


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
        op = get_operation()
        match op:
            case "1":
                get_transaction()
            case _:
                print(op)
    except KeyboardInterrupt:
        print()


def get_operation():
    menu = """
    (1) Add transaction.
    (2) Monthly expenditure table.
    (3) View Transactions.
    (4) Financial analysis graph.
    (5) Consult AI.
    q to exit
    """
    print(menu)
    while True:
        x = input(": ").strip().lower()
        if x=='q':
            raise KeyboardInterrupt
        elif x in "12345":
            return x
        else:
            print("Please choose existing option")

# NEED TO TEST SEPERATELY 

def get_transaction():
        while True: # Getting amount - making sure a float value is given
            try:
                a = float(input("Amount spent?\n: ")) 
                break
            except:
                print("Please enter floating point / integer value")
                continue

        while True: # Getting category - making sure that given one is in our list of possible categories
            categories = "utilities, groceries, transportation, dining, shopping, entertainment, travel, medical, miscellaneous"
            print("Expenditure category?\n")
            c = input(f"Kindly choose from following categories - {categories} \n: ").strip().lower()
            if c in categories : 
                break
        
        while True: # Getting date - making sure its in right formal for sql
            da = input("Enter date of expenditure (YYYY-MM-DD)?\n: ")
            try:
                dl = da.split("-")
                y = dl[0]
                m = dl[1]
                d = dl[2]
                if len(y)==4 and len(m)==len(d)==2 and 0<int(m)<13 and 0<int(d)<32 :
                    break
                else:
                    raise ValueError

            except:
                print("Please adhere to format (YYYY-DD-MM)")
                continue
        
        while True: # Getting short description - making sure its under 50 characters
            desc = input("Enter short description under 50 characters?\n: ")
            if not desc:
                desc = "..."
            elif len(desc) > 50:
                desc = desc[0:51]
            break
        
        l = [[a,c,da,desc]]
        print("\n")
        print(tabulate(l, headers=['Amount', 'Category', 'Date', 'Description'], tablefmt="simple"))
        print("\n")
        print("Are you sure about entering above mentioned values (action cannot be undone)", end=" ")
        while True:
            ans = input("[y/n]: ").strip().lower()
            if ans in "yn":
                break
            else:
                continue


main()