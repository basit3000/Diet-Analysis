# Diet Tracker & Calorie Logger

A desktop Tkinter app that calculates calories and protein from a Google
Sheets food catalog, records daily totals and weight, and archives each week.

## Features

- Search the food catalog and preview nutrition for a gram amount.
- Add calories and protein to the current weekday in Google Sheets.
- Compare today's totals with configurable calorie and protein goals.
- Record weight against today's date.
- Archive a week of totals to a dated log sheet.
- Append successful food entries to a local `diet_log.txt`.

## Architecture

`main.py` is the application and integration layer:

```text
.env + key.json
        │
        ▼
Tkinter UI ── gspread ── Google spreadsheet
    │                     ├── food catalog worksheet
    │                     ├── current-week worksheet
    │                     └── dated logs/weight worksheet
    └── diet_log.txt
```

At startup, the app connects to Google Sheets and caches:

- the food catalog from the first worksheet (`A2:E38`);
- date cells from the logs worksheet (`A2:A1000`);
- today's calorie and protein totals from the current-week worksheet.

This reduces API reads, but changes made directly in those ranges are not
picked up until the app restarts.

## Requirements

- Python 3 with Tkinter and a desktop display (there is no headless mode).
- Google Sheets API and Google Drive API enabled in a Google Cloud project.
- A Google service-account key.
- Access to the internet while the app is running.

Tkinter is included with most Python installations. Some Linux distributions
package it separately; for Debian/Ubuntu, install it with:

```bash
sudo apt install python3-tk
```

## Setup

The commands below use `python3`; use `python` instead if that is how Python 3
is exposed on your system.

1. Create a virtual environment and install the Python dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Prepare the spreadsheet. The quickest option is to upload
   [`Example Diet Analysis.xlsx`](./Example%20Diet%20Analysis.xlsx) to Google
   Sheets. Its worksheet titles are:

   - `Dish Calories`
   - `Calorie Count`
   - `Logs (New)`

3. In Google Cloud:

   - enable the Google Sheets API and Google Drive API;
   - create a service account and download its JSON key;
   - rename the downloaded key to `key.json` and place it beside `main.py`;
   - share the spreadsheet with the service account's email address.

4. Create the runtime environment file:

   ```bash
   cp example.env .env
   ```

   Set `SHEET_NAME` to the spreadsheet title. The three `SHEET_NUMBER*`
   settings are worksheet **titles**, despite their historical names:

   ```dotenv
   SHEET_NAME="Diet Analysis"
   SHEET_NUMBER="Dish Calories"
   SHEET_NUMBER2="Calorie Count"
   SHEET_NUMBER3="Logs (New)"
   CALORIE_GOAL="2000"
   PROTEIN_GOAL="150"
   ```

   `CALORIE_GOAL` and `PROTEIN_GOAL` are optional; invalid or missing values
   fall back to `2000` kcal and `150` g.

5. Run the app from the project root so it can find `.env` and `key.json`:

   ```bash
   python3 main.py
   ```

## Spreadsheet contract

The worksheet titles are configured in `.env`, but their row and column
layouts are fixed in `main.py`.

| Setting | Purpose | Required layout |
| --- | --- | --- |
| `SHEET_NUMBER` | Food catalog | Rows 2–38: name in A, kcal/100 g in B, protein/100 g in E |
| `SHEET_NUMBER2` | Current week | Rows 2–8 are Monday–Sunday; calorie totals in B and protein totals in E |
| `SHEET_NUMBER3` | Dated history | Dates in A, archived calories in C, archived protein in G, weight in I |

Dates in the history worksheet must use `DD/MM/YYYY` and must be present in
`A2:A1000`. Weight logging matches today's exact date, while weekly archiving
looks for the current week's Monday.

## Workflows

### Log food

1. Type to filter the food list, then select an exact catalog item.
2. Enter a gram amount greater than zero.
3. Select **Add Grams → Log Calories** or press Enter in the grams field.

The app calculates:

```text
calories = (grams / 100) × calories_per_100g
protein  = (grams / 100) × protein_per_100g
```

It adds the result to columns B and E on today's row, refreshes the summary,
and then appends a timestamped entry to `diet_log.txt`. Status messages clear
after seven seconds. Summary bars stop at 100%; the calorie value turns red
when the configured goal is exceeded.

### Log weight

Enter a value strictly between 20 and 300 kg, then select **Log Today's
Weight** or press Enter. The app writes it to column I on today's date row.

### Archive the week

Use **Send Weekly Data to Logs** once at the end of the week:

1. The app asks for confirmation.
2. It copies calorie totals from `B2:B8` to column C of the dated history,
   starting at the current Monday.
3. It copies protein totals from `E2:E8` to column G.
4. It clears `B2:B8` and `E2:E8` in the current-week worksheet.
5. It closes after showing a success message.

This is a destructive reset. The Google Sheets writes are separate API calls,
not a transaction. If an error is reported, inspect both worksheets before
retrying.

## Troubleshooting and constraints

- **Connection Error at startup:** verify all four required sheet settings,
  worksheet title spelling, both enabled APIs, spreadsheet sharing, and that
  `key.json` is in the current project directory. The app exits rather than
  running offline.
- **Food not found or catalog changes missing:** select a complete catalog
  name and restart after editing the food worksheet.
- **Today's date or Monday not found:** use `DD/MM/YYYY`, ensure the date is in
  `A2:A1000`, and restart if the date range changed while the app was open.
- **Avoid concurrent writers:** today's totals are updated from an in-memory
  cache. Running multiple app instances or editing current totals at the same
  time can overwrite newer values.
- **gspread compatibility:** write calls use the gspread 6.x
  `update(values, range_name)` API. Recreate the environment from
  `requirements.txt` if an older installation reports argument errors.
- Keep `.env`, `key.json`, and `diet_log.txt` private; they are ignored by Git.

## Repository layout

```text
Diet-Analysis/
├── Example Diet Analysis.xlsx  # Importable spreadsheet template
├── example.env                 # Canonical environment template
├── main.py                     # Tkinter app and Sheets integration
├── requirements.txt            # Python dependencies
├── LICENSE
└── README.md
```

Runtime-only files such as `.env`, `key.json`, and `diet_log.txt` are created
locally and are not committed.

## License

This project is licensed under the MIT License.
