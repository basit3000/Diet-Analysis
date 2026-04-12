# Diet Tracker & Calorie Logger with Google Sheets

Track your food intake, calculate calories and protein, log your weight, and record your daily consumption automatically into Google Sheets — all through a simple Python GUI.

✨ Features:

    ✅ Select food items from a defined list

    ✅ Input custom grams to automatically calculate calories and protein

    ✅ Automatically logs to correct weekday row in your Google Sheet

    ✅ Keeps a local diet_log.txt for timestamped history

    ✅ Uses a dynamic dropdown and clean Tkinter UI

    ✅ Log your daily weight to Google Sheets

    ✅ Send weekly calorie/protein data to a logs sheet at end of week

📁 Folder Structure

```text
diet-tracker/
├── .env                   # Environment variable file (copy from example.env)
├── example.env            # Example environment variable template
├── main.py                # Main script
├── key.json               # Google API credentials (NOT public)
├── diet_log.txt           # Local history logger
├── extracode.txt          # Extra code snippets
├── requirements.txt       # Python dependencies
├── LICENSE                # MIT License
├── README.md              # This file
```

🔧 Requirements

    Python 3.x

    Google Sheets API credentials

    gspread

    google-auth

    python-dotenv

Install dependencies:

```bash 
pip install -r requirements.txt
```

🔐 Setup Google Sheets API

    Visit: Google Developer Console

    Create a project > Enable Google Sheets API + Google Drive API

    Create a Service Account and download the JSON key

    Share your Google Sheet with the service account email (e.g., xyz@project.iam.gserviceaccount.com)

🚀 How to Use

    Prepare a Google Sheet with or use the Example Diet Analysis excel sheet by uploading to Google sheets:

        Column A: Food item names (e.g., from A2 to A31)

        Column B: Calories per 100g for each item

        Column E: Protein per 100g for each item

        Column B (Sheet 2): Rows 2–8 reserved for Monday–Sunday calorie logs

        Column E (Sheet 2): Rows 2-8 reserved for Monday-Sunday protein logs

        Column A (Sheet 3): Rows 2-1000 reserved for days of the year

        Column C (Sheet 3): Rows 2-1000 corresponding to the days column; the total caloric amount
 
        Column G (Sheet 3): Rows 2-1000 corresponding to the days column; the total protein amount

        Column I (Sheet 3): Rows 2-1000 current weight of the day in column A

        If you want to upload to Google Sheets:

        1. Go to Google Sheets

        2. Click on Blank spreadsheet
        
        3. Click on Open > Upload > Example Diet Analysis.xlsx

        4. Click Open

    Update the environment variable or use the example.env:

    Run the app: python main.py

    Select a food, enter grams, and click Add.

        Calories are calculated and added to your Google Sheet under the correct weekday.

        A timestamped entry is saved to diet_log.txt.

🧠 Summary

    Calorie Calculation:
    Calories = (grams / 100) * calories_per_100g
    Protein = (grams / 100) * protein_per_100g

    Sheet Update:
    Calories and Protein are added to column B and E of sheet 2 at the rows corresponding to the current weekday.

    Logging:
    Each entry is appended to diet_log.txt with timestamp.

📌 To Do / Ideas

Weekly summary dashboard feature implementation 

Weekly weight tracker 

Example Google Sheet for the project

Export to CSV or PDF

    Sync with calendar

📃 License

This project is licensed under the MIT License. Feel free to fork, modify, or use it.
