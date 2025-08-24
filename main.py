import mysql.connector as msc
from dotenv import load_dotenv
import os
import datetime
import json
from pyfiglet import Figlet
import sys
import csv
from tabulate import tabulate
import matplotlib.pyplot as plt
import ollama

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
                case "3":
                    writetofile()
                    if not yesorno():
                        break                             
                case "5":
                    ai_chat()
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
    (2) Per month expenditure table.
    (3) Write transactions to file.
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
            categories = ["utilities", "groceries", "transportation", "dining", 
              "shopping", "entertainment", "travel", "medical", "miscellaneous"]
            print("Expenditure category?\n")
            print("Kindly choose from following categories - ", end="")
            print(", ".join(categories))
            c = input(": ").strip().lower()
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
    monthsdict = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
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
    percat = {} #Category wise amount storing dictionary
    for i in t:
        a,c,d,de = i
        tamount += a
        table.append([a,c,d.strftime("%Y-%m-%d"),de])

        if c in percat:
            percat[c] += a
        else:
            percat[c] = a

    table.append([f"TOTAL: {tamount}", "", "", ""])
    print("\n\n")
    print(tabulate(table,headers=['Amount', 'Category', 'Date', 'Description'], tablefmt="simple" ))
    print("\n\n")


    #Plotting Pie Chart:
    categories = percat.keys()
    amounts = percat.values()
    plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
    plt.title(f"Monthly Expenses for {monthsdict[month]}-{year}")
    plt.axis("equal")
    plt.show()
 
def writetofile():
    of = input("Out file name <.csv> ?\n: ").strip()
    yn = False
    while True:
        x = input(f"\nAll records will be written to {of}.csv [y/n]\n: ").strip().lower()
        if x in ('yes', 'y', 'no', 'n'):
            if x == 'yes' or x == 'y':
                yn = True
                break
            else:
                break
        else:
            continue
    curs.execute(f"select * from {tbl}")
    data = curs.fetchall()
    if yn:
        with open(f"../{of}.csv", "w") as recordsfile:
            wr = csv.writer(recordsfile)
            for d in data:
                wr.writerow(d)
        print(f"\n\nData written to {of}.csv")

def ai_definition():
    curs.execute(f"select * from {tbl}")
    d = curs.fetchall()
    data = []
    for _ in d:
        l = list(_)
        l[2] = l[2].strftime("%Y-%m-%d")
        data.append(l)
    finaldata = json.dumps(data, indent=2)

    system = f"""
    You are FinAssist, an AI specialized ONLY in personal finance and expense tracking. 
    Your job is to analyze the user's financial records and assist them with:
    - Tracking daily, weekly, and monthly expenses
    - Categorizing spending
    - Budgeting advice
    - Saving strategies
    - Detecting unusual spending patterns

    Rules:
    1. NEVER answer questions outside finance. If asked, politely redirect back to financial topics.
    2. ALWAYS use the provided expense data when relevant.
    3. KEEP responses short, clear, and practical.
    4. When possible, give actionable insights (e.g., "You spent ₹X on food last month, which is Y% of total").

    Here is the user's expense history:
    {finaldata}
    """
    return system

def ai_chat():
    sysprompt = ai_definition()
    messages = [
        {"role": "system", "content": sysprompt}
    ]

    while True:
        inp = input("\n>>> ")
        if inp.lower().strip() in ['exit', 'quit']:
            break

        messages.append({"role": "user", "content": inp})

        stream = ollama.chat(
            model="phi3:mini",
            messages=messages,
            stream=True
        )

        full_response = ""
        for chunk in stream:
            content = chunk["message"]["content"]
            print(content, end="", flush=True)
            full_response += content

        messages.append({"role": "assistant", "content": full_response})
        print()  # clean newline



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