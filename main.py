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


def _env_float(name, default):
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return float(default)


# Daily targets (override in .env if you like)
CALORIE_GOAL = _env_float("CALORIE_GOAL", 2000)
PROTEIN_GOAL = _env_float("PROTEIN_GOAL", 150)

day_to_row = {
    "Monday": 2,
    "Tuesday": 3,
    "Wednesday": 4,
    "Thursday": 5,
    "Friday": 6,
    "Saturday": 7,
    "Sunday": 8
}


def to_float(value):
    """Best-effort float conversion; returns 0.0 for blank/invalid cells."""
    if value is None:
        return 0.0
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return 0.0


# --- Google Sheets connection + initial data load ---
try:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file("key.json", scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open(SHEET_NAME)
    sheet = spreadsheet.worksheet(SHEET_NUMBER)
    sheet2 = spreadsheet.worksheet(SHEET_NUMBER2)
    sheet3 = spreadsheet.worksheet(SHEET_NUMBER3)

    date_cells = sheet3.get("A2:A1000")

    # Cache the full food table once so logging needs no extra reads later.
    # Column A = name, B = calories/100g, E = protein/100g.
    food_rows = sheet.get("A2:E38")
    food_items = []
    food_data = {}
    for row in food_rows:
        if not row or not row[0].strip():
            continue
        name = row[0].strip()
        cal = to_float(row[1]) if len(row) > 1 else 0.0
        protein = to_float(row[4]) if len(row) > 4 else 0.0
        food_items.append(name)
        food_data[name] = (cal, protein)

    # Today's running totals from the weekly sheet (single read).
    today_weekday = datetime.datetime.today().strftime("%A")
    today_target_row = day_to_row.get(today_weekday)
    today_totals = [0.0, 0.0]
    if today_target_row:
        row_vals = sheet2.row_values(today_target_row)
        today_totals[0] = to_float(row_vals[1]) if len(row_vals) > 1 else 0.0
        today_totals[1] = to_float(row_vals[4]) if len(row_vals) > 4 else 0.0
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
                    return start_row + idx
            except ValueError:
                continue
    return None


def get_today_row_from_weightsheet():
    today = datetime.date.today().strftime("%d/%m/%Y")
    start_row = 2
    for idx, row in enumerate(date_cells):
        if row and row[0].strip() == today:
            return start_row + idx
    return None


start_item = 2

# --- Colors & Styling (Catppuccin Mocha) ---
BG = "#1e1e2e"
FG = "#cdd6f4"
MUTED = "#6c7086"
ACCENT = "#89b4fa"
ACCENT_HOVER = "#74c7ec"
SUCCESS = "#a6e3a1"
SUCCESS_HOVER = "#94e2d5"
WARN = "#fab387"
WARN_HOVER = "#f9e2af"
DANGER = "#f38ba8"
SURFACE = "#313244"
BORDER = "#585b70"
ENTRY_BG = "#45475a"
ENTRY_FG = "#cdd6f4"
FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SECTION = ("Segoe UI", 11, "bold")
FONT_STATUS = ("Segoe UI", 9)
FONT_METRIC = ("Segoe UI", 13, "bold")

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
style.configure("TSeparator", background=BORDER)
style.configure("Cal.Horizontal.TProgressbar",
    troughcolor=ENTRY_BG, background=ACCENT, thickness=14, borderwidth=0)
style.configure("Pro.Horizontal.TProgressbar",
    troughcolor=ENTRY_BG, background=SUCCESS, thickness=14, borderwidth=0)


def add_hover(widget, normal, hover):
    widget.bind("<Enter>", lambda e: widget.config(bg=hover))
    widget.bind("<Leave>", lambda e: widget.config(bg=normal))


def make_card(parent):
    card = Frame(parent, bg=SURFACE, padx=18, pady=12,
                 highlightbackground=BORDER, highlightthickness=1)
    card.pack(fill=X, pady=(0, 10))
    return card


# --- Main container ---
main_frame = Frame(root, bg=BG, padx=24, pady=16)
main_frame.pack(fill=BOTH, expand=True)

# --- Title ---
title_label = Label(main_frame, text="🍽  Diet Analysis", font=FONT_TITLE, bg=BG, fg=ACCENT)
title_label.pack(pady=(0, 2))

today_str = datetime.datetime.today().strftime("%A, %B %d, %Y")
date_label = Label(main_frame, text=today_str, font=FONT_STATUS, bg=BG, fg=MUTED)
date_label.pack(pady=(0, 12))

# --- Two-column body to keep the window short ---
columns = Frame(main_frame, bg=BG)
columns.pack(fill=BOTH, expand=True)
left_col = Frame(columns, bg=BG)
left_col.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 6), anchor=N)
right_col = Frame(columns, bg=BG)
right_col.pack(side=LEFT, fill=BOTH, expand=True, padx=(6, 0), anchor=N)

