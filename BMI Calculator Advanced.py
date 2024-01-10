import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt

class BMICalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("BMI Calculator")

        self.weight_var = tk.DoubleVar()
        self.height_var = tk.DoubleVar()

        self.create_gui()

        # Database
        self.conn = sqlite3.connect("bmi_history.db")
        self.create_table()

    def create_table(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bmi_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    weight REAL,
                    height REAL,
                    bmi REAL,
                    category TEXT,
                    timestamp TEXT
                )
            """)

    def calculate_bmi(self):
        weight = self.weight_var.get()
        height = self.height_var.get()

        if 10 < weight < 500 and 0.5 < height < 3:
            bmi = weight / (height ** 2)
            category = self.categorize_bmi(bmi)
            self.save_to_database(weight, height, bmi, category)

            result_text = f"BMI: {bmi:.2f} ({category})"
            self.result_label.config(text=result_text)

        else:
            messagebox.showerror("Input Error", "Invalid weight or height values. Please check your inputs.")

    def categorize_bmi(self, bmi):
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 24.9:
            return "Normal Weight"
        elif 25 <= bmi < 29.9:
            return "Overweight"
        else:
            return "Obese"

    def save_to_database(self, weight, height, bmi, category):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO bmi_history (weight, height, bmi, category, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (weight, height, bmi, category, timestamp))

    def view_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("BMI History")

        tree = ttk.Treeview(history_window)
        tree["columns"] = ("ID", "Weight", "Height", "BMI", "Category", "Timestamp")
        tree.heading("#0", text="ID")
        tree.heading("ID", text="ID")
        tree.heading("Weight", text="Weight")
        tree.heading("Height", text="Height")
        tree.heading("BMI", text="BMI")
        tree.heading("Category", text="Category")
        tree.heading("Timestamp", text="Timestamp")

        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM bmi_history")
            rows = cursor.fetchall()

            for row in rows:
                tree.insert("", "end", values=row)

        tree.pack()

    def plot_history(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT timestamp, bmi FROM bmi_history")
            rows = cursor.fetchall()

        timestamps = [row[0] for row in rows]
        bmis = [row[1] for row in rows]

        plt.plot(timestamps, bmis, marker='o')
        plt.xlabel("Timestamp")
        plt.ylabel("BMI")
        plt.title("BMI History Over Time")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    def create_gui(self):
        frame = ttk.Frame(self.root, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text="Weight (kg):").grid(row=0, column=0, sticky=tk.E)
        weight_entry = ttk.Entry(frame, textvariable=self.weight_var)
        weight_entry.grid(row=0, column=1)

        ttk.Label(frame, text="Height (m):").grid(row=1, column=0, sticky=tk.E)
        height_entry = ttk.Entry(frame, textvariable=self.height_var)
        height_entry.grid(row=1, column=1)

        calculate_button = ttk.Button(frame, text="Calculate BMI", command=self.calculate_bmi)
        calculate_button.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        self.result_label = ttk.Label(frame, text="")
        self.result_label.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        view_history_button = ttk.Button(frame, text="View History", command=self.view_history)
        view_history_button.grid(row=4, column=0, pady=(10, 0))

        plot_history_button = ttk.Button(frame, text="Plot History", command=self.plot_history)
        plot_history_button.grid(row=4, column=1, pady=(10, 0))

if __name__ == "__main__":
    root = tk.Tk()
    app = BMICalculator(root)
    root.mainloop()
