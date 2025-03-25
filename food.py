import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox, ttk

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('food_orders.db')
cursor = conn.cursor()

# Create a table for food orders
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    food_item TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL
)
''')
conn.commit()

# Function to create an order
def create_order():
    customer_name = entry_customer_name.get()
    food_item = entry_food_item.get()
    quantity = int(entry_quantity.get())
    price = float(entry_price.get())
    
    cursor.execute('INSERT INTO orders (customer_name, food_item, quantity, price) VALUES (?, ?, ?, ?)', 
                   (customer_name, food_item, quantity, price))
    conn.commit()
    messagebox.showinfo("Success", "Order created successfully.")
    clear_entries()

# Function to read orders and display in the treeview
def read_orders():
    for row in tree.get_children():
        tree.delete(row)
    df = pd.read_sql_query('SELECT * FROM orders', conn)
    for index, row in df.iterrows():
        tree.insert("", "end", values=(row['id'], row['customer_name'], row['food_item'], row['quantity'], row['price']))

# Function to update an order
def update_order():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Select an order to update.")
        return
    
    order_id = tree.item(selected_item)['values'][0]
    customer_name = entry_customer_name.get()
    food_item = entry_food_item.get()
    quantity = int(entry_quantity.get())
    price = float(entry_price.get())
    
    cursor.execute('UPDATE orders SET customer_name=?, food_item=?, quantity=?, price=? WHERE id=?', 
                   (customer_name, food_item, quantity, price, order_id))
    conn.commit()
    messagebox.showinfo("Success", "Order updated successfully.")
    clear_entries()
    read_orders()

# Function to delete an order
def delete_order():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("Warning", "Select an order to delete.")
        return
    
    order_id = tree.item(selected_item)['values'][0]
    cursor.execute('DELETE FROM orders WHERE id=?', (order_id,))
    conn.commit()
    messagebox.showinfo("Success", "Order deleted successfully.")
    read_orders()

# Function to analyze orders
def analyze_orders():
    df = pd.read_sql_query('SELECT * FROM orders', conn)
    total_orders = len(df)
    total_revenue = df['price'].sum()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    messagebox.showinfo("Analysis", f"Total Orders: {total_orders}\nTotal Revenue: ${total_revenue:.2f}\nAverage Order Value: ${avg_order_value:.2f}")

# Function to visualize orders
def visualize_orders():
    df = pd.read_sql_query('SELECT food_item, SUM(quantity) as total_quantity FROM orders GROUP BY food_item', conn)
    
    if not df.empty:
        plt.figure(figsize=(10, 6))
        plt.bar(df['food_item'], df['total_quantity'], color='skyblue')
        plt.title('Total Quantity Ordered by Food Item')
        plt.xlabel('Food Item')
        plt.ylabel('Total Quantity')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        messagebox.showwarning("Warning", "No orders to visualize.")

# Function to clear entry fields
def clear_entries():
    entry_customer_name.delete(0, tk.END)
    entry_food_item.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)
    entry_price.delete(0, tk.END)

# Create the main window
root = tk.Tk()
root.title("Food Ordering Application")

# Create input fields
tk.Label(root, text="Customer Name").grid(row=0, column=0)
entry_customer_name = tk.Entry(root)
entry_customer_name.grid(row=0, column=1)

tk.Label(root, text="Food Item").grid(row=1, column=0)
entry_food_item = tk.Entry(root)
entry_food_item.grid(row=1, column=1)

tk.Label(root, text="Quantity").grid(row=2, column=0)
entry_quantity = tk.Entry(root)
entry_quantity.grid(row=2, column=1)

tk.Label(root, text="Price").grid(row=3, column=0)
entry_price = tk.Entry(root)
entry_price.grid(row=3, column=1)

# Create buttons
tk.Button(root, text="Create Order", command=create_order).grid(row=4, column=0)
tk.Button(root, text="Read Orders", command=read_orders).grid(row=4, column=1)
tk.Button(root, text="Update Order", command=update_order).grid(row=5, column=0)
tk.Button(root, text="Delete Order", command=delete_order).grid(row=5, column=1)
tk.Button(root, text="Analyze Orders", command=analyze_orders).grid(row=6, column=0)
tk.Button(root, text="Visualize Orders", command=visualize_orders).grid(row=6, column=1)

# Create a treeview to display orders
tree = ttk.Treeview(root, columns=("ID", "Customer Name", "Food Item", "Quantity", "Price"), show='headings')
tree.heading("ID", text="ID")
tree.heading("Customer Name", text="Customer Name")
tree.heading("Food Item", text="Food Item")
tree.heading("Quantity", text="Quantity")
tree.heading("Price", text="Price")
tree.grid(row=7, column=0, columnspan=2)

# Start the GUI event loop
root.mainloop()

# Close the database connection
conn.close()