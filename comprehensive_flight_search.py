#!/usr/bin/env python3
"""
Comprehensive Turkish Airlines 1M Miles Challenge Flight Search

This script:
1. Generates optimal routes visiting all 6 continents
2. Searches for Turkish Airlines flights for each route segment
3. Calculates total costs and finds the cheapest itineraries
4. Prioritizes easy visa countries for Indian citizens
"""

import json
import time
import sys
import threading
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from google_flights.google_flights import GoogleFlights
from route_planner import generate_all_possible_combinations, print_route_summary
from utils import COUNTRY_MAJOR_CITIES

class TurkishAirlinesOptimizer:
    def __init__(self, headless=True, max_routes_to_search=20, max_workers=4, rate_limit_delay=2, 
                 progress_file="flight_search_progress.json", results_file="flight_search_results.json"):
        self.max_routes_to_search = max_routes_to_search
        self.max_workers = max_workers  # Number of concurrent threads
        self.rate_limit_delay = rate_limit_delay  # Delay between requests per thread
        self.progress_file = progress_file  # File to track completed routes
        self.results_file = results_file   # File to store all results
        self.results = {}
        self.results_lock = threading.Lock()  # Thread-safe results collection
        self.progress_lock = threading.Lock()  # Thread-safe progress tracking
        self.file_lock = threading.Lock()     # Thread-safe file operations
        self.completed_count = 0
        self.failed_count = 0
        self.completed_routes = set()  # Track completed route signatures
        
        # Load existing progress on startup
        self.load_existing_progress()
        
        # Note: We'll create GoogleFlights instances per thread to avoid conflicts
        
    def city_to_airport_code(self, city, country_code):
        """Convert city name to likely airport code for Google Flights"""
        # Common airport mappings based on utils.py cities
        airport_mapping = {
            # Asia
            "Delhi": "DEL",
            "Mumbai": "BOM", 
            "Hyderabad": "HYD",
            "Bangalore": "BLR",
            "Dubai": "DXB",
            "Abu Dhabi": "AUH",
            "Singapore": "SIN",
            "Bangkok": "BKK",
            "Phuket": "HKT",
            "Istanbul": "IST",
            "Ankara": "ESB",
            "Jakarta": "CGK",
            "Bali": "DPS",
            "Doha": "DOH",
            "Kuala Lumpur": "KUL",
            "Dhaka": "DAC",
            "Colombo": "CMB",
            "Male": "MLE",
            "Beijing": "PEK",
            "Shanghai": "PVG",
            "Tokyo": "NRT",
            "Osaka": "KIX",
            "Seoul": "ICN",
            "Manila": "MNL",
            "Ho Chi Minh City": "SGN",
            "Hanoi": "HAN",
            "Riyadh": "RUH",
            "Jeddah": "JED",
            "Kuwait City": "KWI",
            "Manama": "BAH",
            "Muscat": "MCT",
            "Beirut": "BEY",
            "Kabul": "KBL",
            "Almaty": "ALA",
            "Tashkent": "TAS",
            "Bishkek": "FRU",
            "Ashgabat": "ASB",
            "Ulaanbaatar": "ULN",
            "Kathmandu": "KTM",
            
            # Europe
            "Frankfurt": "FRA",
            "Munich": "MUC",
            "Berlin": "BER",
            "Paris": "CDG",
            "Lyon": "LYS",
            "Amsterdam": "AMS",
            "Rome": "FCO",
            "Milan": "MXP",
            "Madrid": "MAD",
            "Barcelona": "BCN",
            "London": "LHR",
            "Manchester": "MAN",
            "Moscow": "SVO",
            "Saint Petersburg": "LED",
            "Vienna": "VIE",
            "Brussels": "BRU",
            "Zurich": "ZUR",
            "Geneva": "GVA",
            "Stockholm": "ARN",
            "Oslo": "OSL",
            "Copenhagen": "CPH",
            "Helsinki": "HEL",
            "Warsaw": "WAW",
            "Krakow": "KRK",
            "Prague": "PRG",
            "Budapest": "BUD",
            "Athens": "ATH",
            "Lisbon": "LIS",
            "Bucharest": "OTP",
            "Sofia": "SOF",
            "Zagreb": "ZAG",
            "Belgrade": "BEG",
            "Sarajevo": "SJJ",
            "Podgorica": "TGD",
            "Ljubljana": "LJU",
            "Skopje": "SKP",
            "Baku": "GYD",
            "Tbilisi": "TBS",
            "Chisinau": "KIV",
            "Tallinn": "TLL",
            "Riga": "RIX",
            "Vilnius": "VNO",
            "Luxembourg": "LUX",
            "Valletta": "MLA",
            "Dublin": "DUB",
            
            # Africa
            "Cairo": "CAI",
            "Alexandria": "HBE",
            "Nairobi": "NBO",
            "Johannesburg": "JNB",
            "Cape Town": "CPT",
            "Casablanca": "CMN",
            "Marrakech": "RAK",
            "Tunis": "TUN",
            "Algiers": "ALG",
            "Tripoli": "TIP",
            "Addis Ababa": "ADD",
            "Accra": "ACC",
            "Lagos": "LOS",
            "Abuja": "ABV",
            "Dakar": "DKR",
            "Abidjan": "ABJ",
            "Douala": "DLA",
            "Kinshasa": "FIH",
            "Luanda": "LAD",
            "Kampala": "EBB",
            "Dar es Salaam": "DAR",
            "Kigali": "KGL",
            "Port Louis": "MRU",
            "Antananarivo": "TNR",
            
            # North America
            "New York": "JFK",
            "Los Angeles": "LAX",
            "Chicago": "ORD",
            "Miami": "MIA",
            "San Francisco": "SFO",
            "Washington DC": "DCA",
            "Seattle": "SEA",
            "Boston": "BOS",
            "Toronto": "YYZ",
            "Montreal": "YUL",
            "Vancouver": "YVR",
            "Mexico City": "MEX",
            "Cancun": "CUN",
            "Havana": "HAV",
            "Panama City": "PTY",
            
            # South America
            "Sao Paulo": "GRU",
            "Rio de Janeiro": "GIG",
            "Buenos Aires": "EZE",
            "Bogota": "BOG",
            "Medellin": "MDE",
            "Santiago": "SCL",
            "Caracas": "CCS",
            
            # Oceania
            "Melbourne": "MEL",
            "Sydney": "SYD",
            "Perth": "PER",
        }
        
        return airport_mapping.get(city, city[:3].upper())
    
    def route_to_signature(self, route):
        """Convert route to a unique signature for tracking completion"""
        return tuple(sorted([(stop["city"], stop["country_code"], stop["continent"]) for stop in route]))
    
    def load_existing_progress(self):
        """Load existing progress from JSON files"""
        completed_count = 0
        
        # Load progress tracking file
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                    self.completed_routes = set(tuple(sig) for sig in progress_data.get('completed_routes', []))
                    completed_count = len(self.completed_routes)
                    print(f"📂 Loaded existing progress: {completed_count} routes already completed")
            except Exception as e:
                print(f"⚠️  Error loading progress file: {e}")
                self.completed_routes = set()
        
        # Load existing results file to get current results
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    existing_results = json.load(f)
                    print(f"📂 Found existing results file with {len(existing_results)} results")
            except Exception as e:
                print(f"⚠️  Error loading results file: {e}")
        
        if completed_count > 0:
            print(f"🔄 Resume mode: Will skip {completed_count} already completed routes")
    
    def save_progress(self, route_signature):
        """Save progress after completing a route (thread-safe)"""
        with self.file_lock:
            try:
                self.completed_routes.add(route_signature)
                
                # Save progress tracking
                progress_data = {
                    'completed_routes': list(self.completed_routes),
                    'last_updated': datetime.now().isoformat(),
                    'total_completed': len(self.completed_routes)
                }
                
                with open(self.progress_file, 'w', encoding='utf-8') as f:
                    json.dump(progress_data, f, indent=2, ensure_ascii=False)
                
            except Exception as e:
                print(f"⚠️  Error saving progress: {e}")
    
    def save_result_to_file(self, result):
        """Save individual result to results file immediately (thread-safe)"""
        with self.file_lock:
            try:
                # Load existing results
                existing_results = []
                if os.path.exists(self.results_file):
                    try:
                        with open(self.results_file, 'r', encoding='utf-8') as f:
                            existing_results = json.load(f)
                    except:
                        existing_results = []
                
                # Add new result
                existing_results.append(result)
                
                # Sort by cost and save
                existing_results.sort(key=lambda x: x.get("total_cost_inr", 999999))
                
                with open(self.results_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_results, f, indent=2, ensure_ascii=False)
                
            except Exception as e:
                print(f"⚠️  Error saving result: {e}")
    
    def is_route_completed(self, route):
        """Check if a route has already been completed"""
        route_signature = self.route_to_signature(route)
        return route_signature in self.completed_routes
    
    def create_scraper(self, headless=True):
        """Create a new GoogleFlights instance for thread-local use"""
        return GoogleFlights(headless=headless, airline_filter="Turkish Airlines")
    
    def update_progress(self, success=True, discarded=False):
        """Thread-safe progress tracking with early termination stats"""
        with self.progress_lock:
            if success:
                self.completed_count += 1
            elif discarded:
                if not hasattr(self, 'discarded_count'):
                    self.discarded_count = 0
                self.discarded_count += 1
            else:
                self.failed_count += 1
            
            total_processed = self.completed_count + getattr(self, 'discarded_count', 0) + self.failed_count
            if total_processed % 10 == 0 or total_processed <= 20:  # Log every 10 routes or first 20
                discarded_info = f", {getattr(self, 'discarded_count', 0)} discarded" if hasattr(self, 'discarded_count') else ""
                print(f"📊 Progress: {self.completed_count} completed, {self.failed_count} failed{discarded_info}, {total_processed}/{self.max_routes_to_search} total")
    
    def search_route_flights(self, route, scraper, route_index, departure_date="Fri, Oct 3"):
        """Search for flights for each segment of a route (thread-safe version with early termination)"""
        route_flights = []
        total_cost = 0
        
        thread_id = threading.current_thread().name
        print(f"\n🔍 [{thread_id}] Route #{route_index}: Searching flights for route:")
        for i, stop in enumerate(route):
            print(f"  {i+1}. {stop['city']}, {stop['country_code']} ({stop['continent']})")
        
        try:
            # Search for flights between consecutive cities
            for i in range(len(route) - 1):
                origin_city = route[i]['city']
                origin_code = self.city_to_airport_code(origin_city, route[i]['country_code'])
                
                dest_city = route[i + 1]['city']
                dest_code = self.city_to_airport_code(dest_city, route[i + 1]['country_code'])
                
                print(f"  [{thread_id}] 🛫 Searching: {origin_city} ({origin_code}) → {dest_city} ({dest_code})")
                
                try:
                    # Search for flights
                    flight_results = scraper.search(
                        origin_code, dest_code, departure_date, passengers=1
                    )
                    
                    # Get cheapest flight from all available categories
                    all_flights = []
                    
                    # Check both top_flights and all_flights keys
                    for key in ["top_flights", "all_flights"]:
                        flights = flight_results.get(key, [])
                        if flights:
                            all_flights.extend(flights)
                    
                    # If no flights in common keys, check all keys in the response
                    if not all_flights:
                        for key, value in flight_results.items():
                            if isinstance(value, list) and value:
                                all_flights.extend(value)
                    
                    if all_flights:
                        # Filter flights to only include Turkish Airlines operated flights with IST route
                        valid_flights = self.filter_turkish_airlines_flights(all_flights, thread_id)
                        
                        if valid_flights:
                            cheapest = min(valid_flights, key=lambda x: self.parse_price(x.get("price", "₹999,999")))
                            route_flights.append({
                                "segment": f"{origin_city} → {dest_city}",
                                "origin": origin_code,
                                "destination": dest_code,
                                "flight": cheapest
                            })
                            
                            price = self.parse_price(cheapest.get("price", "₹0"))
                            total_cost += price
                            print(f"    [{thread_id}] ✅ Found {len(valid_flights)} valid Turkish Airlines flights, cheapest: {cheapest.get('price', 'N/A')}")
                        else:
                            print(f"    [{thread_id}] ❌ No valid Turkish Airlines flights found for segment {i+1}/{len(route)-1}")
                            print(f"    [{thread_id}] 🚫 EARLY TERMINATION: Route discarded due to missing Turkish Airlines flight")
                            # Mark route as processed but invalid - save to avoid re-processing
                            route_signature = self.route_to_signature(route)
                            self.save_progress(route_signature)
                            return None  # Early termination - route is useless
                    else:
                        print(f"    [{thread_id}] ❌ No flights found for segment {i+1}/{len(route)-1}")
                        print(f"    [{thread_id}] 🚫 EARLY TERMINATION: Route discarded due to no flights available")
                        # Mark route as processed but invalid - save to avoid re-processing
                        route_signature = self.route_to_signature(route)
                        self.save_progress(route_signature)
                        return None  # Early termination - route is useless
                    
                    # Rate limiting per thread
                    time.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    print(f"    [{thread_id}] ❌ Error searching {origin_city} → {dest_city}: {e}")
                    print(f"    [{thread_id}] 🚫 EARLY TERMINATION: Route discarded due to search error")
                    # Mark route as processed but invalid - save to avoid re-processing
                    route_signature = self.route_to_signature(route)
                    self.save_progress(route_signature)
                    return None  # Early termination - route has errors
            
            # If we reach here, all segments have valid Turkish Airlines flights
            result = {
                "route_index": route_index,
                "route": route,
                "flights": route_flights,
                "total_cost_inr": total_cost,
                "total_cost_formatted": f"₹{total_cost:,.0f}" if total_cost > 0 else "N/A",
                "thread_id": thread_id,
                "completed_at": datetime.now().isoformat(),
                "status": "complete_with_all_turkish_flights"
            }
            
            print(f"    [{thread_id}] 🎉 ROUTE COMPLETE: All {len(route_flights)} segments have Turkish Airlines flights!")
            
            # Save result immediately and mark as completed
            self.save_result_to_file(result)
            route_signature = self.route_to_signature(route)
            self.save_progress(route_signature)
            
            self.update_progress(success=True)
            return result
            
        except Exception as e:
            print(f"[{thread_id}] ❌ Failed to process route #{route_index}: {e}")
            # Mark route as processed but failed - save to avoid re-processing
            route_signature = self.route_to_signature(route)
            self.save_progress(route_signature)
            self.update_progress(success=False)
            return None
    
    def parse_price(self, price_str):
        """Parse INR price string to float"""
        if not price_str or price_str == "N/A":
            return 999999
        
        # Remove ₹ symbol and commas, convert to float
        try:
            cleaned = price_str.replace("₹", "").replace(",", "").strip()
            return float(cleaned)
        except:
            return 999999
    
    def worker_search_route(self, args):
        """Worker function for thread pool - searches a single route with early termination"""
        route, route_index = args
        
        # Create a scraper instance for this thread
        scraper = self.create_scraper(headless=True)
        
        try:
            result = self.search_route_flights(route, scraper, route_index)
            if result is None:
                # Route was discarded due to early termination
                self.update_progress(success=False, discarded=True)
            return result
        finally:
            # Clean up scraper resources
            try:
                scraper.close()
            except:
                pass
    
    def search_all_routes_parallel(self, routes):
        """Search flights for all routes using multi-threading with resume capability"""
        results = []
        
        # Filter out already completed routes
        pending_routes = []
        skipped_count = 0
        
        for i, route in enumerate(routes[:self.max_routes_to_search]):
            if not self.is_route_completed(route):
                pending_routes.append((route, i+1))
            else:
                skipped_count += 1
        
        print(f"\n🌍 Starting MULTI-THREADED flight search with RESUME and EARLY TERMINATION...")
        print(f"📊 Total routes: {self.max_routes_to_search}")
        print(f"✅ Already completed: {skipped_count}")
        print(f"🔄 Pending routes: {len(pending_routes)}")
        print(f"🚫 Early termination: Routes with missing Turkish Airlines flights will be discarded")
        print(f"🔧 Configuration: {self.max_workers} threads, {self.rate_limit_delay}s delay per thread")
        print("="*90)
        
        if not pending_routes:
            print("🎉 All routes already completed! Loading existing results...")
            # Load and return existing results
            if os.path.exists(self.results_file):
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        
        start_time = time.time()
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all pending tasks
            future_to_route = {
                executor.submit(self.worker_search_route, args): args 
                for args in pending_routes
            }
            
            # Process completed tasks as they finish
            for future in as_completed(future_to_route):
                route_args = future_to_route[future]
                route, route_index = route_args
                
                try:
                    result = future.result()
                    if result:
                        with self.results_lock:
                            results.append(result)
                        
                        # Progress update (result already saved in search_route_flights)
                        with self.progress_lock:
                            total_processed = self.completed_count + self.failed_count
                            if total_processed % 5 == 0:  # More frequent updates
                                print(f"📊 Progress: {self.completed_count} completed, {self.failed_count} failed, {total_processed}/{len(pending_routes)} pending")
                            
                except Exception as e:
                    print(f"❌ Route #{route_index} failed with exception: {e}")
                    self.update_progress(success=False)
        
        elapsed_time = time.time() - start_time
        
        print(f"\n⏱️  Processing time for new routes: {elapsed_time:.2f} seconds")
        discarded_count = getattr(self, 'discarded_count', 0)
        print(f"📊 Final stats: {self.completed_count} completed, {self.failed_count} failed, {discarded_count} discarded")
        
        if discarded_count > 0:
            print(f"🚀 Performance gain: Saved ~{discarded_count * 3 * self.rate_limit_delay:.1f} seconds by early termination")
        
        # Load complete results from file (includes both old and new)
        if os.path.exists(self.results_file):
            with open(self.results_file, 'r', encoding='utf-8') as f:
                all_results = json.load(f)
                complete_routes = [r for r in all_results if r.get('status') == 'complete_with_all_turkish_flights']
                print(f"📂 Total results in file: {len(all_results)} (complete with Turkish flights: {len(complete_routes)})")
                return all_results
        
        return results
    
    def search_all_routes(self, routes):
        """Search flights for all generated routes (now uses parallel processing)"""
        return self.search_all_routes_parallel(routes)
    
    def save_results(self, results, filename="turkish_airlines_comprehensive_search.json"):
        """Save search results to JSON file"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to {filename}")
    
    def print_summary(self, results):
        """Print summary of search results (focusing on complete Turkish Airlines routes)"""
        print(f"\n🏆 SEARCH RESULTS SUMMARY")
        print("="*80)
        
        if not results:
            print("No results found.")
            return
        
        # Filter routes with complete Turkish Airlines coverage
        complete_routes = [r for r in results if r.get('status') == 'complete_with_all_turkish_flights']
        partial_routes = [r for r in results if r.get('status') != 'complete_with_all_turkish_flights']
        
        print(f"✅ Complete Turkish Airlines routes: {len(complete_routes)}")
        print(f"⚠️  Discarded/incomplete routes: {len(partial_routes)}")
        print(f"📊 Total processed: {len(results)}")
        
        if complete_routes:
            print(f"\n🥇 TOP 5 CHEAPEST COMPLETE TURKISH AIRLINES ROUTES:")
            
            # Sort complete routes by cost
            complete_routes.sort(key=lambda x: x.get("total_cost_inr", 999999))
            
            for i, result in enumerate(complete_routes[:5], 1):
                route = result["route"]
                easy_visa_count = sum(1 for stop in route if stop["easy_visa"])
                
                print(f"\n{i}. TOTAL COST: {result['total_cost_formatted']} | Easy Visa: {easy_visa_count}/6")
                print("   Route:", " → ".join([f"{stop['city']} ({stop['country_code']})" for stop in route]))
                print("   Flight segments (all Turkish Airlines):")
                for flight_info in result["flights"]:
                    if flight_info["flight"]:
                        flight = flight_info["flight"]
                        route_info = " → ".join(flight.get("route", []))
                        print(f"     • {flight_info['segment']}: {flight.get('price', 'N/A')} - {flight.get('duration', 'N/A')} (via {route_info})")
        else:
            print(f"\n❌ No complete Turkish Airlines routes found yet.")
            print(f"💡 Routes are discarded when any segment lacks Turkish Airlines flights.")
            print(f"🔄 Continue processing more routes to find complete ones.")
        
        # Show efficiency statistics
        if hasattr(self, 'discarded_count') and self.discarded_count > 0:
            total_processed = len(results) + self.discarded_count
            efficiency = (len(complete_routes) / total_processed) * 100 if total_processed > 0 else 0
            print(f"\n📈 Processing Efficiency:")
            print(f"   • Routes with complete Turkish coverage: {efficiency:.1f}%")
            print(f"   • Early termination saved time on {self.discarded_count} invalid routes")

    def filter_turkish_airlines_flights(self, flights, thread_id="Main"):
        """Filter flights to only include Turkish Airlines operated flights that route via IST"""
        valid_flights = []
        
        for flight in flights:
            # Check if airline is only Turkish Airlines (not codeshare)
            airline = flight.get("airline", "")
            if not airline:
                print(f"      [{thread_id}] 🚫 Skipping flight with no airline info")
                continue
            
            # Skip flights that have multiple airlines (codeshare)
            if "," in airline or " + " in airline or "/" in airline:
                print(f"      [{thread_id}] 🚫 Skipping codeshare flight: {airline}")
                continue
            
            # Check if it's Turkish Airlines (handle various name formats)
            airline_lower = airline.lower().strip()
            turkish_airlines_names = [
                "turkish airlines",
                "turkish",
                "thy",
                "tk"  # IATA code
            ]
            
            is_turkish = any(name in airline_lower for name in turkish_airlines_names)
            if not is_turkish:
                print(f"      [{thread_id}] 🚫 Skipping non-Turkish Airlines flight: {airline}")
                continue
            
            # Check if route includes IST (Istanbul) - check both route and stops
            route = flight.get("route", [])
            stops = flight.get("stops", [])
            
            # Combine route and stops for comprehensive IST check
            all_airports = []
            if isinstance(route, list):
                all_airports.extend(route)
            if isinstance(stops, list):
                all_airports.extend(stops)
            
            # Also check if IST is mentioned in any other fields
            flight_str = str(flight).upper()
            
            has_ist = (
                "IST" in all_airports or 
                "IST" in flight_str or
                "ISTANBUL" in flight_str
            )
            
            if not has_ist:
                print(f"      [{thread_id}] 🚫 Skipping flight not via IST: route {route}, stops {stops}")
                continue
            
            print(f"      [{thread_id}] ✅ Valid Turkish Airlines flight via IST: route {route}")
            valid_flights.append(flight)
        
        return valid_flights

def main():
    print("🇹🇷 Turkish Airlines 1M Miles Challenge - Multi-Threaded Flight Search with Resume & Early Termination")
    print("="*100)
    
    # Generate all possible route combinations for comprehensive analysis
    print("\n📋 Generating ALL possible route combinations...")
    routes = generate_all_possible_combinations()
    
    # Show summary of generated routes
    print(f"\n📊 Route Generation Summary:")
    print(f"Total routes generated: {len(routes)}")
    
    # Group routes by continents for analysis
    continent_combinations = {}
    for route in routes:
        unique_continents = list(dict.fromkeys([stop['continent'] for stop in route]))
        continents = tuple(sorted(unique_continents))
        continent_combinations[continents] = continent_combinations.get(continents, 0) + 1
    
    print(f"Unique continent combinations: {len(continent_combinations)}")
    
    # Count easy visa routes
    all_easy_visa_routes = [r for r in routes if all(stop['easy_visa'] for stop in r)]
    print(f"Routes with all easy visa countries: {len(all_easy_visa_routes)}")
    
    # Calculate optimal search parameters
    total_routes = len(routes)
    
    # Configuration for different scales
    if total_routes > 40000:
        # For very large datasets, process in manageable chunks
        max_routes_to_search = min(20, total_routes)  # Process 1000 routes at a time
        print(f"\n⚠️  Very large dataset detected ({total_routes:,} routes)")
        print(f"📊 Processing in chunks of {max_routes_to_search} routes")
        print(f"💡 Run multiple times to process all routes incrementally")
    elif total_routes > 10000:
        max_routes_to_search = min(1000, total_routes)  # Medium batch size
        print(f"\n⚠️  Large dataset detected ({total_routes:,} routes)")
        print(f"� Processing {max_routes_to_search} routes in this run")
        print(f"💡 Use resume capability for interrupted runs")
    else:
        max_routes_to_search = total_routes
    
    # Threading configuration - balance between speed and API rate limits
    max_workers = 8  # Increased for better parallelization
    rate_limit_delay = 1.0  # Reduced delay for faster processing
    
    print(f"\n🔧 Multi-threading configuration:")
    print(f"   • Max workers: {max_workers} threads")
    print(f"   • Rate limit: {rate_limit_delay}s delay per thread")
    print(f"   • Routes to search: {max_routes_to_search}")
    print(f"   • Estimated time per route: ~{6 * rate_limit_delay}s")
    print(f"   • Estimated total time: ~{(max_routes_to_search * 6 * rate_limit_delay) / max_workers / 60:.1f} minutes")
    
    print(f"\n💾 Resume capability:")
    print(f"   • Progress file: flight_search_progress.json")
    print(f"   • Results file: flight_search_results.json")
    print(f"   • Automatic save after each completed route")
    print(f"   • Resume from last position on restart")
    
    print(f"\n🚫 Early termination optimization:")
    print(f"   • Routes discarded immediately if any segment lacks Turkish Airlines flights")
    print(f"   • Significant time savings by avoiding useless route completion")
    print(f"   • Only complete Turkish Airlines routes are saved as results")
    
    # Initialize optimizer for multi-threaded search with resume capability
    print("\n🔍 Starting multi-threaded flight search with resume capability...")
    optimizer = TurkishAirlinesOptimizer(
        headless=True, 
        max_routes_to_search=max_routes_to_search,
        max_workers=max_workers,
        rate_limit_delay=rate_limit_delay,
        progress_file="flight_search_progress.json",
        results_file="flight_search_results.json"
    )
    
    # Search for flights
    results = optimizer.search_all_routes(routes)
    
    # Display results summary
    optimizer.print_summary(results)
    
    print(f"\n✅ Multi-threaded search complete!")
    print(f"📂 Results saved to: flight_search_results.json")
    print(f"📂 Progress saved to: flight_search_progress.json")
    print(f"🔄 To continue processing more routes, run the script again")
    print(f"🚀 Resume capability ensures no work is lost!")
    
    # Show progress statistics
    total_completed = len(results)
    remaining = total_routes - total_completed
    if remaining > 0:
        print(f"\n📊 Progress Statistics:")
        print(f"   • Completed: {total_completed:,} routes")
        print(f"   • Remaining: {remaining:,} routes")
        print(f"   • Progress: {(total_completed/total_routes)*100:.1f}%")
        print(f"   • Estimated time to complete all: ~{(remaining * 6 * rate_limit_delay) / max_workers / 3600:.1f} hours")

if __name__ == "__main__":
    main()
