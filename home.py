import mysql.connector
import bcrypt
import getpass
import numpy as np
import re
from datetime import datetime

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="Bank_SBI"
)
cursor = conn.cursor()


def validate_password(password):
    return re.fullmatch(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,20}$', password)


class Bank:
    def customer_signup(self):
        username = input("Enter Your Name: ")
        cursor.execute("SELECT * FROM Customer_details WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            print("You already have an account.")
            return username

        while True:
            password = input("Enter your password: ")
            if validate_password(password):
                break
            print("Password must be 8–20 chars, with upper/lowercase, digit & special char.")

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        contact = input("Enter contact number: ")
        address = input("Enter address: ")
        account_no = ''.join(str(d) for d in np.random.randint(0, 10, 10))
        IFSC_code = "SBI123"
        balance = 0

        cursor.execute(
            "INSERT INTO Customer_details (username, password, contact, address, account_no, IFSC_code, balance) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (username, hashed_password, contact, address, account_no, IFSC_code, balance)
        )
        conn.commit()
        print(f"Account created successfully for {username}!\n")
        return username

    def login(self):
        username = input("Enter your username: ")
        cursor.execute("SELECT password FROM Customer_details WHERE username = %s", (username,))
        record = cursor.fetchone()
        if not record:
            print("User not found.")
            return None

        password = input("Enter your password: ")

        if bcrypt.checkpw(password.encode('utf-8'), record[0].encode() if isinstance(record[0], str) else record[0]):
            print("Login successful.")
            return username
        else:
            print("Incorrect password.")
            return None

    def deposit(self, username):
        try:
            amount = float(input("Enter amount to deposit: Rs."))
            cursor.execute("UPDATE Customer_details SET balance = balance + %s WHERE username = %s", (amount, username))
            cursor.execute(
                "INSERT INTO Transaction_History (username, transaction_type, amount) VALUES (%s, 'deposit', %s)",
                (username, amount))
            conn.commit()
            print(f"Rs.{amount} deposited successfully.")
        except ValueError:
            print("Invalid amount.")

    def withdraw(self, username):
        try:
            amount = float(input("Enter amount to withdraw: Rs."))
            cursor.execute("SELECT balance FROM Customer_details WHERE username = %s", (username,))
            bal = cursor.fetchone()[0]
            if amount > bal:
                print("Insufficient balance.")
                return
            cursor.execute("UPDATE Customer_details SET balance = balance - %s WHERE username = %s", (amount, username))
            cursor.execute(
                "INSERT INTO Transaction_History (username, transaction_type, amount) VALUES (%s, 'withdraw', %s)",
                (username, amount))
            conn.commit()
            print(f"Rs.{amount} withdrawn successfully.")
        except ValueError:
            print("Invalid amount.")

    def show_transaction_history(self, username):
        cursor.execute(
            "SELECT transaction_type, amount, timestamp FROM Transaction_History WHERE username = %s ORDER BY timestamp DESC",
            (username,))
        records = cursor.fetchall()
        if not records:
            print("No transaction history found.")
            return
        print(f"\n--- Transaction History for {username} ---")
        for tr_type, amount, time in records:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {tr_type.capitalize():<8} | Rs.{amount}")

    def show_balance(self, username):
        cursor.execute("SELECT balance FROM Customer_details WHERE username = %s", (username,))
        balance = cursor.fetchone()[0]
        print(f"Current Balance: Rs.{balance:.2f}")


# --- Menu ---
def main():
    bank = Bank()
    print("==== Welcome to SBI Bank ====")
    while True:
        print("\n1. Signup")
        print("\n2. Login")
        print("\n3. Exit")
        choice = input("Choose option: ")
        if choice == '1':
            username = bank.customer_signup()
            menu(bank, username)
        elif choice == '2':
            username = bank.login()
            if username:
                menu(bank, username)
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")


def menu(bank, username):
    while True:
        print("\n1. Deposit\n2. Withdraw\n3. Show Balance\n4. Transaction History\n5. Logout")
        ch = input("Select: ")
        if ch == '1':
            bank.deposit(username)
        elif ch == '2':
            bank.withdraw(username)
        elif ch == '3':
            bank.show_balance(username)
        elif ch == '4':
            bank.show_transaction_history(username)
        elif ch == '5':
            print("Logged out.")
            break
        else:
            print("Invalid choice.")
main()