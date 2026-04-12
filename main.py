from tkinter import *
from tkinter import ttk, messagebox
from google.oauth2.service_account import Credentials
import os, gspread, datetime, sys
from dotenv import load_dotenv

load_dotenv()
SHEET_NAME = os.getenv("SHEET_NAME")
SHEET_NUMBER = os.getenv("SHEET_NUMBER")
SHEET_NUMBER2 = os.getenv("SHEET_NUMBER2")
SHEET_NUMBER3 = os.getenv("SHEET_NUMBER3")

day_to_row = {
    "Monday": 2,
    "Tuesday": 3,
    "Wednesday": 4,
    "Thursday": 5,
    "Friday": 6,
    "Saturday": 7,
    "Sunday": 8
}

try:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file("key.json", scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).worksheet(SHEET_NUMBER)
    sheet2 = client.open(SHEET_NAME).worksheet(SHEET_NUMBER2)
    sheet3 = client.open(SHEET_NAME).worksheet(SHEET_NUMBER3)
    date_cells = sheet3.get("A2:A1000")
except Exception as e:
    root_err = Tk()
    root_err.withdraw()
    messagebox.showerror("Connection Error", f"Failed to connect to Google Sheets:\n{e}")
    root_err.destroy()
    sys.exit(1)

def get_monday_cell():
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())  
    start_row = 2 
    for idx, row in enumerate(date_cells):
        if row and row[0]:
            date_str = row[0].strip()
            try:
                d = datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
                if d == monday:
                    actual_row = start_row + idx
                    cell_address = f"A{actual_row}"
                    return cell_address 
            except ValueError:
                print(f"Skipping invalid date format: {date_str}")
    return None

def get_today_row_from_weightsheet():
    today = datetime.date.today().strftime("%d/%m/%Y")
    start_row = 2  # Assuming dates start at A2
    date_cells = sheet3.get("A2:A1000")  # Adjust range as needed

    for idx, row in enumerate(date_cells):
        if row and row[0].strip():
            cell_date = row[0].strip()
            if cell_date == today:
                return start_row + idx  
    return None  


start_item = 2
food_items = sheet.get("A2:A38")
food_items = [item[0] for item in food_items if item]

# --- Colors & Styling ---
BG = "#1e1e2e"
FG = "#cdd6f4"
ACCENT = "#89b4fa"
ACCENT_HOVER = "#74c7ec"
SUCCESS = "#a6e3a1"
DANGER = "#f38ba8"
SURFACE = "#313244"
ENTRY_BG = "#45475a"
ENTRY_FG = "#cdd6f4"
FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SECTION = ("Segoe UI", 11, "bold")
FONT_STATUS = ("Segoe UI", 9)

root = Tk()
root.title('Diet Analysis')
root.configure(bg=BG)
root.resizable(False, False)

# --- ttk Style ---
style = ttk.Style()
style.theme_use("clam")
style.configure("TCombobox",
    fieldbackground=ENTRY_BG,
    background=SURFACE,
    foreground=ENTRY_FG,
    selectbackground=ACCENT,
    selectforeground=BG,
    arrowcolor=ACCENT)
style.map("TCombobox",
    fieldbackground=[("readonly", ENTRY_BG)],
    foreground=[("readonly", ENTRY_FG)])
style.configure("TSeparator", background="#585b70")

# --- Main container ---
main_frame = Frame(root, bg=BG, padx=30, pady=20)
main_frame.pack(fill=BOTH, expand=True)

# --- Title ---
title_label = Label(main_frame, text="🍽  Diet Analysis", font=FONT_TITLE, bg=BG, fg=ACCENT)
title_label.pack(pady=(0, 5))

today_str = datetime.datetime.today().strftime("%A, %B %d, %Y")
date_label = Label(main_frame, text=today_str, font=FONT_STATUS, bg=BG, fg="#6c7086")
date_label.pack(pady=(0, 15))

# --- Food Logging Section ---
food_section = Frame(main_frame, bg=SURFACE, padx=20, pady=15, highlightbackground="#585b70", highlightthickness=1)
food_section.pack(fill=X, pady=(0, 10))

Label(food_section, text="Log Food", font=FONT_SECTION, bg=SURFACE, fg=ACCENT).pack(anchor=W)
ttk.Separator(food_section, orient=HORIZONTAL).pack(fill=X, pady=(5, 10))

