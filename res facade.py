# reservation_facade.py
# Interface between the GUI and reservation controller logicc

import backend.reservation_controller as controller

def book_slot_for_customer(user_id, slot_id, table_number):
    return controller.book_slot(user_id, slot_id, table_number)

def view_all_reservations():
    return controller.get_all_reservations()

def modify_existing_reservation(reservation_id, new_slot_id, new_table_number):
    return controller.modify_reservation(reservation_id, new_slot_id, new_table_number)

def edit_existing_slot(slot_id, new_start, new_end, new_status):
    return controller.update_slot_details(slot_id, new_start, new_end, new_status)

def list_available_slots():
    return controller.get_available_slots()