# --- Today's Summary Section ---
summary_section = make_card(left_col)
Label(summary_section, text="Today's Summary", font=FONT_SECTION, bg=SURFACE, fg=ACCENT).pack(anchor=W)
ttk.Separator(summary_section, orient=HORIZONTAL).pack(fill=X, pady=(5, 12))

cal_header = Frame(summary_section, bg=SURFACE)
cal_header.pack(fill=X)
Label(cal_header, text="Calories", font=FONT, bg=SURFACE, fg=FG).pack(side=LEFT)
cal_value_label = Label(cal_header, text="", font=FONT_METRIC, bg=SURFACE, fg=ACCENT)
cal_value_label.pack(side=RIGHT)
cal_bar = ttk.Progressbar(summary_section, style="Cal.Horizontal.TProgressbar", maximum=100)
cal_bar.pack(fill=X, pady=(2, 12))

pro_header = Frame(summary_section, bg=SURFACE)
pro_header.pack(fill=X)
Label(pro_header, text="Protein", font=FONT, bg=SURFACE, fg=FG).pack(side=LEFT)
pro_value_label = Label(pro_header, text="", font=FONT_METRIC, bg=SURFACE, fg=SUCCESS)
pro_value_label.pack(side=RIGHT)
pro_bar = ttk.Progressbar(summary_section, style="Pro.Horizontal.TProgressbar", maximum=100)
pro_bar.pack(fill=X, pady=(2, 0))

# --- Food Logging Section ---
food_section = make_card(left_col)
Label(food_section, text="Log Food", font=FONT_SECTION, bg=SURFACE, fg=ACCENT).pack(anchor=W)
ttk.Separator(food_section, orient=HORIZONTAL).pack(fill=X, pady=(5, 10))

food_row = Frame(food_section, bg=SURFACE)
food_row.pack(fill=X, pady=(0, 8))

Label(food_row, text="Food Item  (type to search)", font=FONT, bg=SURFACE, fg=FG).pack(anchor=W)
selected_item = StringVar()
dropdown = ttk.Combobox(food_row, textvariable=selected_item, values=food_items, width=35, font=FONT)
dropdown.pack(fill=X, pady=(3, 0))

grams_row = Frame(food_section, bg=SURFACE)
grams_row.pack(fill=X, pady=(0, 4))

Label(grams_row, text="Amount (grams)", font=FONT, bg=SURFACE, fg=FG).pack(anchor=W)
grams_entry = Entry(grams_row, width=38, font=FONT, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG,
                    relief=FLAT, highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT)
grams_entry.pack(fill=X, pady=(3, 0), ipady=4)

preview_label = Label(food_section, text="", font=FONT_STATUS, bg=SURFACE, fg=MUTED, anchor=W, justify=LEFT)
preview_label.pack(fill=X, pady=(6, 4))

add_button = Button(food_section, text="Add Grams → Log Calories", command=lambda: add_grams_and_calories(),
    font=FONT_BOLD, bg=ACCENT, fg=BG, activebackground=ACCENT_HOVER, activeforeground=BG,
    relief=FLAT, cursor="hand2", padx=15, pady=6)
add_button.pack(fill=X, pady=(5, 0))
add_hover(add_button, ACCENT, ACCENT_HOVER)

# --- Weight Section ---
weight_section = make_card(right_col)
Label(weight_section, text="Log Weight", font=FONT_SECTION, bg=SURFACE, fg=ACCENT).pack(anchor=W)
ttk.Separator(weight_section, orient=HORIZONTAL).pack(fill=X, pady=(5, 10))

Label(weight_section, text="Today's Weight (kg)", font=FONT, bg=SURFACE, fg=FG).pack(anchor=W)
weight_entry = Entry(weight_section, width=38, font=FONT, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG,
                     relief=FLAT, highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT)
weight_entry.pack(fill=X, pady=(3, 8), ipady=4)

log_weight_button = Button(weight_section, text="Log Today's Weight", command=lambda: log_today_weight(),
    font=FONT_BOLD, bg=SUCCESS, fg=BG, activebackground=SUCCESS_HOVER, activeforeground=BG,
    relief=FLAT, cursor="hand2", padx=15, pady=6)
