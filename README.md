# Turkish Airlines 1M Miles Challenge Route & Flight Search Tool

## Overview

This project is a robust, multi-threaded tool for generating and analyzing all possible Turkish Airlines flight routes that visit all 6 continents, specifically designed for the [Turkish Airlines 1 Million Miles Challenge](https://www.turkishairlines.com/en-int/miles-and-smiles/campaigns/fly-across-6-continents-Earn-1-million-miles/). It was developed by extensively modifying and extending the [google-flights-scraper](https://github.com/hugoglvs/google-flights-scraper/) library to support advanced route generation, flight search, and robust, resumable execution.

---

## Features

### 1. **Comprehensive Route Generation**
- **All 6 Continents:** Generates all possible multi-continent routes, ensuring every route visits all 6 continents (Asia, Europe, Africa, North America, South America, Oceania).
- **Easy Visa Countries:** Only includes countries that are easy for Indian citizens to visit (visa-free, e-visa, or visa-on-arrival), maximizing practical feasibility.
- **Major Cities:** Uses major cities per country for realistic flight segment planning.

### 2. **Multi-Threaded, High-Performance Flight Search**
- **Parallel Processing:** Uses Python's `ThreadPoolExecutor` to search for flights on multiple routes in parallel, dramatically speeding up the search process.
- **Per-Thread Scrapers:** Each thread uses its own Google Flights scraper instance to avoid conflicts and maximize throughput.
- **Rate Limiting:** Configurable delay per thread to avoid being rate-limited by Google Flights.

### 3. **Turkish Airlines-Only Filtering & Early Termination**
- **Strict Airline Filter:** Only considers flights operated by Turkish Airlines (no codeshares), and only those routing via Istanbul (IST).
- **Early Termination:** As soon as any segment in a route cannot be flown with Turkish Airlines, the entire route is discarded immediately, saving time and resources.

### 4. **Resumable & Robust Execution**
- **Continuous Progress Saving:** Progress is saved after every route to `flight_search_progress.json` and results to `flight_search_results.json` using atomic file writes.
- **Crash/Interruption Recovery:** On restart, the tool loads previous progress and resumes from where it left off, skipping already-completed routes.
- **Thread-Safe File I/O:** All file operations are protected by locks to ensure data integrity in multi-threaded execution.

### 5. **Output & Reporting**
- **JSON Results:** All complete Turkish Airlines routes (with all segments valid) are saved in a structured JSON file, including route details, flight segments, and total cost.
- **Human-Readable Summaries:** The tool prints summaries of the best routes, progress statistics, and efficiency metrics to the console.
- **Efficiency Stats:** Reports on early termination savings, processing speed, and completion rates.

### 6. **Extensive Modifications & Improvements**
- **Full Combinatorial Route Coverage:** Implements `generate_all_possible_combinations` for exhaustive route generation.
- **Robust Error Handling:** Handles all exceptions gracefully, marking failed routes as processed to avoid infinite retries.
- **Atomic File Writes:** Ensures no data loss even if the process is killed or crashes.
- **Highly Configurable:** Thread count, rate limits, and batch sizes are easily adjustable for different hardware or dataset sizes.

---

## Usage

1. **Install Dependencies**
   - Clone this repo and install requirements (see `requirements.txt`).
   - Ensure you have Python 3.9+.

2. **Run the Tool**
   ```bash
   python3 comprehensive_flight_search.py
   ```
   - The tool will generate all valid routes and begin searching for Turkish Airlines flights for each segment.
   - Progress and results are saved continuously. You can safely interrupt and resume at any time.

3. **Review Results**
   - Results are saved in `flight_search_results.json` (all complete Turkish Airlines routes).
   - Progress is tracked in `flight_search_progress.json`.
   - Summaries and statistics are printed to the console after each run.

---

## File Structure

- `comprehensive_flight_search.py` — Main script for route generation, multi-threaded search, and reporting.
- `route_planner.py` — Route generation logic (all possible 6-continent combinations).
- `utils.py` — Country, city, and visa data utilities.
- `google_flights/google_flights.py` — Modified Google Flights scraper (airline filtering, robust error handling).
- `flight_search_progress.json` — Progress tracking (auto-generated).
- `flight_search_results.json` — Results (auto-generated).

---

## Key Modifications to google-flights-scraper
- **Thread Safety:** Refactored to allow multiple concurrent scraper instances.
- **Airline Filtering:** Added strict Turkish Airlines-only and IST routing filters.
- **Robust Error Handling:** Improved handling of missing data, timeouts, and Google Flights quirks.
- **Atomic File Writes:** Ensured all progress/results are saved safely in multi-threaded environments.

---

## Example Output

- **Top 5 Cheapest Complete Turkish Airlines Routes:**
  - Printed to console after each run, showing total cost, route, and flight segment details.
- **JSON Results:**
  - Each result includes route, all flight segments, total cost, and status.

---

## How to Extend or Modify
- **Change Visa Rules:** Edit `utils.py` to update which countries are considered "easy visa".
- **Adjust Threading/Performance:** Change `max_workers` and `rate_limit_delay` in `comprehensive_flight_search.py`.
- **Add More Cities:** Update `COUNTRY_MAJOR_CITIES` in `utils.py`.

---

## Credits
- **Original Scraper:** [hugoglvs/google-flights-scraper](https://github.com/hugoglvs/google-flights-scraper)
- **Project Author:** Custom modifications and tool by [Amsal1](https://github.com/Amsal1)

---

## License
This project is for educational and research purposes. Please respect the terms of service of Google Flights and Turkish Airlines. Not affiliated with Turkish Airlines or Google.
