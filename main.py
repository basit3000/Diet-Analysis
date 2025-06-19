from tkinter import *
from tkinter import ttk
from oauth2client.service_account import ServiceAccountCredentials
import os, gspread, datetime
from dotenv import load_dotenv

load_dotenv()
SHEET_NAME = os.getenv("SHEET_NAME")
SHEET_NUMBER = os.getenv("SHEET_NUMBER")
SHEET_NUMBER2 = os.getenv("SHEET_NUMBER2")

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

start_item = 2
food_items = sheet.get("A2:A31")
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

root.mainloop()