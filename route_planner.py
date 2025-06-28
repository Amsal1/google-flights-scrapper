from itertools import product, combinations
from utils import get_eligible_country_list, COUNTRY_MAJOR_CITIES, EASY_VISA_COUNTRIES, REQUIRED_CONTINENTS
import random

NUM_CONTINENTS = 6
MAX_ROUTES = 4000  # Generate many more route options for comprehensive analysis
EASY_VISA_WEIGHT = 10  # Priority multiplier for easy visa countries

def get_continent_city_mapping():
    """Map eligible countries to their continents and cities - ONLY easy visa countries"""
    eligible_countries = get_eligible_country_list()
    continent_cities = {}
    
    for continent, country_codes in eligible_countries.items():
        continent_cities[continent] = []
        for country_code in country_codes:
            # Only include countries that are in EASY_VISA_COUNTRIES
            if country_code in EASY_VISA_COUNTRIES and country_code in COUNTRY_MAJOR_CITIES:
                cities = COUNTRY_MAJOR_CITIES[country_code]
                for city in cities:
                    continent_cities[continent].append({
                        "country_code": country_code,
                        "city": city,
                        "easy_visa": True  # All countries are easy visa now
                    })
    
    return continent_cities

def calculate_route_score(route):
    """Calculate route score based on priorities: visa ease, cost estimates"""
    score = 0
    
    # Prioritize easy visa countries (most important after cost)
    easy_visa_count = sum(1 for stop in route if stop["easy_visa"])
    score += easy_visa_count * EASY_VISA_WEIGHT
    
    # Prefer fewer countries with multiple cities (potentially cheaper connections)
    countries = set(stop["country_code"] for stop in route)
    if len(countries) < len(route):
        score += 5
    
    return score

