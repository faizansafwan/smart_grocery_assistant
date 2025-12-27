import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime


class GroceryAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Grocery & Billing Assistant")
        self.root.geometry("1200x780")

        # =========================
        # RULE BASED KNOWLEDGE
        # =========================

        # Alternative groups (bidirectional)
        self.alternative_groups = {
            "sugar": ["white sugar", "brown sugar"],
            "rice": ["white rice", "brown rice"],
            "bread": ["white bread", "whole wheat bread"],
            "fat": ["butter", "olive oil"],
            "drink": ["soda", "sparkling water"]
        }

        # Expanded hard-coded inventory
        self.store_inventory = [
            {"name": "white sugar", "quantity": 20, "unit": "kg", "unit_price": 350, "expiry": "2025-12-29"},
            {"name": "brown sugar", "quantity": 5, "unit": "kg", "unit_price": 380, "expiry": "2026-01-10"},
            {"name": "white rice", "quantity": 50, "unit": "kg", "unit_price": 220, "expiry": "2026-03-01"},
            {"name": "brown rice", "quantity": 10, "unit": "kg", "unit_price": 260, "expiry": "2026-02-10"},
            {"name": "white bread", "quantity": 12, "unit": "loaves", "unit_price": 150, "expiry": "2025-12-28"},
            {"name": "whole wheat bread", "quantity": 8, "unit": "loaves", "unit_price": 180, "expiry": "2025-12-30"},
            {"name": "butter", "quantity": 6, "unit": "packs", "unit_price": 550, "expiry": "2025-12-27"},
            {"name": "olive oil", "quantity": 4, "unit": "bottles", "unit_price": 1200, "expiry": "2026-05-01"},
            {"name": "soda", "quantity": 10, "unit": "bottles", "unit_price": 200, "expiry": "2026-01-05"},
            {"name": "sparkling water", "quantity": 15, "unit": "bottles", "unit_price": 220, "expiry": "2026-02-01"}
        ]

        self.create_ui()
        self.update_inventory_table()
        self.check_expiry_notifications()

    # =========================
    # UI
    # =========================

    def create_ui(self):
        title = tk.Label(
            self.root,
            text="🛒 Smart Grocery Inventory & Billing System",
            font=("Arial", 20, "bold"),
            bg="#4CAF50",
            fg="white"
        )
        title.pack(fill=tk.X)

        main = tk.Frame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left = tk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = tk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Inventory Table
        inv_frame = tk.LabelFrame(left, text="Store Inventory", font=("Arial", 12, "bold"))
        inv_frame.pack(fill=tk.BOTH, expand=True)

        self.inv_tree = ttk.Treeview(
            inv_frame,
            columns=("Item", "Qty", "Unit Price", "Expiry", "Total"),
            show="headings"
        )

        for col in ("Item", "Qty", "Unit Price", "Expiry", "Total"):
            self.inv_tree.heading(col, text=col)

        self.inv_tree.pack(fill=tk.BOTH, expand=True)

        # Billing
        bill_frame = tk.LabelFrame(left, text="Billing", font=("Arial", 12, "bold"))
        bill_frame.pack(fill=tk.X, pady=10)

        tk.Label(bill_frame, text="Item").grid(row=0, column=0)
        tk.Label(bill_frame, text="Qty").grid(row=0, column=1)
        tk.Label(bill_frame, text="Selling Price").grid(row=0, column=2)

        self.bill_item = ttk.Combobox(
            bill_frame,
            values=[i["name"] for i in self.store_inventory],
            width=25
        )
        self.bill_item.grid(row=1, column=0, padx=5)

        self.bill_qty = tk.Entry(bill_frame, width=6)
        self.bill_qty.grid(row=1, column=1)

        self.bill_price = tk.Entry(bill_frame, width=10)
        self.bill_price.grid(row=1, column=2)

        tk.Button(
            bill_frame,
            text="Add",
            command=self.add_to_bill,
            bg="#4CAF50",
            fg="white"
        ).grid(row=1, column=3, padx=5)

        # Bill List
        bill_list = tk.LabelFrame(left, text="Current Bill")
        bill_list.pack(fill=tk.BOTH, expand=True)

        self.bill_tree = ttk.Treeview(
            bill_list,
            columns=("Item", "Qty", "Price", "Total"),
            show="headings"
        )

        for col in ("Item", "Qty", "Price", "Total"):
            self.bill_tree.heading(col, text=col)

        self.bill_tree.pack(fill=tk.BOTH, expand=True)

        # Assistant Messages
        msg_frame = tk.LabelFrame(right, text="Assistant Notifications", font=("Arial", 12, "bold"))
        msg_frame.pack(fill=tk.BOTH, expand=True)

        self.messages = scrolledtext.ScrolledText(msg_frame)
        self.messages.pack(fill=tk.BOTH, expand=True)
        self.messages.config(state=tk.DISABLED)

    # =========================
    # CORE LOGIC
    # =========================

    def log(self, text, icon="ℹ️"):
        self.messages.config(state=tk.NORMAL)
        time = datetime.now().strftime("%H:%M:%S")
        self.messages.insert(tk.END, f"[{time}] {icon} {text}\n\n")
        self.messages.config(state=tk.DISABLED)
        self.messages.see(tk.END)

    def update_inventory_table(self):
        self.inv_tree.delete(*self.inv_tree.get_children())

        for item in self.store_inventory:
            total = item["quantity"] * item["unit_price"]
            self.inv_tree.insert("", tk.END, values=(
                item["name"],
                f"{item['quantity']} {item['unit']}",
                f"LKR {item['unit_price']}",
                item["expiry"],
                f"LKR {total}"
            ))

    def check_expiry_notifications(self):
        today = datetime.now()
        for item in self.store_inventory:
            expiry = datetime.strptime(item["expiry"], "%Y-%m-%d")
            days_left = (expiry - today).days
            if 0 <= days_left <= 3:
                self.log(f"'{item['name']}' expires in {days_left} day(s)!", "⚠️")

    def suggest_alternatives(self, item_name):
        for group_items in self.alternative_groups.values():
            if item_name in group_items:
                for alt in group_items:
                    if alt != item_name:
                        for inv in self.store_inventory:
                            if inv["name"] == alt and inv["quantity"] > 0:
                                self.log(f"Suggested alternative: {alt}", "💡")

    def add_to_bill(self):
        name = self.bill_item.get()

        try:
            qty = int(self.bill_qty.get())
            price = float(self.bill_price.get())
        except:
            messagebox.showerror("Error", "Invalid quantity or price")
            return

        for item in self.store_inventory:
            if item["name"] == name:
                if item["quantity"] < qty:
                    self.log(f"Insufficient stock for '{name}'", "⚠️")
                    self.suggest_alternatives(name)
                    return

                item["quantity"] -= qty
                total = qty * price

                self.bill_tree.insert("", tk.END, values=(
                    name, qty, f"LKR {price}", f"LKR {total}"
                ))

                self.log(f"Added {qty} {item['unit']} of '{name}' to bill", "✅")
                self.update_inventory_table()
                return


# =========================
# RUN
# =========================

if __name__ == "__main__":
    root = tk.Tk()
    app = GroceryAssistant(root)
    root.mainloop()