log_weight_button.pack(fill=X)
add_hover(log_weight_button, SUCCESS, SUCCESS_HOVER)

# --- Weekly Logs Section ---
logs_section = make_card(right_col)
Label(logs_section, text="Weekly Logs", font=FONT_SECTION, bg=SURFACE, fg=ACCENT).pack(anchor=W)
ttk.Separator(logs_section, orient=HORIZONTAL).pack(fill=X, pady=(5, 10))
Label(logs_section, text="Archive this week's totals and reset the weekly sheet.",
      font=FONT_STATUS, bg=SURFACE, fg=MUTED, wraplength=320, justify=LEFT).pack(anchor=W, pady=(0, 8))

send_button = Button(logs_section, text="Send Weekly Data to Logs", command=lambda: send_data_to_logs(),
    font=FONT_BOLD, bg=WARN, fg=BG, activebackground=WARN_HOVER, activeforeground=BG,
    relief=FLAT, cursor="hand2", padx=15, pady=6)
send_button.pack(fill=X)
add_hover(send_button, WARN, WARN_HOVER)

# --- Status (spans full width under both columns) ---
status_label = Label(main_frame, text="", font=FONT_STATUS, bg=BG, fg=SUCCESS, wraplength=520)
status_label.pack(fill=X, pady=(2, 6))

# --- Quit ---
quit_button = Button(main_frame, text="Quit Program", command=lambda: quit_app(),
    font=FONT, bg=SURFACE, fg=DANGER, activebackground=DANGER, activeforeground=BG,
    relief=FLAT, cursor="hand2", padx=15, pady=4,
    highlightbackground=BORDER, highlightthickness=1)
quit_button.pack(fill=X, pady=(5, 0))


# --- Helpers for live feedback ---
_status_after_id = None


def set_status(msg, color=SUCCESS):
    global _status_after_id
    status_label.config(text=msg, fg=color)
    if _status_after_id:
        root.after_cancel(_status_after_id)
    _status_after_id = root.after(7000, lambda: status_label.config(text=""))


def refresh_summary():
    cal, pro = today_totals
    cal_pct = min(cal / CALORIE_GOAL * 100, 100) if CALORIE_GOAL else 0
    pro_pct = min(pro / PROTEIN_GOAL * 100, 100) if PROTEIN_GOAL else 0
    cal_bar["value"] = cal_pct
    pro_bar["value"] = pro_pct
    cal_value_label.config(
        text=f"{round(cal)} / {round(CALORIE_GOAL)} kcal",
        fg=DANGER if cal > CALORIE_GOAL else ACCENT)
    pro_value_label.config(
        text=f"{round(pro, 1)} / {round(PROTEIN_GOAL)} g",
        fg=SUCCESS if pro >= PROTEIN_GOAL else FG)


def update_preview(*_):
    food = selected_item.get().strip()
    info = food_data.get(food)
    if not info:
        preview_label.config(text="")
        return
    cal100, pro100 = info
    grams_text = grams_entry.get().strip()
    if grams_text:
        try:
            g = float(grams_text)
            preview_label.config(
                text=f"➜ {round(g / 100 * cal100, 1)} kcal · {round(g / 100 * pro100, 1)} g protein")
            return
        except ValueError:
            pass
    preview_label.config(text=f"{cal100:g} kcal · {pro100:g} g protein per 100g")


def filter_dropdown(event):
    if event.keysym in ("Return", "Escape", "Up", "Down", "Tab"):
        return
    typed = selected_item.get().strip().lower()
    if not typed:
        dropdown["values"] = food_items
    else:
        matches = [f for f in food_items if typed in f.lower()]
        dropdown["values"] = matches if matches else food_items
    update_preview()


def log_entry(food, grams, calories, protein):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{now} - Added {grams}g of {food}, Calories: {round(calories, 2)} and Protein: {round(protein, 5)}\n"
    with open("diet_log.txt", "a") as f:
        f.write(log_line)