def generate_optimal_routes():
    """Generate routes visiting all 6 continents with priority on visa ease and cost"""
    continent_cities = get_continent_city_mapping()
    
    # Ensure we have all required continents
    available_continents = list(continent_cities.keys())
    if len(available_continents) < NUM_CONTINENTS:
        missing = set(REQUIRED_CONTINENTS) - set(available_continents)
        raise ValueError(f"Missing continents: {missing}")
    
    # Print available cities per continent for debugging
    print(f"\n📊 Available cities per continent (Easy Visa only):")
    for continent in available_continents:
        cities_count = len(continent_cities[continent])
        sample_cities = [city['city'] for city in continent_cities[continent][:3]]
        print(f"  {continent}: {cities_count} cities (e.g., {', '.join(sample_cities)}{'...' if cities_count > 3 else ''})")
    
    all_routes = []
    
    # Generate systematic combinations for better coverage
    # Use a completely deterministic approach
    for attempt in range(MAX_ROUTES * 2):  # More attempts to get diverse routes
        route = []
        used_continents = set()
        
        # Shuffle continents deterministically based on attempt number
        continents = available_continents.copy()
        random.seed(attempt)  # Use attempt number as seed for reproducible variety
        random.shuffle(continents)
        # DO NOT reset seed - keep it deterministic
        
        for continent in continents[:NUM_CONTINENTS]:
            if continent in used_continents:
                continue
                
            # Get cities for this continent
            cities = continent_cities[continent].copy()
            
            if not cities:
                continue
            
            # For better diversity, cycle through different selection strategies
            selection_strategy = attempt % 4
            
            if selection_strategy == 0:
                # Strategy 1: Deterministic based on attempt
                selected_city = cities[attempt % len(cities)]
            elif selection_strategy == 1:
                # Strategy 2: Prefer first cities alphabetically (different pattern)
                cities.sort(key=lambda x: x['city'])
                selected_city = cities[attempt % len(cities)]
            elif selection_strategy == 2:
                # Strategy 3: Prefer cities by country code
                cities.sort(key=lambda x: x['country_code'])
                selected_city = cities[attempt % len(cities)]
            else:
                # Strategy 4: Mixed approach
                if len(cities) > 1:
                    # Pick from first half or second half alternately
                    half = len(cities) // 2
                    if attempt % 2 == 0 and half > 0:
                        selected_city = cities[(attempt // 2) % half]
                    else:
                        start_idx = half if half > 0 else 0
                        available_cities = cities[start_idx:] if half > 0 else cities
                        selected_city = available_cities[attempt % len(available_cities)]
                else:
                    selected_city = cities[0]
            
            route.append({
                "continent": continent,
                "country_code": selected_city["country_code"],
                "city": selected_city["city"],
                "easy_visa": selected_city["easy_visa"]
            })
            used_continents.add(continent)
        
        # Only keep routes that visit all 6 continents
        if len(route) == NUM_CONTINENTS:
            all_routes.append(route)
    
    # Remove duplicates more efficiently
    unique_routes = []
    seen_routes = set()
    
    for route in all_routes:
        # Create a signature for deduplication
        route_sig = tuple(sorted([(stop["continent"], stop["city"], stop["country_code"]) for stop in route]))
        if route_sig not in seen_routes:
            seen_routes.add(route_sig)
            unique_routes.append(route)
    
    # Sort by score (higher is better) but keep more variety
    unique_routes.sort(key=calculate_route_score, reverse=True)
    
    print(f"\n📈 Generated {len(unique_routes)} unique routes from {len(all_routes)} total attempts")
    
    return unique_routes[:MAX_ROUTES]

def print_route_summary(routes):
    """Print summary of generated routes"""
    print(f"\n🌍 Generated {len(routes)} optimal routes for Turkish Airlines 1M miles challenge")
    print("="*80)
    
    # Show ALL routes, not just top 10
    for i, route in enumerate(routes, 1):
        score = calculate_route_score(route)
        easy_visa_count = sum(1 for stop in route if stop["easy_visa"])
        
        print(f"\nRoute #{i} (Score: {score})")
        print(f"Easy Visa: {easy_visa_count}/6 cities")
        
        for j, stop in enumerate(route, 1):
            visa_status = "🟢 Easy" if stop["easy_visa"] else "🔴 Hard"
            print(f"  {j}. {stop['city']}, {stop['country_code']} ({stop['continent']}) - {visa_status}")
        
        # Add a separator every 10 routes for readability
        if i % 10 == 0 and i < len(routes):
            print("\n" + "-"*60)

def generate_all_possible_combinations():
    """Generate ALL possible route combinations visiting 6 continents with easy visa countries"""
    continent_cities = get_continent_city_mapping()
    
    # Ensure we have all required continents
    available_continents = list(continent_cities.keys())
    if len(available_continents) < NUM_CONTINENTS:
        missing = set(REQUIRED_CONTINENTS) - set(available_continents)
        raise ValueError(f"Missing continents: {missing}")
    
    print(f"\n📊 Generating ALL possible combinations:")
    city_counts = {}
    for continent in available_continents:
        count = len(continent_cities[continent])
        city_counts[continent] = count
        sample_cities = [city['city'] for city in continent_cities[continent][:3]]
        print(f"  {continent}: {count} cities (e.g., {', '.join(sample_cities)}{'...' if count > 3 else ''})")
    
    # Calculate total combinations
    total_combinations = 1
    for count in city_counts.values():
        total_combinations *= count
    print(f"\n🔢 Total possible combinations: {total_combinations:,}")
    
    if total_combinations > 100000:  # If too many combinations
        print(f"⚠️  Warning: {total_combinations:,} combinations is very large!")
        print("Consider limiting to top cities per continent or using sampling approach.")
        return generate_optimal_routes()  # Fall back to current approach
    
    # Generate all combinations using itertools.product
    continent_city_lists = []
    continent_order = []
    
    for continent in available_continents:
        continent_city_lists.append(continent_cities[continent])
        continent_order.append(continent)
    
    print(f"🔄 Generating all {total_combinations:,} combinations...")
    
    all_routes = []
    for combination in product(*continent_city_lists):
        route = []
        for i, city_info in enumerate(combination):
            route.append({
                "continent": continent_order[i],
                "country_code": city_info["country_code"],
                "city": city_info["city"],
                "easy_visa": city_info["easy_visa"]
            })
        all_routes.append(route)
    
    # Sort by score (higher is better)
    all_routes.sort(key=calculate_route_score, reverse=True)
    
    print(f"✅ Generated {len(all_routes):,} complete route combinations")
    return all_routes



# Generate routes when script is run directly
if __name__ == "__main__":
    print("="*90)
    print("🇹🇷 TURKISH AIRLINES 1M MILES ROUTE PLANNER")
    print("="*90)
    
    # Test first to see if complete coverage is feasible
    continent_cities = get_continent_city_mapping()
    total_combinations = 1
    for continent, cities in continent_cities.items():
        total_combinations *= len(cities)
    
    if total_combinations <= 100000:  # Reasonable limit
        print(f"\n💡 Complete coverage is feasible ({total_combinations:,} combinations)")
        print("\n🔄 COMPLETE COVERAGE - ALL COMBINATIONS:")
        print("-" * 50)
        ALL_COMBINATIONS = generate_all_possible_combinations()
        print_route_summary(ALL_COMBINATIONS[:10])  # Show first 10
        
        print(f"\n📊 COMPLETE COVERAGE SUMMARY:")
        print(f"All standard routes: {len(ALL_COMBINATIONS):,}")
        
    else:
        print(f"\n⚠️  Complete coverage not feasible ({total_combinations:,} combinations)")
        print("Using sampling method instead...")
        
        print("\n1️⃣ STANDARD ROUTES (Sampling):")
        print("-" * 50)
        ITINERARIES = generate_optimal_routes()
        print_route_summary(ITINERARIES[:5])
        
        print(f"\n📊 SAMPLING SUMMARY:")
        print(f"Standard routes generated: {len(ITINERARIES)}")
        print(f"\n💡 Use generate_optimal_routes() for sampling approach")
        print(f"💡 Use generate_all_possible_combinations() for complete coverage")

else:
    # When imported, try complete coverage first, fall back to sampling
    continent_cities = get_continent_city_mapping()
    total_combinations = 1
    for continent, cities in continent_cities.items():
        total_combinations *= len(cities)
    
    if total_combinations <= 100000:
        ITINERARIES = generate_all_possible_combinations()
        print_route_summary(ITINERARIES[:5])
    else:
        ITINERARIES = generate_optimal_routes()
        print_route_summary(ITINERARIES[:5])
