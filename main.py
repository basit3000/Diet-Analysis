from tkinter import *
from tkinter import ttk, messagebox
from oauth2client.service_account import ServiceAccountCredentials
import os, gspread, datetime
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

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("key.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).worksheet(SHEET_NUMBER)
sheet2 = client.open(SHEET_NAME).worksheet(SHEET_NUMBER2)
sheet3 = client.open(SHEET_NAME).worksheet(SHEET_NUMBER3)
date_cells = sheet3.get("A2:A1000")  

dates = []

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
food_items = sheet.get("A2:A32")
food_items = [item[0] for item in food_items if item]

root = Tk()
root.title('Diet Analysis')

frame = LabelFrame(root, padx=20, pady=20)
frame.pack(padx=10, pady=10)

Label(frame, text="Select food item:").grid(row=0, column=0)

selected_item = StringVar()
dropdown = ttk.Combobox(frame, textvariable=selected_item)
dropdown['values'] = food_items
dropdown.grid(row=1, column=0, padx=5, pady=5)

Label(frame, text="Enter amount in grams:").grid(row=2, column=0)
grams_entry = Entry(frame, width=20)
grams_entry.grid(row=3, column=0, padx=5, pady=5)

Label(frame, text="Enter today's weight (kg):").grid(row=7, column=0)
weight_entry = Entry(frame, width=20)
weight_entry.grid(row=8, column=0, padx=5, pady=5)

status_label = Label(frame, text="")
status_label.grid(row=5, column=0)

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

    cal_value = sheet.cell(row_index, 2).value 
    protein_value = sheet.cell(row_index, 5).value
    try:
        calories_per_100g = float(cal_value)
        protein_per_100g = float(protein_value)
    except (TypeError, ValueError):
        status_label.config(text="Invalid calorie or protein value in sheet.")
        return

    calories_to_add = (grams / 100.0) * calories_per_100g
    protein_to_add = (grams / 100.0) * protein_per_100g
    existing_value = sheet2.cell(target_row, 2).value  
    existing_value2 = sheet2.cell(target_row, 5).value

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
    status_label.config(text=f"Logged {round(calories_to_add, 2)} cal and {round (protein_to_add, 2)} protein from {grams}g of {food}")

add_button = Button(frame, text="Add Grams → Log Calories", command=add_grams_and_calories)
add_button.grid(row=4, column=0, pady=10)

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

add_button = Button(frame, text="Send data to Logs (Please note: it is end of week)", command=send_data_to_logs)
add_button.grid(row=6, column=0, pady=10)

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

    row_number = get_today_row_from_weightsheet()
    if not row_number:
        status_label.config(text="Today's date not found in sheet.")
        return

    weight_cell = f"I{row_number}"
    sheet3.update(weight_cell, [[weight_value]])
    status_label.config(text=f"✅ Weight {weight_value} kg logged to {weight_cell}")

log_weight_button = Button(frame, text="Log Today’s Weight", command=log_today_weight)
log_weight_button.grid(row=9, column=0, pady=10)

def quit_app():
    messagebox.showinfo("Notice", "Closing the application.")
    root.quit()

quit_button = Button(frame, text="Quit Program", command=quit_app, fg="red")
quit_button.grid(row=10, column=0, pady=10)

root.mainloop()