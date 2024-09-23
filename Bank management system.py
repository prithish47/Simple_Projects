import mysql.connector
from tkinter import Tk, ttk, Label, Button, simpledialog, messagebox, Toplevel, Listbox
import requests
from PIL import Image, ImageTk

# Initialize cursor globally
connection = None
cursor = None

def create_connection():
    global connection, cursor
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="bank"
    )
    cursor = connection.cursor()

def close_connection():
    global connection, cursor
    if cursor:
        cursor.close()
    if connection:
        connection.close()

def init_database():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS customers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255),
        password VARCHAR(255),
        dob DATE,
        balance DECIMAL(10, 2) DEFAULT 0.0
    )
    """
    execute_query(create_table_query)

    create_transaction_table_query = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255),
        transaction_type VARCHAR(20),
        amount DECIMAL(10, 2),
        transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    execute_query(create_transaction_table_query)

    create_bank_workers_table_query = """
    CREATE TABLE IF NOT EXISTS bank_workers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255),
        password VARCHAR(255)
    )
    """
    execute_query(create_bank_workers_table_query)

def execute_query(query, values=None):
    global cursor
    try:
        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)

        if query.lower().startswith("select"):
            result = cursor.fetchall()
        else:
            result = None

        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e

    return result

def get_transaction_history(username):
    query = "SELECT * FROM transactions WHERE username = %s"
    values = (username,)
    return execute_query(query, values)

def update_balance(amount, username):
    query = "UPDATE customers SET balance = balance + %s WHERE username = %s"
    values = (amount, username)
    execute_query(query, values)

def check_sufficient_balance(amount, username):
    current_balance = get_balance(username)
    return current_balance is not None and current_balance >= amount

def get_balance(username):
    query = "SELECT balance FROM customers WHERE username = %s"
    values = (username,)
    result = execute_query(query, values)
    return result[0][0] if result else None

def record_transaction(transaction_type, amount, username):
    query = "INSERT INTO transactions (username, transaction_type, amount) VALUES (%s, %s, %s)"
    values = (username, transaction_type, amount)
    execute_query(query, values)

def get_dob(username):
    query = "SELECT dob FROM customers WHERE username = %s"
    values = (username,)
    result = execute_query(query, values)
    return result[0][0] if result else None

def get_all_customers():
    query = "SELECT * FROM customers"
    return execute_query(query)

def create_new_customer(username, password, dob):
    try:
      
        cursor.execute("SELECT * FROM customers WHERE username = %s", (username,))
        existing_customer = cursor.fetchone()

        if existing_customer:
            return "Username already exists. Please choose a different one."

        username = username.capitalize()

        cursor.execute("INSERT INTO customers (username, password, dob) VALUES (%s, %s, %s)", (username, password, dob))
        connection.commit()

        return "New customer created successfully."

    except Exception as e:
        connection.rollback()
        return f"Error creating new customer: {str(e)}"

def authenticate_user(username, password):
    try:
        cursor.execute("SELECT * FROM customers WHERE username = %s AND password = %s", (username, password))
        authenticated_user = cursor.fetchone()

        if authenticated_user:
            return True
        else:
            return False

    except Exception as e:
        return f"Error authenticating user: {str(e)}"

def authenticate_admin(username, password):
    admin_username = "admin"
    admin_password = "1234"  

    if username == admin_username and password == admin_password:
        return True
    else:
        return False

def authenticate_bank_worker(username, password):
    try:
        
        cursor.execute("SELECT * FROM bank_workers WHERE username = %s AND password = %s", (username, password))
        authenticated_worker = cursor.fetchone()

        if authenticated_worker:
            return True
        else:
            return False

    except Exception as e:
        return f"Error authenticating bank worker: {str(e)}"

class BankManagementSystem:
    def __init__(self, master):
        self.master = master
        self.master.title("Bank Management System")
        self.master.geometry("1440x900")  

        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12))

        self.title_label = Label(self.master, text="Bank Management System", font=("Helvetica", 20, "bold"))
        self.title_label.pack(pady=10)

        image_url = "https://i0.wp.com/www.iedunote.com/img/1087/bank-management.jpg?fit=1080%2C630&quality=100&ssl=1"
        image = Image.open(requests.get(image_url, stream=True).raw)
        photo = ImageTk.PhotoImage(image)
        image_label = Label(self.master, image=photo)
        image_label.image = photo  
        image_label.pack()

        self.login_frame = ttk.Frame(self.master)
        self.login_frame.pack(pady=20)

        self.customer_login_button = Button(self.login_frame, text="Customer Login", command=self.open_customer_page)
        self.customer_login_button.pack(side="left", padx=10)

        self.bank_worker_login_button = Button(self.login_frame, text="Bank Worker's Login", command=self.open_bank_worker_page)
        self.bank_worker_login_button.pack(side="left", padx=10)

        self.admin_login_button = Button(self.login_frame, text="Admin Login", command=self.open_admin_page)
        self.admin_login_button.pack(side="left", padx=10)

        self.new_customer_button = Button(self.master, text="New Customer", command=self.create_new_customer)
        self.new_customer_button.pack()

        self.footer_label = Label(self.master, text="© 2023 Bank Management System. All rights reserved.", font=("Helvetica", 10))
        self.footer_label.pack(side="bottom", pady=10)

    def open_customer_page(self):
        username = simpledialog.askstring("Customer Login", "Enter your username:")
        password = simpledialog.askstring("Customer Login", "Enter your password:")

        if authenticate_user(username, password):
            self.master.destroy()
            customer_page = CustomerPage(username)
            customer_page.show_page()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials. Please try again.")

    def open_bank_worker_page(self):
        username = simpledialog.askstring("Bank Worker's Login", "Enter your username:")
        password = simpledialog.askstring("Bank Worker's Login", "Enter your password:")

        if authenticate_bank_worker(username, password):
            self.master.destroy()
            bank_worker_page = BankWorkerPage()
            bank_worker_page.show_page()
        else:
            messagebox.showerror("Login Failed", "Invalid bank worker credentials. Please try again.")

    def open_admin_page(self):
        username = simpledialog.askstring("Admin Login", "Enter your username:")
        password = simpledialog.askstring("Admin Login", "Enter your password:")

        if authenticate_admin(username, password):
            self.master.destroy()
            admin_page = AdminPage()
            admin_page.show_page()
        else:
            messagebox.showerror("Login Failed", "Invalid admin credentials. Please try again.")

    def create_new_customer(self):
        username = simpledialog.askstring("New Customer", "Enter the username:")
        password = simpledialog.askstring("New Customer", "Enter the password:")
        if password:
            dob = simpledialog.askstring("New Customer", "Enter the date of birth (yyyy-mm-dd):")

            result = create_new_customer(username, password, dob)
            messagebox.showinfo("New Customer", result)

class CustomerPage:
    def __init__(self, username):
        self.username = username
        self.root = Tk()
        self.root.title("Customer Page")
        self.root.geometry("800x600")

        self.label = Label(self.root, text=f"Welcome, {username}!", font=("Helvetica", 16, "bold"))
        self.label.pack(pady=20)

        self.deposit_button = Button(self.root, text="Deposit", command=self.deposit)
        self.deposit_button.pack()

        self.withdraw_button = Button(self.root, text="Withdraw", command=self.withdraw)
        self.withdraw_button.pack()

        self.balance_button = Button(self.root, text="Check Balance", command=self.check_balance)
        self.balance_button.pack()

        self.transaction_history_button = Button(self.root, text="Transaction History", command=self.show_transaction_history)
        self.transaction_history_button.pack()

        self.account_info_button = Button(self.root, text="Account Info", command=self.show_account_info)
        self.account_info_button.pack()

        self.close_account_button = Button(self.root, text="Close Account", command=self.close_account)
        self.close_account_button.pack()

    def deposit(self):
        amount = simpledialog.askfloat("Deposit", "Enter the deposit amount:")
        if amount is not None:
            update_balance(amount, self.username)
            record_transaction("Deposit", amount, self.username)
            messagebox.showinfo("Deposit", f"Deposit of {amount} successful.")
            self.show_page()

    def withdraw(self):
        amount = simpledialog.askfloat("Withdraw", "Enter the withdrawal amount:")
        if amount is not None:
            if check_sufficient_balance(amount, self.username):
                update_balance(-amount, self.username)
                record_transaction("Withdrawal", amount, self.username)
                messagebox.showinfo("Withdraw", f"Withdrawal of {amount} successful.")
                self.show_page()
            else:
                messagebox.showerror("Withdraw", "Insufficient balance.")

    def check_balance(self):
        balance = get_balance(self.username)
        if balance is not None:
            messagebox.showinfo("Balance", f"Your current balance is: {balance}")
        else:
            messagebox.showerror("Balance", "Error fetching balance.")

    def show_transaction_history(self):
        transactions = get_transaction_history(self.username)

        if transactions:
        
            history_window = Toplevel(self.root)
            history_window.title("Transaction History")
            history_window.geometry("600x400")

          
            transaction_listbox = Listbox(history_window, width=50, height=15)
            transaction_listbox.pack(pady=10)

           
            transaction_listbox.insert(0, "Transaction Type     Amount     Date")

         
            for trans in transactions:
                trans_str = f"{trans[2]:<20} {trans[3]:<10} {trans[4]}"
                transaction_listbox.insert("end", trans_str)
        else:
            messagebox.showinfo("Transaction History", "No transactions found.")

    def show_account_info(self):
        balance = get_balance(self.username)
        dob = get_dob(self.username)
        messagebox.showinfo("Account Info", f"Username: {self.username}\nBalance: {balance}\nDate of Birth: {dob}")

    def close_account(self):
        confirm = messagebox.askyesno("Close Account", "Are you sure you want to close your account?")
        if confirm:
            delete_customer(self.username)
            messagebox.showinfo("Close Account", "Account closed successfully.")
            self.root.destroy()

    def show_page(self):
        self.root.mainloop()

class BankWorkerPage:
    def __init__(self):
        self.root = Tk()
        self.root.title("Bank Worker's Page")
        self.root.geometry("800x600")

        self.label = Label(self.root, text="Bank Worker's Page", font=("Helvetica", 16, "bold"))
        self.label.pack(pady=20)

        self.modify_customer_button = Button(self.root, text="Modify Customer", command=self.modify_customer)
        self.modify_customer_button.pack()

        self.display_customers_button = Button(self.root, text="Display All Customers", command=self.display_customers)
        self.display_customers_button.pack()

    def modify_customer(self):
        customer_username = simpledialog.askstring("Modify Customer", "Enter the customer's username:")

        if customer_username:
            
            cursor.execute("SELECT * FROM customers WHERE username = %s", (customer_username,))
            existing_customer = cursor.fetchone()

            if existing_customer:
                
                modify_dialog = Toplevel(self.root)
                modify_dialog.title("Modify Customer")
                modify_dialog.geometry("400x300")

                Label(modify_dialog, text=f"Current Details for {customer_username}", font=("Helvetica", 14)).pack(pady=10)

               
                Label(modify_dialog, text=f"Username: {existing_customer[1]}").pack()
                Label(modify_dialog, text=f"Password: {existing_customer[2]}").pack()
                Label(modify_dialog, text=f"Date of Birth: {existing_customer[3]}").pack()
                Label(modify_dialog, text=f"Balance: {existing_customer[4]}").pack()

                
                def modify_detail(detail_type):
                    new_value = simpledialog.askstring(f"Modify {detail_type}", f"Enter the new {detail_type.lower()}:")
                    if new_value:
                        cursor.execute(f"UPDATE customers SET {detail_type.lower()} = %s WHERE username = %s", (new_value, customer_username))
                        connection.commit()
                        messagebox.showinfo("Modify Customer", f"{detail_type} updated successfully.")
                        modify_dialog.destroy()

                Button(modify_dialog, text="Modify Password", command=lambda: modify_detail("Password")).pack(pady=5)
                Button(modify_dialog, text="Modify Date of Birth", command=lambda: modify_detail("DOB")).pack(pady=5)

            else:
                messagebox.showerror("Modify Customer", "Customer not found.")

    def display_customers(self):
        customers = get_all_customers()
        if customers:
            
            customers_window = Toplevel(self.root)
            customers_window.title("All Customers")
            customers_window.geometry("600x400")

           
            customer_listbox = Listbox(customers_window, width=50, height=15)
            customer_listbox.pack(pady=10)

            
            customer_listbox.insert(0, "Username     Balance")

           
            for customer in customers:
                customer_str = f"{customer[1]:<15} {customer[4]:<10}"
                customer_listbox.insert("end", customer_str)
        else:
            messagebox.showinfo("All Customers", "No customers found.")

    def show_page(self):
        self.root.mainloop()

class AdminPage:
    def __init__(self):
        self.root = Tk()
        self.root.title("Admin Page")
        self.root.geometry("400x300")

        self.label = Label(self.root, text="Admin Page", font=("Helvetica", 16, "bold"))
        self.label.pack(pady=20)

        self.create_worker_button = Button(self.root, text="Create Bank Worker", command=self.create_bank_worker)
        self.create_worker_button.pack()

    def create_bank_worker(self):
        worker_username = simpledialog.askstring("Create Bank Worker", "Enter the new worker's username:")
        worker_password = simpledialog.askstring("Create Bank Worker", "Enter the new worker's password:")

        
        create_new_bank_worker(worker_username, worker_password)

        messagebox.showinfo("Create Bank Worker", "Bank worker created successfully.")

    def show_page(self):
        self.root.mainloop()

def create_new_bank_worker(username, password):
    try:
     
        cursor.execute("SELECT * FROM bank_workers WHERE username = %s", (username,))
        existing_worker = cursor.fetchone()

        if existing_worker:
            return "Username already exists. Please choose a different one."

        username = username.capitalize()
        cursor.execute("INSERT INTO bank_workers (username, password) VALUES (%s, %s)", (username, password))
        connection.commit()

        return "New bank worker created successfully."

    except Exception as e:
        connection.rollback()
        return f"Error creating new bank worker: {str(e)}"
def main():
    create_connection()
    init_database()

    root = Tk()

    try:
        # Set window size to user's screen resolution
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"{screen_width}x{screen_height}")

        bank_system = BankManagementSystem(root)
        root.mainloop()
    finally:
        close_connection()


if __name__ == "__main__":
    main()
    close_connection()
