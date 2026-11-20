"""Conference room and equipment scheduler."""
import itertools
import json
from datetime import datetime

# Global state
reservations = {}
equipment_pool = {"projector": 2, "microphone": 4, "webcam": 1}
conflicts = []
reservation_ids = itertools.count(1)


def parse_slot(time_slot):
    """Return (start, end) hours for a 'HH-HH' slot, or raise ValueError."""
    if not isinstance(time_slot, str) or time_slot.count("-") != 1:
        raise ValueError(f"Invalid time slot {time_slot!r}, expected 'HH-HH'")
    start, end = (int(part) for part in time_slot.split("-"))
    if not 0 <= start < end <= 24:
        raise ValueError(
            f"Invalid time slot {time_slot!r}, end must be after start")
    return start, end


def schedule_room(room_id, time_slot, equipment_list=None):
    """Book a room for a slot, allocating equipment; return reservation id."""
    equipment_list = list(equipment_list or [])
    parse_slot(time_slot)
    for item in equipment_list:
        if equipment_pool.get(item, 0) < 1:
            raise ValueError(f"Equipment {item!r} is not available")
    for booking in reservations.values():
        if booking["room"] == room_id and booking["slot"] == time_slot:
            conflicts.append(f"{room_id} double-booked at {time_slot}")
    for item in equipment_list:
        equipment_pool[item] -= 1
    reservation_id = next(reservation_ids)
    reservations[reservation_id] = {
        "room": room_id, "slot": time_slot, "equipment": equipment_list}
    return reservation_id


def cancel_reservation(reservation_id):
    """Cancel a reservation and return its equipment to the pool."""
    if reservation_id not in reservations:
        print("No reservation with id", reservation_id)
        return
    for item in reservations[reservation_id]["equipment"]:
        equipment_pool[item] += 1
    del reservations[reservation_id]


def slot_hours(time_slot):
    """Return the length of a slot in hours."""
    start, end = parse_slot(time_slot)
    return end - start


def export_schedule(file="schedule.json"):
    """Write all reservations to a JSON file."""
    with open(file, "w", encoding="utf-8") as out:
        out.write(json.dumps(reservations))


def log_conflicts(file="conflicts.log"):
    """Append conflicts to the log file and print the log."""
    with open(file, "a", encoding="utf-8") as log:
        for conflict in conflicts:
            log.write(str(datetime.now()) + " " + conflict + "\n")
    with open(file, encoding="utf-8") as log:
        print(log.read(), end="")


def main():
    """Run the demo scenario."""
    schedule_room("Board-1", "09-11")
    schedule_room("Board-1", "09-11")
    for room, slot in (("Huddle-3", "14-12"), ("Huddle-3", 1530)):
        try:
            schedule_room(room, slot)
        except ValueError as err:
            print("Rejected booking:", err)
    first = schedule_room("Huddle-3", "14-16")
    print("Slot length for first:", slot_hours(reservations[first]["slot"]))
    cancel_reservation(77)
    slot = input("Slot for Board-2, like 10-12 (Enter for 10-12): ") or "10-12"
    try:
        schedule_room("Board-2", slot, ["projector", "webcam"])
    except ValueError as err:
        print("Rejected booking:", err)
    export_schedule()
    log_conflicts()
    print("Equipment left:", equipment_pool)
    print("Reservations:", reservations)


if __name__ == "__main__":
    main()