food_row = Frame(food_section, bg=SURFACE)
food_row.pack(fill=X, pady=(0, 8))

Label(food_row, text="Food Item", font=FONT, bg=SURFACE, fg=FG).pack(anchor=W)
selected_item = StringVar()
dropdown = ttk.Combobox(food_row, textvariable=selected_item, values=food_items, state="readonly", width=35, font=FONT)
dropdown.pack(fill=X, pady=(3, 0))

grams_row = Frame(food_section, bg=SURFACE)
grams_row.pack(fill=X, pady=(0, 8))

Label(grams_row, text="Amount (grams)", font=FONT, bg=SURFACE, fg=FG).pack(anchor=W)
grams_entry = Entry(grams_row, width=38, font=FONT, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG, relief=FLAT, highlightthickness=1, highlightbackground="#585b70", highlightcolor=ACCENT)
grams_entry.pack(fill=X, pady=(3, 0), ipady=4)

add_button = Button(food_section, text="Add Grams → Log Calories", command=lambda: add_grams_and_calories(),
    font=FONT_BOLD, bg=ACCENT, fg=BG, activebackground=ACCENT_HOVER, activeforeground=BG,
    relief=FLAT, cursor="hand2", padx=15, pady=6)
add_button.pack(fill=X, pady=(5, 0))

# --- Status ---
status_label = Label(main_frame, text="", font=FONT_STATUS, bg=BG, fg=SUCCESS, wraplength=350)
status_label.pack(pady=(5, 5))

# --- Weekly Logs Section ---
logs_section = Frame(main_frame, bg=SURFACE, padx=20, pady=15, highlightbackground="#585b70", highlightthickness=1)
logs_section.pack(fill=X, pady=(0, 10))

Label(logs_section, text="Weekly Logs", font=FONT_SECTION, bg=SURFACE, fg=ACCENT).pack(anchor=W)
ttk.Separator(logs_section, orient=HORIZONTAL).pack(fill=X, pady=(5, 10))

send_button = Button(logs_section, text="Send Weekly Data to Logs", command=lambda: send_data_to_logs(),
    font=FONT_BOLD, bg="#fab387", fg=BG, activebackground="#f9e2af", activeforeground=BG,
    relief=FLAT, cursor="hand2", padx=15, pady=6)
send_button.pack(fill=X)

# --- Weight Section ---
weight_section = Frame(main_frame, bg=SURFACE, padx=20, pady=15, highlightbackground="#585b70", highlightthickness=1)
weight_section.pack(fill=X, pady=(0, 10))

Label(weight_section, text="Log Weight", font=FONT_SECTION, bg=SURFACE, fg=ACCENT).pack(anchor=W)
ttk.Separator(weight_section, orient=HORIZONTAL).pack(fill=X, pady=(5, 10))

Label(weight_section, text="Today's Weight (kg)", font=FONT, bg=SURFACE, fg=FG).pack(anchor=W)
weight_entry = Entry(weight_section, width=38, font=FONT, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG, relief=FLAT, highlightthickness=1, highlightbackground="#585b70", highlightcolor=ACCENT)
weight_entry.pack(fill=X, pady=(3, 8), ipady=4)

log_weight_button = Button(weight_section, text="Log Today's Weight", command=lambda: log_today_weight(),
    font=FONT_BOLD, bg=SUCCESS, fg=BG, activebackground="#94e2d5", activeforeground=BG,
    relief=FLAT, cursor="hand2", padx=15, pady=6)
log_weight_button.pack(fill=X)

# --- Quit ---
quit_button = Button(main_frame, text="Quit Program", command=lambda: quit_app(),
    font=FONT, bg=SURFACE, fg=DANGER, activebackground=DANGER, activeforeground=BG,
    relief=FLAT, cursor="hand2", padx=15, pady=4,
    highlightbackground="#585b70", highlightthickness=1)
quit_button.pack(fill=X, pady=(5, 0))

def log_entry(food, grams, calories, protein):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{now} - Added {grams}g of {food}, Calories: {round(calories, 2)} and Protein: {round (protein, 5)}\n"
    with open("diet_log.txt", "a") as f:
        f.write(log_line)

