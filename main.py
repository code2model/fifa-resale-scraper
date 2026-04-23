import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

OUTPUT_FILE = "availability_output.json"


async def main():
    print("Connecting to existing Chrome...")

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")

        context = browser.contexts[0]
        page = context.pages[0]

        print("Attached to browser successfully")

        captured_data = None

        async def handle_response(response):
            nonlocal captured_data
            try:
                if "availability" in response.url and response.status == 200:
                    data = await response.json()
                    captured_data = data
                    print("Captured availability API")
            except:
                pass

        page.on("response", handle_response)

        print("Refreshing page to trigger API...")

        # Trigger reload but don't wait for full load
        await page.reload(wait_until="domcontentloaded")

        # small wait to capture API
        await page.wait_for_timeout(10000)

        # extra safety
        await page.mouse.move(400, 400)
        await page.wait_for_timeout(3000)

        if not captured_data:
            print(" No data captured. Try refreshing page manually.")
            return

        # Parse
        results = []

        categories = captured_data.get("priceRangeCategories", [])

        for cat in categories:
            category_name = cat.get("name")
            min_price = cat.get("minPrice")
            max_price = cat.get("maxPrice")

            blocks = cat.get("blocks", [])

            for block in blocks:
                results.append({
                    "category": category_name,
                    "block": block,
                    "min_price": min_price,
                    "max_price": max_price
                })

        output = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_blocks": len(results),
            "data": results
        }

        with open(OUTPUT_FILE, "w") as f:
            json.dump(output, f, indent=2)

        print(f"Saved {len(results)} records")


if __name__ == "__main__":
    asyncio.run(main())


