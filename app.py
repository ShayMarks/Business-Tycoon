import tkinter as tk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt
import random
from PIL import Image, ImageTk

# ------------------- Worker Class ------------------- #
class Worker:
    def __init__(self, canvas, image, canvas_width, canvas_height):
        self.canvas = canvas
        self.image = image
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        
        # Attempt to get the image dimensions (80×80 after resizing)
        try:
            self.img_width = self.image.width()
            self.img_height = self.image.height()
        except Exception:
            self.img_width = 80
            self.img_height = 80

        # Random horizontal starting position ensuring the full image is visible
        self.x = random.randint(0, canvas_width - self.img_width)
        # Vertical position: place the image at the bottom of the canvas
        self.y = canvas_height - self.img_height
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 3)
        # Create the image on the canvas using anchor="nw" (top-left corner)
        self.canvas_id = self.canvas.create_image(self.x, self.y, image=self.image, anchor="nw")

    def update(self):
        self.x += self.direction * self.speed
        if self.x < 0:
            self.x = 0
            self.direction = 1
            self.randomize_speed()
        elif self.x > self.canvas_width - self.img_width:
            self.x = self.canvas_width - self.img_width
            self.direction = -1
            self.randomize_speed()
        if random.random() < 0.02:
            self.direction = random.choice([-1, 1])
            self.randomize_speed()
        self.canvas.coords(self.canvas_id, self.x, self.y)

    def randomize_speed(self):
        self.speed = random.randint(1, 3)