def add_grams_and_calories():
    food = selected_item.get()
    grams_text = grams_entry.get()
    today = datetime.datetime.today().strftime("%A")
    target_row = day_to_row.get(today)

    if not target_row:
        status_label.config(text="Day not recognized.")
        return

    if not food or not grams_text:
        status_label.config(text="Please select a food and enter grams.")
        return

    try:
        grams = float(grams_text)
    except ValueError:
        status_label.config(text="Invalid number entered for grams.")
        return

    try:
        row_index = food_items.index(food) + start_item
    except ValueError:
        status_label.config(text="Food not found in column A.")
        return

    row_data = sheet.row_values(row_index)
    cal_value = row_data[1] if len(row_data) > 1 else None
    protein_value = row_data[4] if len(row_data) > 4 else None
    try:
        calories_per_100g = float(cal_value)
        protein_per_100g = float(protein_value)
    except (TypeError, ValueError):
        status_label.config(text="Invalid calorie or protein value in sheet.")
        return

    calories_to_add = (grams / 100.0) * calories_per_100g
    protein_to_add = (grams / 100.0) * protein_per_100g
    target_row_data = sheet2.row_values(target_row)
    existing_value = target_row_data[1] if len(target_row_data) > 1 else None
    existing_value2 = target_row_data[4] if len(target_row_data) > 4 else None

    try:
        if existing_value and existing_value.strip():
            updated_total = float(existing_value) + calories_to_add
        else:
            updated_total = calories_to_add
    except ValueError:
        updated_total = calories_to_add

    try:
        if existing_value2 and existing_value2.strip():
            updated_total2 = float(existing_value2) + protein_to_add
        else:
            updated_total2 = protein_to_add
    except ValueError:
        updated_total2 = protein_to_add

    sheet2.update_cell(target_row, 2, round(updated_total, 2))
    sheet2.update_cell(target_row, 5, round(updated_total2, 2))
    log_entry(food, grams, calories_to_add, protein_to_add)
    status_label.config(text=f"Logged {round(calories_to_add, 2)} cal and {round (protein_to_add, 2)} protein from {grams}g of {food}")    # After successful logging
    messagebox.showinfo("Success", f"{round(calories_to_add, 2)} cal and {round(protein_to_add, 2)} g protein logged.")

def send_data_to_logs():
    cell_address = get_monday_cell()  
    if not cell_address:
        status_label.config(text="Monday date not found in sheet.")
        return

    start_row = int(''.join(filter(str.isdigit, cell_address)))

    days_data = sheet2.get("B2:E8")
    calories_days = [row[0] if len(row) > 0 else "" for row in days_data]
    protein_days = [row[3] if len(row) > 3 else "" for row in days_data]

    calories_range = f"C{start_row}:C{start_row + 6}"
    protein_range = f"G{start_row}:G{start_row + 6}"

    calories_days_2d = [[float(val)] if val != "" else [""] for val in calories_days]
    protein_days_2d = [[float(val)] if val != "" else [""] for val in protein_days]

    sheet3.update(calories_range, calories_days_2d)
    sheet3.update(protein_range, protein_days_2d)

    sheet2.update("B2:B8", [[""] for _ in range(7)])
    sheet2.update("E2:E8", [[""] for _ in range(7)])

    messagebox.showinfo("Notice", "✅ Applied!\nThe program will now close. Please don’t press the button again until next week.")
    root.quit()

def log_today_weight():
    weight = weight_entry.get()
    if not weight:
        status_label.config(text="Please enter today's weight.")
        return

    try:
        weight_value = float(weight)
    except ValueError:
        status_label.config(text="Invalid weight value.")
        return

    if not (20 < weight_value < 300):
        status_label.config(text="Weight must be between 20 and 300 kg.")
        return

    row_number = get_today_row_from_weightsheet()
    if not row_number:
        status_label.config(text="Today's date not found in sheet.")
        return

    weight_cell = f"I{row_number}"
    sheet3.update(weight_cell, [[weight_value]])
    status_label.config(text=f"✅ Weight {weight_value} kg logged to {weight_cell}")
    messagebox.showinfo("Success", f"Weight {weight_value} kg logged to {weight_cell}.")


def quit_app():
    messagebox.showinfo("Notice", "Closing the application.")
    root.quit()

root.mainloop()