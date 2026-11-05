# Security Notes

## Credentials

Never store Google service-account JSON keys in this
repository or commit them to Git history.

Use GOOGLE_APPLICATION_CREDENTIALS to point to a
private file outside the repository.

Any previously exposed key must be revoked, not merely
deleted from a local folder.

## Customer data

Bookings can contain names, phone numbers and notes.

Do not publish real booking records, spreadsheets,
screenshots or exported data.

## Deployment

This project is intended for local demonstration only.

It does not implement authentication, role-based
authorisation or multi-user concurrency controls.

Do not expose this application to the public internet
without an appropriate security review and additional
access controls.
