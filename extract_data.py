import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

OUTPUT_FILE = Path("poc_output_with_cart_4.json")
LICENSE_HASH = "personal"


def normalize_text(value):
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def extract_match_code(text):
    m = re.search(r"MATCH\s+(\d+)", text, re.IGNORECASE)
    return f"M{m.group(1)}" if m else None


def extract_performance_id(url):
    m = re.search(r"/performance/(\d+)", url)
    return m.group(1) if m else None


def value_en(value):
    if isinstance(value, dict):
        return value.get("en") or next(iter(value.values()), None)
    return value


def parse_availability(data):
    results = []
    block_map = {}

    for item in data.get("areaBlocksAvailability", []):
        block_id = item.get("blockId") or item.get("id")
        if block_id:
            block_map[str(block_id)] = item.get("availabilityResale", 0)

    for cat in data.get("priceRangeCategories", []):
        category_name = value_en(cat.get("name"))
        min_price = cat.get("minPrice")
        max_price = cat.get("maxPrice")

        for block in cat.get("blocks", []):
            if isinstance(block, dict):
                block_id = str(block.get("id"))
                block_name = value_en(block.get("name"))
            else:
                block_id = str(block)
                block_name = str(block)

            results.append({
                "category": category_name,
                "block": block_name,
                "availability_resale": block_map.get(block_id, 0),
                "min_price": min_price,
                "max_price": max_price
            })

    return results


async def main():
    print("Connecting to Chrome...")

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]

        # Attach to FIFA tab
        page = None
        for tab in context.pages:
            if "fifa.com" in tab.url:
                page = tab
                break

        if not page:
            print(" Open FIFA page first")
            return

        print("Connected:", page.url)

        captured_data = None

        async def handle_response(response):
            nonlocal captured_data
            try:
                if "availability" in response.url and response.status == 200:
                    captured_data = await response.json()
                    print("API Captured")
            except:
                pass

        page.on("response", handle_response)

        # Trigger API
        await page.reload(wait_until="domcontentloaded")
        await page.wait_for_timeout(8000)

        if not captured_data:
            print("⚠️ Click UI once manually")
            await page.wait_for_timeout(8000)

        if not captured_data:
            print("API not captured")
            return

        # -------------------------
        # MATCH METADATA
        # -------------------------
        body_text = normalize_text(await page.locator("body").inner_text())

        match_code = extract_match_code(body_text)
        performance_id = extract_performance_id(page.url)

        home = ""
        away = ""

        if await page.locator(".team.host").count():
            home = normalize_text(await page.locator(".team.host").inner_text())

        if await page.locator(".team.opposing").count():
            away = normalize_text(await page.locator(".team.opposing").inner_text())

        # -------------------------
        # LAYER 1 DATA
        # -------------------------
        layer1_rows = parse_availability(captured_data)

        # -------------------------
        # CART EXTRACTION (MAIN FIX)
        # -------------------------
        cart_tickets = []

        # Open cart panel if needed
        try:
            await page.locator("text=Ticket(s) selected").click(timeout=2000)
            await page.wait_for_timeout(1000)
        except:
            pass

        # IMPORTANT: adjust selector if needed after inspect
        cart_items = page.locator(".stx-sm-SeatDetails-Details")

        count = await cart_items.count()
        print(f"🧾 Found {count} ticket elements")

        for i in range(count):
            try:
                text = normalize_text(await cart_items.nth(i).inner_text())

                block = re.search(r"Block\s+(\S+)", text)
                row = re.search(r"Row\s+(\S+)", text)
                seat = re.search(r"Seat\s+(\S+)", text)
                category = re.search(r"(Front Category \d|Category \d|Technical|VIP)", text)
                price = re.search(r"([\d,]+\.\d+)\s+USD", text)

                cart_tickets.append({
                    "block": block.group(1) if block else None,
                    "row": row.group(1) if row else None,
                    "seat": seat.group(1) if seat else None,
                    "category": category.group(1) if category else None,
                    "usd": float(price.group(1).replace(",", "")) if price else None,
                    "seatId": None,
                    "resaleMovementId": None,
                    "exclusive": None,
                    "raw": text
                })

            except Exception:
                continue

        # -------------------------
        # FINAL OUTPUT
        # -------------------------
        output = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "license_hash": LICENSE_HASH,
            "match_code": match_code,
            "home": home,
            "away": away,
            "performance_id": performance_id,
            "seat_count": len(cart_tickets),
            "layer1": layer1_rows,
            "cart_tickets": cart_tickets
        }

        with open(OUTPUT_FILE, "w") as f:
            json.dump(output, f, indent=2)

        print(" SUCCESS - Cart data captured")


if __name__ == "__main__":
    asyncio.run(main())