# ------------------- BusinessGame Class ------------------- #
class BusinessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Business - Project Management")
        # Set a nearly full-screen window
        self.root.geometry("1200x800")
        self.root.configure(bg="#f5f5f5")  # Light gray background

        # Business management variables
        self.day = 0
        self.budget = 1000
        self.employees = 1
        self.upgrade_level = 0
        self.business_name = "My Business"

        self.data_log = []         # Data for analysis
        self.worker_sprites = []   # List of worker sprites (moving)
        self.box_items = []        # List of box items (static)

        # Load worker image – resized to 80×80
        try:
            original_worker = Image.open("worker.png")
            resized_worker = original_worker.resize((80, 80), Image.Resampling.LANCZOS)
            self.worker_img = ImageTk.PhotoImage(resized_worker)
        except Exception as e:
            messagebox.showerror("Image Error", f"Error loading worker.png:\n{e}")
            self.worker_img = None

        # Load box image – resized to 20×20
        try:
            original_box = Image.open("box.png")
            resized_box = original_box.resize((20, 20), Image.Resampling.LANCZOS)
            self.box_img = ImageTk.PhotoImage(resized_box)
            self.box_width = 20
            self.box_height = 20
        except Exception as e:
            messagebox.showerror("Image Error", f"Error loading box.png:\n{e}")
            self.box_img = None

        self.create_widgets()
        self.update_labels()
        self.update_sign()

        # Add initial worker sprites if worker image loaded
        if self.worker_img:
            for _ in range(self.employees):
                self.add_worker_sprite()
            self.update_workers()

        # Prompt for business name at startup
        self.ask_business_name()

    def create_widgets(self):
        # Top section – Status and Actions
        top_frame = tk.Frame(self.root, bg="#f5f5f5")
        top_frame.pack(pady=10)

        self.lbl_title = tk.Label(top_frame, text="Smart Business Management", font=("Arial", 20, "bold"), bg="#f5f5f5", fg="black")
        self.lbl_title.pack(pady=5)

        status_frame = tk.Frame(top_frame, bg="#f5f5f5")
        status_frame.pack(pady=5)

        self.lbl_business = tk.Label(status_frame, text=f"Business: {self.business_name}", font=("Arial", 16, "bold"), bg="#f5f5f5", fg="black")
        self.lbl_business.grid(row=0, column=0, padx=10, sticky="w")
        self.lbl_day = tk.Label(status_frame, text=f"Day: {self.day}", font=("Arial", 14, "bold"), bg="#f5f5f5", fg="black")
        self.lbl_day.grid(row=1, column=0, padx=10, sticky="w")
        self.lbl_budget = tk.Label(status_frame, text=f"Budget: {self.budget}", font=("Arial", 14, "bold"), bg="#f5f5f5", fg="black")
        self.lbl_budget.grid(row=2, column=0, padx=10, sticky="w")
        self.lbl_employees = tk.Label(status_frame, text=f"Employees: {self.employees}", font=("Arial", 14, "bold"), bg="#f5f5f5", fg="black")
        self.lbl_employees.grid(row=3, column=0, padx=10, sticky="w")
        self.lbl_upgrade = tk.Label(status_frame, text=f"Upgrade: {self.upgrade_level}", font=("Arial", 14, "bold"), bg="#f5f5f5", fg="black")
        self.lbl_upgrade.grid(row=4, column=0, padx=10, sticky="w")

        actions_frame = tk.Frame(top_frame, bg="#f5f5f5")
        actions_frame.pack(pady=10)

        simulate_frame = tk.Frame(actions_frame, bg="#f5f5f5", bd=2, relief="groove", padx=5, pady=5)
        simulate_frame.pack(pady=5, fill="x", padx=20)
        self.btn_simulate_day = tk.Button(simulate_frame, text="Simulate Work Day", command=self.simulate_day, width=20, font=("Arial", 12, "bold"))
        self.btn_simulate_day.pack(side="left", padx=5)
        self.label_simulate_day_outcome = tk.Label(simulate_frame, text="", font=("Arial", 12, "bold"), bg="#f5f5f5", fg="black")
        self.label_simulate_day_outcome.pack(side="left", padx=5)

        hire_frame = tk.Frame(actions_frame, bg="#f5f5f5", bd=2, relief="groove", padx=5, pady=5)
        hire_frame.pack(pady=5, fill="x", padx=20)
        self.btn_hire = tk.Button(hire_frame, text="Hire Employee", command=self.hire_employee, width=20, font=("Arial", 12, "bold"))
        self.btn_hire.pack(side="left", padx=5)
        self.label_hire_outcome = tk.Label(hire_frame, text="", font=("Arial", 12, "bold"), bg="#f5f5f5", fg="black")
        self.label_hire_outcome.pack(side="left", padx=5)

        upgrade_frame = tk.Frame(actions_frame, bg="#f5f5f5", bd=2, relief="groove", padx=5, pady=5)
        upgrade_frame.pack(pady=5, fill="x", padx=20)
        self.btn_upgrade = tk.Button(upgrade_frame, text="Upgrade Business", command=self.upgrade_business, width=20, font=("Arial", 12, "bold"))
        self.btn_upgrade.pack(side="left", padx=5)
        self.label_upgrade_outcome = tk.Label(upgrade_frame, text="", font=("Arial", 12, "bold"), bg="#f5f5f5", fg="black")
        self.label_upgrade_outcome.pack(side="left", padx=5)

        self.btn_check_income = tk.Button(actions_frame, text="Check Today's Income", command=self.check_income, width=30, font=("Arial", 12, "bold"))
        self.btn_check_income.pack(pady=5)
        self.btn_show_graphs = tk.Button(actions_frame, text="Show Graphs", command=self.show_graphs, width=30, font=("Arial", 12, "bold"))
        self.btn_show_graphs.pack(pady=5)

        bottom_frame = tk.Frame(self.root, bg="#f5f5f5")
        bottom_frame.pack(side="bottom", fill="x", pady=10)

        # A styled sign label with dark background and bold italic text
        self.sign_label = tk.Label(bottom_frame, text="", font=("Arial", 18, "bold italic"), fg="white", bg="#444444", padx=10, pady=10)
        self.sign_label.pack(fill="x")

        # The shop area – a canvas of size 650×300 with a black background where workers move
        self.floor_canvas_width = 650
        self.floor_canvas_height = 300
        self.floor_canvas = tk.Canvas(bottom_frame, width=self.floor_canvas_width, height=self.floor_canvas_height, bg="black", highlightthickness=0)
        self.floor_canvas.pack()

    def update_labels(self):
        self.lbl_day.config(text=f"Day: {self.day}")
        self.lbl_budget.config(text=f"Budget: {self.budget}")
        self.lbl_employees.config(text=f"Employees: {self.employees}")
        self.lbl_upgrade.config(text=f"Upgrade: {self.upgrade_level}")
        self.update_expected_outcomes()
        self.update_sign()

    def update_expected_outcomes(self):
        expected_income = 100 + self.employees * 20 + self.upgrade_level * 50
        expected_expense = 50 + self.employees * 10 + self.upgrade_level * 20
        expected_profit = expected_income - expected_expense
        simulate_text = f"Expected: +{expected_profit}"
        simulate_color = "green" if expected_profit >= 0 else "red"
        self.label_simulate_day_outcome.config(text=simulate_text, fg=simulate_color)

        hire_text = "Cost: -300"
        self.label_hire_outcome.config(text=hire_text, fg="red")

        upgrade_cost = 200 + self.upgrade_level * 100
        upgrade_text = f"Cost: -{upgrade_cost}"
        self.label_upgrade_outcome.config(text=upgrade_text, fg="red")

    def update_sign(self):
        sign_text = f"Welcome to {self.business_name}\nLevel: {self.upgrade_level}"
        self.sign_label.config(text=sign_text)
        self.lbl_business.config(text=f"Business: {self.business_name}")

    def ask_business_name(self):
        def set_name():
            name = entry.get().strip()
            if name:
                self.business_name = name
                self.update_sign()
                top.destroy()
            else:
                messagebox.showerror("Input Error", "Please enter a valid business name.")
        top = tk.Toplevel(self.root)
        top.title("Enter Business Name")
        top.grab_set()
        tk.Label(top, text="Enter your business name:", font=("Arial", 14, "bold")).pack(pady=10, padx=10)
        entry = tk.Entry(top, font=("Arial", 14))
        entry.pack(pady=5, padx=10)
        entry.focus_set()
        tk.Button(top, text="OK", command=set_name, font=("Arial", 12, "bold")).pack(pady=10)
        self.root.wait_window(top)

    def simulate_day(self):
        self.day += 1
        base_income = 100
        employee_bonus = self.employees * 20
        upgrade_bonus = self.upgrade_level * 50
        income = base_income + employee_bonus + upgrade_bonus
        base_expense = 50
        wage_expense = self.employees * 10
        upgrade_cost = self.upgrade_level * 20
        expense = base_expense + wage_expense + upgrade_cost
        profit = income - expense
        self.budget += profit
        day_record = {
            "Day": self.day,
            "Income": income,
            "Expense": expense,
            "Profit": profit,
            "Budget": self.budget,
            "Employees": self.employees,
            "Upgrade Level": self.upgrade_level
        }
        self.data_log.append(day_record)
        self.update_labels()
        messagebox.showinfo("Day Summary", f"Day {self.day}\nIncome: {income}\nExpense: {expense}\nProfit: {profit}")

    def hire_employee(self):
        cost = 300
        if self.budget >= cost:
            self.budget -= cost
            self.employees += 1
            self.update_labels()
            messagebox.showinfo("Hire Employee", f"New employee hired! Cost: {cost}")
            self.add_worker_sprite()
        else:
            messagebox.showerror("Hire Employee Failed", f"Insufficient budget.\nRequired: {cost}\nCurrent: {self.budget}")

    def upgrade_business(self):
        cost = 200 + self.upgrade_level * 100
        if self.budget >= cost:
            self.budget -= cost
            self.upgrade_level += 1
            self.update_labels()
            messagebox.showinfo("Upgrade Business", f"Business upgraded! Upgrade cost: {cost}")
            self.add_box_sprite()  # Add a box item to the shop area
        else:
            messagebox.showerror("Upgrade Failed", f"Insufficient budget for upgrade.\nRequired: {cost}\nCurrent: {self.budget}")

    def check_income(self):
        if self.data_log:
            last_day = self.data_log[-1]
            info = (f"Day {last_day['Day']}\n"
                    f"Income: {last_day['Income']}\n"
                    f"Expense: {last_day['Expense']}\n"
                    f"Profit: {last_day['Profit']}")
            messagebox.showinfo("Today's Data", info)
        else:
            messagebox.showinfo("Data", "No work day has been simulated yet.")

    def show_graphs(self):
        if not self.data_log:
            messagebox.showinfo("Graphs", "No data available for analysis. Please simulate at least one work day.")
            return
        df = pd.DataFrame(self.data_log)
        plt.figure(figsize=(10, 12))
        plt.subplot(3, 1, 1)
        plt.plot(df["Day"], df["Profit"], marker="o", linestyle="-", color="green")
        plt.title("Daily Profit")
        plt.xlabel("Day")
        plt.ylabel("Profit")
        plt.grid(True)
        df["Cumulative Profit"] = df["Profit"].cumsum()
        plt.subplot(3, 1, 2)
        plt.plot(df["Day"], df["Cumulative Profit"], marker="o", linestyle="-", color="blue")
        plt.title("Cumulative Profit")
        plt.xlabel("Day")
        plt.ylabel("Cumulative Profit")
        plt.grid(True)
        plt.subplot(3, 1, 3)
        plt.plot(df["Day"], df["Income"], marker="o", linestyle="-", label="Income", color="orange")
        plt.plot(df["Day"], df["Expense"], marker="o", linestyle="-", label="Expense", color="red")
        plt.title("Income vs Expense")
        plt.xlabel("Day")
        plt.ylabel("Amount")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    # ------------------- Worker Management ------------------- #
    def add_worker_sprite(self):
        if self.worker_img:
            worker = Worker(self.floor_canvas, self.worker_img, self.floor_canvas_width, self.floor_canvas_height)
            self.worker_sprites.append(worker)

    def update_workers(self):
        for worker in self.worker_sprites:
            worker.update()
        self.root.after(50, self.update_workers)

    # ------------------- Adding a Box Item to the Shop Area ------------------- #
    def add_box_sprite(self):
        if self.box_img:
            # Choose a random position in the upper half of the canvas
            x = random.randint(0, self.floor_canvas_width - self.box_width)
            y = random.randint(0, self.floor_canvas_height // 2 - self.box_height)
            box_item = self.floor_canvas.create_image(x, y, image=self.box_img, anchor="nw")
            # Lower the box so that worker images appear above it
            self.floor_canvas.lower(box_item)
            self.box_items.append(box_item)

def main():
    root = tk.Tk()
    app = BusinessGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()