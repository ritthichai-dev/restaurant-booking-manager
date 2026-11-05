import uuid
from datetime import date, datetime

HEADERS = [
    "BookingID", "Name", "Date", "Time",
    "Party Size", "Phone", "Notes", "Timestamp"
]
DISPLAY_HEADERS = HEADERS[:7]


def parse_datetime(value):
    if value is None or value == "":
        raise ValueError("Booking date and time are required.")

    try:
        if isinstance(value, datetime):
            result = value
        elif isinstance(value, (int, float)):
            result = datetime.fromtimestamp(value)
        elif isinstance(value, str):
            result = datetime.fromisoformat(
                value.strip().replace("Z", "+00:00")
            )
        else:
            raise ValueError("Unsupported date format.")

        if result.tzinfo is not None:
            result = result.astimezone().replace(tzinfo=None)

        return result.replace(second=0, microsecond=0)
    except (ValueError, OverflowError, OSError) as exc:
        raise ValueError("Invalid booking date or time.") from exc


def date_string(value):
    if isinstance(value, date) and not isinstance(value, datetime):
        return value.isoformat()
    return parse_datetime(value).date().isoformat()


def validate_booking(name, when, party_size, phone, notes):
    name = str(name or "").strip()
    phone = str(phone or "").strip()
    notes = str(notes or "").strip()

    if not 1 <= len(name) <= 100:
        raise ValueError("Name must contain 1–100 characters.")

    try:
        number = float(party_size)
        if not number.is_integer():
            raise ValueError()
        party_size = int(number)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("Party size must be a whole number.")

    if not 1 <= party_size <= 100:
        raise ValueError("Party size must be between 1 and 100.")

    if len(phone) > 40 or sum(c.isdigit() for c in phone) < 6:
        raise ValueError("Enter a valid contact phone number.")

    if len(notes) > 500:
        raise ValueError("Notes cannot exceed 500 characters.")

    dt = parse_datetime(when)

    return [
        name,
        dt.strftime("%Y-%m-%d"),
        dt.strftime("%I:%M %p"),
        str(party_size),
        phone,
        notes,
    ]


class BookingManager:
    def __init__(self, worksheet):
        self.sheet = worksheet
        self.ensure_headers()

    def ensure_headers(self):
        records = self.sheet.get_all_values()

        if not records:
            self.sheet.update(
                range_name="A1:H1", values=[HEADERS]
            )
            return

        header = records[0]
        if header[:7] != DISPLAY_HEADERS:
            raise ValueError(
                "Unexpected spreadsheet columns. "
                "Check the README before changing the sheet."
            )

        if len(header) < 8 or header[7] != "Timestamp":
            self.sheet.update(
                range_name="H1", values=[["Timestamp"]]
            )

    def indexed_rows(self):
        records = self.sheet.get_all_values()
        return [
            (index, row)
            for index, row in enumerate(records[1:], start=2)
            if len(row) >= 7 and row[0].strip()
        ]

    def find(self, booking_id):
        booking_id = str(booking_id or "").strip()
        for index, row in self.indexed_rows():
            if row[0] == booking_id:
                return index, row
        raise ValueError("Booking ID was not found.")

    def create(self, name, when, party_size, phone, notes):
        fields = validate_booking(
            name, when, party_size, phone, notes
        )
        existing = {row[0] for _, row in self.indexed_rows()}

        for _ in range(10):
            booking_id = "BK" + uuid.uuid4().hex[:12].upper()
            if booking_id not in existing:
                break
        else:
            raise RuntimeError("Unable to generate a unique ID.")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.sheet.append_row(
            [booking_id, *fields, timestamp],
            value_input_option="RAW",
        )
        return booking_id

    def update(self, booking_id, name, when, size, phone, notes):
        index, original = self.find(booking_id)
        fields = validate_booking(name, when, size, phone, notes)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update in place: never delete the original row first.
        self.sheet.update(
            range_name=f"A{index}:H{index}",
            values=[[original[0], *fields, timestamp]],
            value_input_option="RAW",
        )
        return original[0]

    def delete(self, booking_id):
        index, row = self.find(booking_id)
        self.sheet.delete_rows(index)
        return row[0]

    def load(self, booking_id):
        _, row = self.find(booking_id)
        date_time = datetime.strptime(
            f"{row[2]} {row[3]}", "%Y-%m-%d %I:%M %p"
        )
        return (
            row[1], date_time, int(row[4]), row[5], row[6]
        )

    def recent(self):
        rows = [row for _, row in self.indexed_rows()]
        rows.sort(
            key=lambda row: row[7] if len(row) > 7 else "",
            reverse=True,
        )
        return [row[:7] for row in rows]

    def by_date(self, selected):
        wanted = date_string(selected)
        return [
            row[:7]
            for _, row in self.indexed_rows()
            if row[2] == wanted
        ]
