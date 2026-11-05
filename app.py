import logging
import os
from datetime import datetime

import gradio as gr
import gspread
from dotenv import load_dotenv

from booking_manager import BookingManager, DISPLAY_HEADERS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def connect():
    load_dotenv()
    credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    sheet_id = os.getenv("GOOGLE_SHEET_ID")

    if not credentials or not sheet_id:
        raise RuntimeError(
            "Set GOOGLE_APPLICATION_CREDENTIALS and "
            "GOOGLE_SHEET_ID in your environment."
        )

    client = gspread.service_account(filename=credentials)
    worksheet = client.open_by_key(sheet_id).sheet1
    return BookingManager(worksheet)


def build_app(manager):
    def error_message(exc):
        if isinstance(exc, ValueError):
            return f"**Input error:** {exc}"
        logger.exception("Booking operation failed")
        return "**Error:** Operation failed. Check the server logs."

    def create(name, when, size, phone, notes):
        try:
            booking_id = manager.create(
                name, when, size, phone, notes
            )
            return (
                f"Booking saved. ID: `{booking_id}`",
                manager.recent(),
            )
        except Exception as exc:
            return error_message(exc), []

    def load(booking_id):
        try:
            values = manager.load(booking_id)
            return ("Booking loaded for editing.", *values)
        except Exception as exc:
            return (
                error_message(exc),
                "", datetime.now(), 1, "", "",
            )

    def save(booking_id, name, when, size, phone, notes):
        try:
            updated = manager.update(
                booking_id, name, when, size, phone, notes
            )
            return (
                f"Booking `{updated}` updated.",
                manager.recent(),
            )
        except Exception as exc:
            return error_message(exc), []

    def remove(booking_id, confirmed):
        if not confirmed:
            return (
                "Select the deletion confirmation checkbox first.",
                manager.recent(),
                False,
            )

        try:
            deleted = manager.delete(booking_id)
            return (
                f"Booking `{deleted}` deleted.",
                manager.recent(),
                False,
            )
        except Exception as exc:
            return error_message(exc), [], False

    def refresh():
        try:
            return "Bookings refreshed.", manager.recent()
        except Exception as exc:
            return error_message(exc), []

    def search(selected):
        try:
            return "Date search complete.", manager.by_date(selected)
        except Exception as exc:
            return error_message(exc), []

    with gr.Blocks(
        title="Restaurant Booking Manager"
    ) as demo:
        gr.Markdown("# Restaurant Booking Manager")
        gr.Markdown(
            "Create, search, edit and delete restaurant bookings. "
            "Records are stored in Google Sheets."
        )

        status = gr.Markdown()

        with gr.Row():
            with gr.Column():
                name = gr.Textbox(label="Customer name")
                when = gr.DateTime(
                    label="Booking date and time",
                    type="datetime",
                    value=datetime.now(),
                )
                size = gr.Number(
                    label="Party size",
                    value=2,
                    precision=0,
                )
                phone = gr.Textbox(label="Phone number")
                notes = gr.Textbox(
                    label="Notes",
                    lines=3,
                )

                create_button = gr.Button(
                    "Create booking", variant="primary"
                )

                gr.Markdown("### Manage an existing booking")
                booking_id = gr.Textbox(
                    label="Booking ID",
                    placeholder="BK...",
                )

                with gr.Row():
                    load_button = gr.Button("Load booking")
                    save_button = gr.Button("Save changes")

                confirm_delete = gr.Checkbox(
                    label="I confirm I want to delete this booking"
                )
                delete_button = gr.Button("Delete booking")

            with gr.Column():
                recent = gr.Dataframe(
                    headers=DISPLAY_HEADERS,
                    value=manager.recent(),
                    type="array",
                    interactive=False,
                    label="Recent bookings",
                )
                refresh_button = gr.Button("Refresh bookings")

                gr.Markdown("### Search by date")
                search_date = gr.DateTime(
                    label="Booking date",
                    type="datetime",
                    value=datetime.now(),
                )
                search_button = gr.Button("Find bookings")
                results = gr.Dataframe(
                    headers=DISPLAY_HEADERS,
                    value=[],
                    type="array",
                    interactive=False,
                    label="Bookings on selected date",
                )

        form_fields = [name, when, size, phone, notes]

        create_button.click(
            create,
            inputs=form_fields,
            outputs=[status, recent],
        )
        load_button.click(
            load,
            inputs=[booking_id],
            outputs=[status, *form_fields],
        )
        save_button.click(
            save,
            inputs=[booking_id, *form_fields],
            outputs=[status, recent],
        )
        delete_button.click(
            remove,
            inputs=[booking_id, confirm_delete],
            outputs=[status, recent, confirm_delete],
        )
        refresh_button.click(
            refresh,
            outputs=[status, recent],
        )
        search_button.click(
            search,
            inputs=[search_date],
            outputs=[status, results],
        )

    return demo


if __name__ == "__main__":
    manager = connect()
    demo = build_app(manager)
    demo.launch(server_name="127.0.0.1", share=False)
