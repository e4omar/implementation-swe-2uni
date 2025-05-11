# ───────────── reservation_controller.py ─────────────

from datetime import datetime
import backend.database_access as db

def book_slot(user_id, slot_id, table_number):
    slots = db.get_available_slots()
    if not any(s[0] == slot_id for s in slots):
        return "❌ Slot not available."
    now = datetime.now().isoformat()
    db.insert_reservation(user_id, slot_id, now, table_number)
    db.update_slot_status(slot_id, "Booked")
    db.log_notification(user_id, None, "Your reservation is confirmed.")
    return "✅ Reservation confirmed."

def get_all_reservations():
    return db.get_all_reservations()

def modify_reservation(reservation_id, new_slot_id, new_table):
    slots = db.get_available_slots()
    if not any(s[0] == new_slot_id for s in slots):
        return "❌ New slot not available."
    db.update_reservation(reservation_id, new_slot_id, new_table)
    db.update_slot_status(new_slot_id, "Booked")
    return "✅ Reservation updated."

def update_slot_details(slot_id, start_time, end_time, status):
    db.edit_slot(slot_id, start_time, end_time, status)
    return "✅ Slot updated."

def get_available_slots():
    return db.get_available_slots()