def add_grams_and_calories():
    food = selected_item.get().strip()
    grams_text = grams_entry.get().strip()
    today = datetime.datetime.today().strftime("%A")
    target_row = day_to_row.get(today)

    if not target_row:
        set_status("Day not recognized.", DANGER)
        return

    if not food or not grams_text:
        set_status("Please select a food and enter grams.", DANGER)
        return

    if food not in food_data:
        set_status("Food not found in the list.", DANGER)
        return

    try:
        grams = float(grams_text)
    except ValueError:
        set_status("Invalid number entered for grams.", DANGER)
        return

    if grams <= 0:
        set_status("Grams must be greater than zero.", DANGER)
        return

    calories_per_100g, protein_per_100g = food_data[food]
    calories_to_add = (grams / 100.0) * calories_per_100g
    protein_to_add = (grams / 100.0) * protein_per_100g

    # Use cached running totals when logging for the current day to avoid an
    # extra read; otherwise fetch the target row directly.
    if target_row == today_target_row:
        new_cal = today_totals[0] + calories_to_add
        new_pro = today_totals[1] + protein_to_add
    else:
        existing = sheet2.row_values(target_row)
        new_cal = (to_float(existing[1]) if len(existing) > 1 else 0.0) + calories_to_add
        new_pro = (to_float(existing[4]) if len(existing) > 4 else 0.0) + protein_to_add

    try:
        sheet2.batch_update([
            {"range": f"B{target_row}", "values": [[round(new_cal, 2)]]},
            {"range": f"E{target_row}", "values": [[round(new_pro, 2)]]},
        ])
    except Exception as e:
        set_status(f"Failed to update sheet: {e}", DANGER)
        return

    if target_row == today_target_row:
        today_totals[0] = new_cal
        today_totals[1] = new_pro
        refresh_summary()

    log_entry(food, grams, calories_to_add, protein_to_add)
    grams_entry.delete(0, END)
    update_preview()
    set_status(f"Logged {round(calories_to_add, 1)} kcal · {round(protein_to_add, 1)} g protein "
               f"from {grams:g}g of {food}.", SUCCESS)


def send_data_to_logs():
    if not messagebox.askyesno(
            "Confirm Weekly Archive",
            "This copies this week's daily totals into the logs sheet and CLEARS the "
            "weekly sheet.\n\nOnly do this once at the end of the week. Continue?"):
        return

    start_row = get_monday_cell()
    if not start_row:
        set_status("Monday date not found in sheet.", DANGER)
        return

    days_data = sheet2.get("B2:E8")
    calories_days = [row[0] if len(row) > 0 else "" for row in days_data]
    protein_days = [row[3] if len(row) > 3 else "" for row in days_data]

    calories_range = f"C{start_row}:C{start_row + 6}"
    protein_range = f"G{start_row}:G{start_row + 6}"

    calories_days_2d = [[to_float(val)] if str(val).strip() != "" else [""] for val in calories_days]
    protein_days_2d = [[to_float(val)] if str(val).strip() != "" else [""] for val in protein_days]

    try:
        # gspread 6.x signature: update(values, range_name)
        sheet3.update(calories_days_2d, calories_range)
        sheet3.update(protein_days_2d, protein_range)
        sheet2.update([[""] for _ in range(7)], "B2:B8")
        sheet2.update([[""] for _ in range(7)], "E2:E8")
    except Exception as e:
        set_status(f"Failed to archive weekly data: {e}", DANGER)
        return

    today_totals[0] = 0.0
    today_totals[1] = 0.0
    refresh_summary()
    messagebox.showinfo("Notice", "✅ Weekly data archived and the weekly sheet was reset.\n"
                                   "The program will now close. Please don't run this again until next week.")
    root.quit()


def log_today_weight():
    weight = weight_entry.get().strip()
    if not weight:
        set_status("Please enter today's weight.", DANGER)
        return

    try:
        weight_value = float(weight)
    except ValueError:
        set_status("Invalid weight value.", DANGER)
        return

    if not (20 < weight_value < 300):
        set_status("Weight must be between 20 and 300 kg.", DANGER)
        return

    row_number = get_today_row_from_weightsheet()
    if not row_number:
        set_status("Today's date not found in sheet.", DANGER)
        return

    weight_cell = f"I{row_number}"
    try:
        sheet3.update([[weight_value]], weight_cell)
    except Exception as e:
        set_status(f"Failed to log weight: {e}", DANGER)
        return

    weight_entry.delete(0, END)
    set_status(f"✅ Weight {weight_value:g} kg logged for today.", SUCCESS)


def quit_app():
    root.quit()


# --- Bindings ---
dropdown.bind("<KeyRelease>", filter_dropdown)
dropdown.bind("<<ComboboxSelected>>", update_preview)
grams_entry.bind("<KeyRelease>", update_preview)
grams_entry.bind("<Return>", lambda e: add_grams_and_calories())
weight_entry.bind("<Return>", lambda e: log_today_weight())

refresh_summary()
root.mainloop()
