import re
from datetime import datetime

import pytest

from booking_manager import (
    BookingManager,
    HEADERS,
    parse_datetime,
    validate_booking,
)


class FakeWorksheet:
    def __init__(self):
        self.rows = []
        self.fail_updates = False

    def get_all_values(self):
        return [list(row) for row in self.rows]

    def update(self, range_name, values, **kwargs):
        if range_name == "A1:H1":
            if self.rows:
                self.rows[0] = list(values[0])
            else:
                self.rows.append(list(values[0]))
            return

        if range_name == "H1":
            self.rows[0] = self.rows[0][:7] + [values[0][0]]
            return

        if self.fail_updates:
            raise RuntimeError("Simulated Google Sheets failure")

        match = re.fullmatch(r"A(\d+):H\1", range_name)
        if not match:
            raise AssertionError("Unexpected update range")

        self.rows[int(match.group(1)) - 1] = list(values[0])

    def append_row(self, row, **kwargs):
        self.rows.append(list(row))

    def delete_rows(self, row_number):
        self.rows.pop(row_number - 1)


@pytest.fixture
def store():
    return BookingManager(FakeWorksheet())


def test_headers_initialised(store):
    assert store.sheet.rows[0] == HEADERS


def test_booking_minutes_are_preserved(store):
    booking_id = store.create(
        "Alex Example",
        datetime(2026, 11, 10, 18, 45),
        4,
        "0400000000",
        "Window seat",
    )
    row = store.find(booking_id)[1]
    assert row[3] == "06:45 PM"


def test_create_and_search(store):
    booking_id = store.create(
        "Alex Example", "2026-11-10T18:30",
        2, "0400000000", ""
    )
    assert store.find(booking_id)[1][1] == "Alex Example"
    assert len(store.by_date("2026-11-10")) == 1
    assert len(store.by_date("2026-11-11")) == 0


def test_update_keeps_original_row(store):
    booking_id = store.create(
        "Alex Example", "2026-11-10T18:30",
        2, "0400000000", ""
    )
    before = len(store.sheet.rows)

    store.update(
        booking_id, "Alex Updated",
        "2026-11-10T19:15", 3, "0400000000", ""
    )

    assert len(store.sheet.rows) == before
    assert store.find(booking_id)[1][1] == "Alex Updated"
    assert store.find(booking_id)[1][3] == "07:15 PM"


def test_failed_update_does_not_delete_original(store):
    booking_id = store.create(
        "Alex Example", "2026-11-10T18:30",
        2, "0400000000", ""
    )
    store.sheet.fail_updates = True

    with pytest.raises(RuntimeError):
        store.update(
            booking_id, "Changed",
            "2026-11-10T19:15", 3, "0400000000", ""
        )

    assert store.find(booking_id)[1][1] == "Alex Example"


def test_delete(store):
    booking_id = store.create(
        "Alex Example", "2026-11-10T18:30",
        2, "0400000000", ""
    )
    assert store.delete(booking_id) == booking_id

    with pytest.raises(ValueError):
        store.find(booking_id)


@pytest.mark.parametrize("size", [0, -1, 2.5, "abc", 101])
def test_invalid_party_size(size):
    with pytest.raises(ValueError):
        validate_booking(
            "Alex", "2026-11-10T18:30",
            size, "0400000000", ""
        )


def test_datetime_preserves_minutes():
    dt = parse_datetime("2026-11-10T18:37:59")
    assert (dt.hour, dt.minute, dt.second) == (18, 37, 0)
