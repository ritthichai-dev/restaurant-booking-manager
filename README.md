# Restaurant Booking Manager

A Python and Gradio application for managing restaurant
reservations, with Google Sheets as the storage backend.

Originally developed as **Smart Booking Log Digitizer**.

This is a manual booking-entry application. It does not
automatically read handwritten booking logs or perform OCR.

## Features

- Create bookings with unique IDs
- View recent bookings
- Filter bookings by date
- Load bookings for editing
- Update records without deleting and re-adding them
- Delete bookings with confirmation
- Validate customer and booking information
- Preserve booking minutes
- Store data in Google Sheets

## Technologies

- Python
- Gradio
- gspread / Google Sheets API
- python-dotenv
- pytest

## Requirements

- Python 3.10 or later
- A Google Cloud project
- A new Google service account
- A Google spreadsheet shared with that service account

## Installation

Create a virtual environment.

Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Google Sheets configuration

1. Create or select a Google Cloud project.
2. Enable the Google Sheets API and required access.
3. Create a service account.
4. Generate a NEW service-account JSON key.
5. Store that key outside the project directory.
6. Create a Google spreadsheet.
7. Share the spreadsheet with the service-account email.
8. Copy `.env.example` to `.env`.
9. Set `GOOGLE_APPLICATION_CREDENTIALS` to the private
   credentials file's absolute path.
10. Set `GOOGLE_SHEET_ID` to the ID from the spreadsheet URL.

Never commit the credentials file or your `.env`.

Do not reuse previously exposed service-account keys.

### Spreadsheet columns

The first worksheet uses:

BookingID | Name | Date | Time | Party Size |
Phone | Notes | Timestamp

The app creates the headers on an empty worksheet.

If an existing sheet already contains the original first
seven headers, the app adds the Timestamp header.

Make a backup before running the app on existing data.

## Running

```bash
python app.py
```

Open the local URL printed by Gradio.

The application binds to `127.0.0.1` with public sharing
disabled.

## Testing

Tests use an in-memory fake worksheet and do not require
Google credentials or internet access.

```bash
pytest -q
```

## Repository structure

```text
restaurant-booking-manager/
├── app.py
├── booking_manager.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── SECURITY.md
├── tests/
│   └── test_booking_manager.py
└── .github/
    └── workflows/
        └── tests.yml
```

## Known limitations

- Google Sheets is not a transactional database.
- Concurrent edits by multiple staff are not protected.
- Deletion cannot be undone without a separate backup.
- No user accounts or role-based permissions.
- No built-in booking conflict or capacity management.
- No automated customer notifications.
- Google API availability affects the application.

This is a portfolio and demonstration project, not a
production-ready restaurant booking service.

Do not use real customer data in public screenshots.

## Development notes

The original project was refactored to separate booking
logic from the Gradio user interface.

The updated design avoids deleting a booking before
saving its edited replacement.

Automated tests cover creation, searching, editing,
deletion, date handling and input validation.
