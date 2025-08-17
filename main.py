import mysql.connector as msc
from dotenv import load_dotenv
import os
import datetime
from pyfiglet import Figlet
import sys
from tabulate import tabulate


def main():
    load_dotenv()
    usr = os.getenv("dbuser")
    dbase = os.getenv("dbname")
    psswd = os.getenv("dbpasswd")
    global tbl
    tbl = os.getenv("tbname")
    global conn
    conn = msc.connect(host="localhost", user=usr, passwd=psswd, database=dbase)
    global curs 
    curs = conn.cursor()

    #if conn.is_connected():
    #    print("Hello, world!")
    while True:
        try:
            op = get_operation()
            match op:
                case "1":
                    get_transaction()
                    if not yesorno():
                        break                        
                case "2":
                    view_transaction()
                    if not yesorno():
                        break                             
                case _:
                    print(op)
        except KeyboardInterrupt:
            print()
            break


def get_operation():
    fig = Figlet(font="small")
    print("\n", fig.renderText("Expense Tracker"))

    menu = """
    (1) Add transaction.
    (2) Per Month expenditure table.
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
                y = int(dl[0])
                m = int(dl[1])
                d = int(dl[2])
                datetime.date(y,m,d) # datetime module's constructor raises ValueError if invalid date is given. We use that to our advantage
                break

            except ValueError:
                print("Invalid date, please adhere to format (YYYY-DD-MM)")
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
        if ans == "y":
            print("Transaction recorded, returning to main menu..\n\n\n")
            curs.execute(f"INSERT INTO {tbl} values({a},'{c}','{da}','{desc}')")
            conn.commit()
            conn.close()
        else:
            print("Cancelled, returning to main menu..\n\n\n")

def view_transaction():
    while True:
        try:
            _ = input("Please enter month in format (YYYY, MM)\n: ").split(",")
            year = _[0].strip()
            month = _[1].strip()
            __ = int(year)
            if not (len(year) == 4 and len(month) == 2 and 0<int(month)<13):
                continue
            year, month = int(year), int(month)
            break
        except KeyboardInterrupt:
            sys.exit()
        except:
            continue

    curs.execute(f"select * from Expense where year(TransactionDate) = {year} and month(TransactionDate) = {month} order by Amount desc")
    t = curs.fetchall()
    
    if not t:
        print("\nNo transactions found for this month. \n")
        return
    
    table = []
    tamount = 0
    for i in t:
        a,c,d,de = i
        tamount += a
        table.append([a,c,d.strftime("%Y-%m-%d"),de])

    table.append([f"TOTAL: {tamount}", "", "", ""])
    print("\n\n")
    print(tabulate(table,headers=['Amount', 'Category', 'Date', 'Description'], tablefmt="simple" ))

def yesorno():
    while True:
        x = input("\nDo you want to return to main menu?\n: ").strip().lower()
        if x in ('yes', 'y', 'no', 'n'):
            if x == 'yes' or x == 'y':
                return True
            else:
                return False
        else:
            continue

main()