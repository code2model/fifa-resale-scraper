import json
from pathlib import Path
from datetime import datetime, timezone

INPUT_DIR = Path("D:\\Fifa\\input_json")   # put your 6 json files here
OUTPUT_FILE = Path("all_final_matches.json")




def normalize_seat(seat: dict) -> dict:
    """
    Keep only the fields needed for Supabase.
    """
    usd = seat.get("usd")
    price = seat.get("price")

    # If price is missing but usd exists, derive price in millicents
    if price is None and usd is not None:
        try:
            price = int(float(usd) * 1000)
        except Exception:
            price = None

    return {
        "seatId": seat.get("seatId"),
        "block": seat.get("block"),
        "row": seat.get("row"),
        "seat": seat.get("seat"),
        "category": seat.get("category"),
        "price": price,
        "usd": usd,
        "resaleMovementId": seat.get("resaleMovementId"),
        "exclusive": seat.get("exclusive"),
    }


def normalize_record(data: dict) -> dict:
    """
    Convert one raw JSON file into final Supabase-ready structure.
    Removes extra keys like layer1, cart_tickets, selected_seat_html, etc.
    """
    # Choose the best seat source available
    raw_seats = (
        data.get("seats")
        or data.get("cart_tickets")
        or []
    )

    final_seats = []

    if isinstance(raw_seats, list):
        for seat in raw_seats:
            if isinstance(seat, dict):
                final_seats.append(normalize_seat(seat))

    # If the file has a single seat dict in selected_seat_html, convert it too
    selected = data.get("selected_seat_html")
    if not final_seats and isinstance(selected, dict):
        final_seats.append(
            {
                "seatId": selected.get("seatId"),
                "block": selected.get("block"),
                "row": selected.get("row"),
                "seat": selected.get("seat"),
                "category": selected.get("category"),
                "price": selected.get("price"),
                "usd": selected.get("usd"),
                "resaleMovementId": selected.get("resaleMovementId"),
                "exclusive": selected.get("exclusive"),
            }
        )

    # seat_count should match actual seats if available
    seat_count = data.get("seat_count")
    if seat_count is None:
        seat_count = len(final_seats)

    return {
        "created_at": data.get("created_at") or datetime.now(timezone.utc).isoformat(),
        "license_hash": data.get("license_hash", "personal"),
        "match_code": data.get("match_code"),
        "home": data.get("home"),
        "away": data.get("away"),
        "performance_id": data.get("performance_id"),
        "seat_count": seat_count,
        "seats": final_seats,
    }


def main():
    combined = []

    for file_path in sorted(INPUT_DIR.glob("*.json")):
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # If the file itself is a list, normalize each item
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    combined.append(normalize_record(item))
        elif isinstance(data, dict):
            combined.append(normalize_record(data))

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            combined,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"Saved {len(combined)} final match records to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()