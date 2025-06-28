"""
Patched google_flights.py to:
- Use English selectors
- Target INR currency
- Add airline_filter to extract only Turkish Airlines results
- Headless optional via init param
"""

from playwright.sync_api import sync_playwright
from selectolax.lexbor import LexborHTMLParser
import time

class GoogleFlights:
    def __init__(self, headless=True, airline_filter=None):
        self.headless = headless
        self.airline_filter = airline_filter

    def _extract(self, origin, destination, departure_date, passengers=1):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless, slow_mo=100)
            page = browser.new_page()

            try:
                page.goto("https://www.google.com/travel/flights?hl=en&curr=INR")

                # Accept cookies
                try:
                    page.get_by_text("Accept all").click(timeout=5000)
                except:
                    pass  # cookie popup might not show

                # One-way trip
                page.get_by_role("combobox", name="Change ticket type.").click()
                time.sleep(0.4)
                page.get_by_role("option", name="One way").click()

                # Passengers
                # page.get_by_label("1 passenger").click()
                # page.get_by_label("Add adult").click(click_count=passengers - 1)

                # Origin
                page.get_by_label("Where from?").click()
                page.keyboard.insert_text(origin)
                # page.type("input[aria-label^='Where']", origin, delay=1000)
                page.wait_for_selector("span.yPKHsc", timeout=5000)
                page.keyboard.press("ArrowDown")
                page.keyboard.press("Enter")
                time.sleep(1)

                # page.fill("input[aria-label='Where else?']", origin)
                # page.keyboard.press("Enter")
                # page.get_by_label("Where else?").fill(origin)
                # page.get_by_label("Where else?").press("Enter")

                # Destination
                page.get_by_role("combobox", name="Where to?").click()
                page.get_by_role("combobox", name="Where to?").fill(destination)
                page.get_by_role("combobox", name="Where to?").press("Enter")
                time.sleep(0.5)

                # Date
                page.get_by_role("textbox", name="Departure").click()
                page.get_by_role("textbox", name="Departure").fill(departure_date)
                page.get_by_role("textbox", name="Departure").press("Enter")
                formatted_date = "October 3, 2025"
                time.sleep(0.7)
                # page.click("div:has-text('one way price')")
                aria_label = f"Done. Search for one-way flights, departing on {formatted_date}"

                # Wait and click the correct Done button
                page.get_by_role("button", name=aria_label).wait_for(state="visible", timeout=5000)
                page.get_by_role("button", name=aria_label).click()
                # page.get_by_role("textbox", name="Departure").press("Done")
                time.sleep(0.7)

                # Search
                # page.get_by_label("OK. Search one-way").click()
                page.get_by_label("Search", exact=True).click()
                time.sleep(3)

                # Select Airlines
                if self.airline_filter:
                    # Open filters
                    page.get_by_role("button", name="Airlines, Not selected").click()
                    time.sleep(0.7)

                    page.get_by_role("button", name=self.airline_filter).click()
                    time.sleep(0.7)
                    page.get_by_role("button", name=self.airline_filter + ' only').press("Enter")
                    time.sleep(0.7)
                

                results_selector = ".pIav2d"
                page.wait_for_selector(results_selector, state="visible", timeout=5000)

                # Scroll and load all flight results
                print("🔍 Scrolling to load more flight results...")
                for _ in range(15):  # Adjust range for deeper pagination
                    try:
                        # Scroll down
                        page.mouse.wheel(0, 1000)
                        time.sleep(1)

                        # Click "View more flights" if visible
                        view_more_button = page.locator("button[aria-label='View more flights']").first
                        if view_more_button.is_visible():
                            print("🔄 Clicking 'View more flights' to load more results...")
                            view_more_button.click()
                            time.sleep(3)
                    except Exception as e:
                        print(f"⚠️  Scroll/View More Exception: {e}")
                        continue

                # Wait for any remaining JS rendering
                time.sleep(3)

                # Return hydrated HTML
                return page.content()

            except Exception as e:
                print("Error during scraping:", e)
                return None
            finally:
                browser.close()

    def _parse(self, html):
        return LexborHTMLParser(html)

    def _process(self, parser):
        data = {}
        categories = [parser.root.css_first('.zBTtmb')]
        category_results = [parser.root.css_first('.Rk10dc')]

        for category, category_result in zip(categories, category_results):
            category_data = []
            for result in category_result.css('.pIav2d'):
                main = result.css_first('.yR1fYc')
                if not main or not main.css_first('.PTuQse.sSHqwe.tPgKwe.ogfYpf'):
                    continue

                airline = main.css_first('.Ir0Voe .sSHqwe').text()
                if self.airline_filter and self.airline_filter.lower() not in airline.lower():
                    continue

                times = main.css('[jscontroller="cNtv4b"] span')
                departure_time = times[0].text() if times else None
                arrival_time = times[1].text() if times and len(times) > 1 else None
                duration = main.css_first('.AdWm1c.gvkrdb').text()
                stops = main.css_first('.EfT7Ae .ogfYpf').text()
                emissions = main.css_first('.V1iAHe .AdWm1c').text()
                emission_comparison = (main.css_first('.N6PNV').text() if main.css_first('.N6PNV') else None)
                price = main.css_first('.U3gSDe .FpEdX span').text()
                price_type = (main.css_first('.U3gSDe .N872Rd').text() if main.css_first('.U3gSDe .N872Rd') else None)

                airports_raw = main.css_first('.PTuQse.sSHqwe.tPgKwe.ogfYpf').css(".QylvBf")
                departure_airport = airports_raw[0].text()[:3]
                arrival_airport = airports_raw[-1].text()[:3]
                route = [departure_airport, arrival_airport]

                if stops != "Nonstop":
                    stop_airports = main.css('.BbR8Ec > .sSHqwe.tPgKwe.ogfYpf > span')
                    if stop_airports:
                        route[1:1] = [s.text()[:3] for s in stop_airports]

                flight_data = {
                    'departure_time': departure_time,
                    'arrival_time': arrival_time,
                    'airline': airline,
                    'duration': duration,
                    'stops': stops,
                    'emissions': emissions,
                    'emission_comparison': emission_comparison,
                    'price': price,
                    'price_type': price_type,
                    'route': route
                }

                category_data.append(flight_data)
            if category:
                data[category.text().lower().replace(' ', '_')] = category_data
        return data

    def search(self, origin, destination, departure_date, passengers=1):
        html = self._extract(origin, destination, departure_date, passengers)
        if not html:
            return {}
        parser = self._parse(html)
        return self._process(parser)