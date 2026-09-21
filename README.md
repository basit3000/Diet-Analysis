# Diet Analysis

Tkinter desktop app that logs food calories/protein and daily weight into a Google Spreadsheet via a service account (`gspread`).

## Intent

Keep a fixed weekly calorie/protein sheet in sync with a searchable food list, archive the week into a long-running logs sheet, and optionally record weight — without editing Sheets by hand every meal.

## Architecture

```
main.py (Tkinter GUI)
  ├── Startup: authorize key.json → open SHEET_NAME → cache food + today totals
  ├── Log food → update weekly sheet (sheet2) B/E for today's weekday row
  ├── Log weight → update logs sheet (sheet3) column I for today's date row
  └── Archive week → copy Mon–Sun B/E into logs C/G, clear weekly B/E, quit
```

At startup the app:

1. Loads env from `.env` (`python-dotenv`).
2. Authorizes with `key.json` (Google service account).
3. Opens three worksheets by **title** (not numeric index).
4. Caches food rows `A2:E38` and today's weekly totals in memory so logging does not re-read the food table.

If Sheets auth or open fails, a dialog is shown and the process exits.

## Spreadsheet contract

Use [`Example Diet Analysis.xlsx`](Example%20Diet%20Analysis.xlsx) as a template (upload to Google Sheets), or match this schema.

| Env var | Role | Example title (bundled workbook) | Required layout |
|---------|------|----------------------------------|-----------------|
| `SHEET_NUMBER` | Food table | `Dish Calories` | `A2:E38`: name (A), kcal/100g (B), protein/100g (E). Empty name cells are skipped. |
| `SHEET_NUMBER2` | Weekly running totals | `Calorie Count` | Rows **2–8** = Mon–Sun. Calories in **B**, protein in **E**. |
| `SHEET_NUMBER3` | Archive + weight | `Logs (New)` | Col **A** dates as `DD/MM/YYYY` from row 2. Archive writes calories **C**, protein **G** for seven days from the Monday row. Weight writes **I** on today's date row. |

`SHEET_NAME` is the spreadsheet title in Drive (not a worksheet tab).

Weekday → weekly row mapping is fixed in code: Monday=2 … Sunday=8.

## Setup

1. Python 3.x with a display (Tkinter).
2. Create a Google Cloud project, enable **Google Sheets API** and **Google Drive API**, create a service account, download the JSON key as `key.json` in the project root (do not commit it).
3. Share the spreadsheet with the service account email (Editor).
4. Copy env template and fill real titles:

```bash
cp example.env .env
pip install -r requirements.txt
python main.py
```

### Environment

| Variable | Required | Notes |
|----------|----------|-------|
| `SHEET_NAME` | Yes | Spreadsheet title in Drive |
| `SHEET_NUMBER` | Yes | Food worksheet **title** |
| `SHEET_NUMBER2` | Yes | Weekly totals worksheet **title** |
| `SHEET_NUMBER3` | Yes | Logs / weight worksheet **title** |
| `CALORIE_GOAL` | No | Today's Summary bar target (default `2000`) |
| `PROTEIN_GOAL` | No | Today's Summary bar target (default `150`) |

`example.env` ships with placeholder titles plus optional goals. For the bundled workbook, set titles to `Dish Calories`, `Calorie Count`, and `Logs (New)`.

## Workflows

### Log food

1. Type to filter the food combobox (substring match, case-insensitive).
2. Enter grams (`> 0`). Preview shows projected kcal/protein.
3. Click **Add Grams → Log Calories** or press Enter in the grams field.
4. App adds `(grams/100) * per-100g` values into today's **B** (calories) and **E** (protein) on the weekly sheet, updates the summary bars, and appends a line to local `diet_log.txt`.

### Log weight

1. Enter weight in kg (must be **> 20 and < 300**).
2. Click **Log Today's Weight** or press Enter.
3. App finds today's `DD/MM/YYYY` in sheet3 column A and writes the value to column **I**.

### Archive the week (destructive)

1. Ensure the logs sheet has a Monday date row for the current week (`DD/MM/YYYY` in column A).
2. Click **Send Weekly Data to Logs** and confirm the dialog.
3. App copies weekly `B2:B8` → logs `C{monday}:C{monday+6}` and `E2:E8` → `G{monday}:G{monday+6}`, clears weekly B and E, resets in-memory totals, then **quits**.

Only run once at week end. Re-running the same week overwrites that archive block and clears the weekly sheet again.

## Project layout

```text
├── main.py                      # GUI + Sheets workflows
├── example.env                  # Env template (copy to .env)
├── key.json                     # Service account key (local only)
├── Example Diet Analysis.xlsx   # Schema template
├── requirements.txt             # gspread, google-auth, python-dotenv
├── diet_log.txt                 # Created at runtime (local meal history)
└── README.md
```

## Dependencies

- `gspread` (6.x-style `update(values, range_name)` calls)
- `google-auth`
- `python-dotenv`
- Tkinter (stdlib; needs a graphical session)

## Constraints and pitfalls

| Pitfall | Detail |
|---------|--------|
| Worksheet titles vs indexes | `SHEET_NUMBER*` must be tab **names**. Numeric indexes fail. |
| Date format | Logs dates must be `DD/MM/YYYY`. Excel serial numbers or other formats break Monday/today lookup. |
| Food cache is startup-only | Editing the food sheet while the app runs is ignored until restart. |
| Food range hard-coded | Only `A2:E38` is loaded. Foods below row 38 never appear. |
| Single-user / no locking | Concurrent GUI instances can race on the same cells. |
| Archive is not transactional | A mid-failure can leave logs updated and weekly sheet partially cleared (or the reverse). |
| Headless / SSH | Tkinter needs a display; use a desktop or virtual framebuffer. |
| Credentials | Keep `key.json` and `.env` out of git. Share the sheet with the service account email. |
| Status messages | Inline status clears after ~7s; validation errors do not use blocking dialogs (except archive confirm / connection failure / archive success). |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Connection Error on launch | Bad `key.json`, sheet not shared, wrong `SHEET_NAME`, or wrong tab titles | Verify Drive share + exact titles in `.env` |
| Food not found | Name mismatch or outside `A2:E38` | Match sheet A column exactly; restart after edits |
| Today's date not found (weight) | Missing/wrong date in logs col A | Add today as `DD/MM/YYYY` |
| Monday date not found (archive) | No Monday row for this week | Pre-seed seven dated rows starting Monday |
| Summary bars wrong after archive | Expected — totals reset and app quits | Relaunch for the new week |
| `update()` TypeError | Older gspread API | Use current `requirements.txt` (`gspread` 6.x value-first `update`) |
