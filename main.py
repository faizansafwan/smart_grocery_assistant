import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
import json
import os


class GroceryAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Grocery Shopping Assistant")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")

        # Data storage
        self.grocery_list = []
        self.purchase_history = []
        self.inventory = []

        # Healthy alternatives database
        self.healthy_alternatives = {
            "white bread": "whole wheat bread",
            "white rice": "brown rice",
            "sugar": "honey or stevia",
            "butter": "olive oil",
            "whole milk": "skim milk",
            "soda": "sparkling water",
            "chips": "nuts or fruit",
            "ice cream": "frozen yogurt",
            "pasta": "whole grain pasta",
            "mayo": "greek yogurt"
        }

        # Item categories with typical shelf life (in days)
        self.shelf_life = {
            "milk": 7,
            "bread": 5,
            "eggs": 21,
            "yogurt": 14,
            "cheese": 14,
            "chicken": 2,
            "fish": 2,
            "beef": 3,
            "lettuce": 5,
            "tomatoes": 7,
            "bananas": 5,
            "apples": 14,
            "carrots": 21,
            "butter": 30,
            "juice": 7
        }

        self.load_data()
        self.create_ui()
        self.check_suggestions()

    def create_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#4CAF50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text="🛒 Smart Grocery Shopping Assistant",
                               font=("Arial", 20, "bold"), bg="#4CAF50", fg="white")
        title_label.pack(pady=15)

        # Main container
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left panel - Input and Lists
        left_panel = tk.Frame(main_frame, bg="white", relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Add Item Section
        add_frame = tk.LabelFrame(left_panel, text="Add Item", font=("Arial", 12, "bold"),
                                  bg="white", padx=10, pady=10)
        add_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(add_frame, text="Item Name:", bg="white", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W,
                                                                                    pady=5)
        self.item_entry = tk.Entry(add_frame, width=25, font=("Arial", 10))
        self.item_entry.grid(row=0, column=1, pady=5, padx=5)

        tk.Label(add_frame, text="Quantity:", bg="white", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.quantity_entry = tk.Entry(add_frame, width=25, font=("Arial", 10))
        self.quantity_entry.grid(row=1, column=1, pady=5, padx=5)
        self.quantity_entry.insert(0, "1")

        btn_frame = tk.Frame(add_frame, bg="white")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(btn_frame, text="Add to List", command=self.add_to_grocery_list,
                  bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                  padx=10, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Mark as Purchased", command=self.mark_as_purchased,
                  bg="#2196F3", fg="white", font=("Arial", 10, "bold"),
                  padx=10, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)

        # Grocery List Section
        list_frame = tk.LabelFrame(left_panel, text="Current Grocery List",
                                   font=("Arial", 12, "bold"), bg="white", padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create Treeview for grocery list
        self.list_tree = ttk.Treeview(list_frame, columns=("Item", "Quantity"),
                                      show="headings", height=8)
        self.list_tree.heading("Item", text="Item")
        self.list_tree.heading("Quantity", text="Quantity")
        self.list_tree.column("Item", width=200)
        self.list_tree.column("Quantity", width=100)

        list_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.list_tree.yview)
        self.list_tree.configure(yscrollcommand=list_scroll.set)

        self.list_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(left_panel, text="Remove Selected", command=self.remove_from_list,
                  bg="#f44336", fg="white", font=("Arial", 10, "bold"),
                  padx=10, pady=5, cursor="hand2").pack(pady=5)

        # Right panel - Assistant Messages and Inventory
        right_panel = tk.Frame(main_frame, bg="white", relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Assistant Messages
        msg_frame = tk.LabelFrame(right_panel, text="Assistant Suggestions",
                                  font=("Arial", 12, "bold"), bg="white", padx=10, pady=10)
        msg_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.message_box = scrolledtext.ScrolledText(msg_frame, wrap=tk.WORD,
                                                     font=("Arial", 10), height=15,
                                                     bg="#f9f9f9", relief=tk.SUNKEN, bd=2)
        self.message_box.pack(fill=tk.BOTH, expand=True)
        self.message_box.config(state=tk.DISABLED)

        # Inventory Section
        inv_frame = tk.LabelFrame(right_panel, text="Current Inventory (Expiring Soon)",
                                  font=("Arial", 12, "bold"), bg="white", padx=10, pady=10)
        inv_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.inv_tree = ttk.Treeview(inv_frame, columns=("Item", "Expires", "Days Left"),
                                     show="headings", height=6)
        self.inv_tree.heading("Item", text="Item")
        self.inv_tree.heading("Expires", text="Expires On")
        self.inv_tree.heading("Days Left", text="Days Left")
        self.inv_tree.column("Item", width=120)
        self.inv_tree.column("Expires", width=100)
        self.inv_tree.column("Days Left", width=80)

        inv_scroll = ttk.Scrollbar(inv_frame, orient=tk.VERTICAL, command=self.inv_tree.yview)
        self.inv_tree.configure(yscrollcommand=inv_scroll.set)

        self.inv_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        inv_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Bottom buttons
        bottom_frame = tk.Frame(right_panel, bg="white")
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(bottom_frame, text="Check Suggestions", command=self.check_suggestions,
                  bg="#FF9800", fg="white", font=("Arial", 10, "bold"),
                  padx=10, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)

        tk.Button(bottom_frame, text="Clear Messages", command=self.clear_messages,
                  bg="#9E9E9E", fg="white", font=("Arial", 10, "bold"),
                  padx=10, pady=5, cursor="hand2").pack(side=tk.LEFT, padx=5)

        self.update_displays()

    def add_message(self, message, msg_type="info"):
        self.message_box.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")

        if msg_type == "warning":
            prefix = "⚠️ "
        elif msg_type == "success":
            prefix = "✅ "
        elif msg_type == "suggestion":
            prefix = "💡 "
        else:
            prefix = "ℹ️ "

        self.message_box.insert(tk.END, f"[{timestamp}] {prefix}{message}\n\n")
        self.message_box.see(tk.END)
        self.message_box.config(state=tk.DISABLED)

    def clear_messages(self):
        self.message_box.config(state=tk.NORMAL)
        self.message_box.delete(1.0, tk.END)
        self.message_box.config(state=tk.DISABLED)

    def add_to_grocery_list(self):
        item_name = self.item_entry.get().strip().lower()
        quantity = self.quantity_entry.get().strip()

        if not item_name:
            messagebox.showwarning("Input Error", "Please enter an item name")
            return

        # Check for healthy alternative
        if item_name in self.healthy_alternatives:
            alternative = self.healthy_alternatives[item_name]
            self.add_message(f"Healthier Alternative: Instead of '{item_name}', "
                             f"consider '{alternative}' for better nutrition!", "suggestion")

        # Check if item already in list
        for item in self.grocery_list:
            if item['name'] == item_name:
                messagebox.showinfo("Duplicate", f"'{item_name}' is already in your list")
                return

        self.grocery_list.append({'name': item_name, 'quantity': quantity})
        self.add_message(f"Added '{item_name}' (x{quantity}) to your grocery list", "success")

        self.item_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, "1")

        self.update_displays()
        self.save_data()

    def mark_as_purchased(self):
        item_name = self.item_entry.get().strip().lower()

        if not item_name:
            messagebox.showwarning("Input Error", "Please enter an item name")
            return

        # Add to inventory with expiration date
        purchase_date = datetime.now()
        days = self.shelf_life.get(item_name, 7)  # Default 7 days if not in database
        expiry_date = purchase_date + timedelta(days=days)

        self.inventory.append({
            'name': item_name,
            'purchase_date': purchase_date.strftime("%Y-%m-%d"),
            'expiry_date': expiry_date.strftime("%Y-%m-%d"),
            'days_left': days
        })

        # Add to purchase history
        self.purchase_history.append({
            'name': item_name,
            'date': purchase_date.strftime("%Y-%m-%d")
        })

        # Remove from grocery list if present
        self.grocery_list = [item for item in self.grocery_list if item['name'] != item_name]

        self.add_message(f"Marked '{item_name}' as purchased. It will expire in {days} days.", "success")

        self.item_entry.delete(0, tk.END)
        self.update_displays()
        self.save_data()

    def remove_from_list(self):
        selected = self.list_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an item to remove")
            return

        item = self.list_tree.item(selected[0])
        item_name = item['values'][0]

        self.grocery_list = [item for item in self.grocery_list if item['name'] != item_name]
        self.add_message(f"Removed '{item_name}' from grocery list", "info")

        self.update_displays()
        self.save_data()

    def check_suggestions(self):
        # Rule-based suggestions based on purchase history
        current_date = datetime.now()

        # Check for recurring items (bought more than once in last 30 days)
        item_frequency = {}
        for purchase in self.purchase_history:
            purchase_date = datetime.strptime(purchase['date'], "%Y-%m-%d")
            days_ago = (current_date - purchase_date).days

            if days_ago <= 30:
                item_name = purchase['name']
                item_frequency[item_name] = item_frequency.get(item_name, 0) + 1

        # Suggest items bought regularly
        for item, count in item_frequency.items():
            if count >= 2 and item not in [g['name'] for g in self.grocery_list]:
                last_purchase = max([datetime.strptime(p['date'], "%Y-%m-%d")
                                     for p in self.purchase_history if p['name'] == item])
                days_since = (current_date - last_purchase).days

                if days_since >= 5:
                    self.add_message(f"You bought '{item}' {days_since} days ago. "
                                     f"Should I add it to your list?", "suggestion")

        # Check for expiring items
        self.check_expiring_items()

    def check_expiring_items(self):
        current_date = datetime.now()
        expiring_soon = []

        for item in self.inventory:
            expiry_date = datetime.strptime(item['expiry_date'], "%Y-%m-%d")
            days_left = (expiry_date - current_date).days
            item['days_left'] = days_left

            if days_left <= 3 and days_left >= 0:
                expiring_soon.append(item)
                self.add_message(f"Warning: '{item['name']}' expires in {days_left} day(s)!", "warning")
            elif days_left < 0:
                self.add_message(f"'{item['name']}' has expired! Consider removing it.", "warning")

        # Remove expired items from inventory
        self.inventory = [item for item in self.inventory if item['days_left'] >= -1]

    def update_displays(self):
        # Update grocery list
        for item in self.list_tree.get_children():
            self.list_tree.delete(item)

        for item in self.grocery_list:
            self.list_tree.insert("", tk.END, values=(item['name'], item['quantity']))

        # Update inventory (show items expiring within 7 days)
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)

        current_date = datetime.now()
        for item in self.inventory:
            expiry_date = datetime.strptime(item['expiry_date'], "%Y-%m-%d")
            days_left = (expiry_date - current_date).days

            if days_left <= 7:
                self.inv_tree.insert("", tk.END, values=(
                    item['name'],
                    item['expiry_date'],
                    f"{days_left} days"
                ))

    def save_data(self):
        data = {
            'grocery_list': self.grocery_list,
            'purchase_history': self.purchase_history,
            'inventory': self.inventory
        }

        with open('grocery_data.json', 'w') as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        if os.path.exists('grocery_data.json'):
            try:
                with open('grocery_data.json', 'r') as f:
                    data = json.load(f)
                    self.grocery_list = data.get('grocery_list', [])
                    self.purchase_history = data.get('purchase_history', [])
                    self.inventory = data.get('inventory', [])
            except:
                pass


if __name__ == "__main__":
    root = tk.Tk()
    app = GroceryAssistant(root)
    root.mainloop()