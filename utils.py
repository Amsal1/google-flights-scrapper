def get_eligible_country_list():
    return {
        "Europe": ["DE", "AT", "AZ", "BE", "GB", "BA", "BG", "CZ", "DK", "EE", "FI", "FR", "GE", "HR", "NL", "IE", "ES", "SE", "CH", "IT", "ME", "XK", "LV", "LT", "LU", "HU", "MK", "MT", "MD", "NO", "PL", "PT", "RO", "RU", "RS", "SI", "GR"],
        "North America": ["US", "CA", "CU", "MX", "PA"],
        "South America": ["AR", "BR", "CO", "CL", "VE"],
        "Asia": ["AF", "BH", "BD", "AE", "CN", "ID", "PH", "KR", "IN", "IQ", "IR", "JP", "QA", "KZ", "KG", "KW", "LB", "MV", "MY", "MN", "NP", "UZ", "PK", "SG", "LK", "SY", "SA", "TH", "TM", "OM", "JO", "VN", "TR"],
        "Africa": ["AO", "BJ", "BF", "DZ", "DJ", "TD", "CD", "ER", "ET", "MA", "CI", "GA", "GM", "GH", "GN", "ZA", "SS", "CM", "KE", "CG", "LY", "MG", "ML", "MU", "EG", "MR", "MZ", "NE", "NG", "RW", "SN", "SL", "SO", "TZ", "TN", "UG", "ZM"],
        "Oceania": ["AU"]
    }
    

REQUIRED_CONTINENTS = ["Asia", "Europe", "Africa", "North America", "South America", "Oceania"]

COUNTRY_MAJOR_CITIES = {
    # Asia (Easy visa priority for Indians)
    "IN": ["Delhi", "Mumbai"],
    "AE": ["Dubai", "Abu Dhabi"],
    "SG": ["Singapore"],
    "TH": ["Bangkok", "Phuket"],
    "TR": ["Istanbul"],
    "ID": ["Jakarta", "Bali"],
    "QA": ["Doha"],
    "MY": ["Kuala Lumpur"],
    "BD": ["Dhaka"],
    "LK": ["Colombo"],
    "MV": ["Male"],
    "CN": ["Beijing", "Shanghai"],
    "JP": ["Tokyo", "Osaka"],
    "KR": ["Seoul"],
    "PH": ["Manila"],
    "VN": ["Ho Chi Minh City", "Hanoi"],
    "SA": ["Riyadh", "Jeddah"],
    "KW": ["Kuwait City"],
    "BH": ["Manama"],
    "OM": ["Muscat"],
    "LB": ["Beirut"],
    "AF": ["Kabul"],
    "KZ": ["Almaty"],
    "UZ": ["Tashkent"],
    "KG": ["Bishkek"],
    "TM": ["Ashgabat"],
    "MN": ["Ulaanbaatar"],
    
    # Europe
    "DE": ["Frankfurt", "Munich", "Berlin"],
    "FR": ["Paris", "Lyon"],
    "NL": ["Amsterdam"],
    "IT": ["Rome", "Milan"],
    "ES": ["Madrid", "Barcelona"],
    "GB": ["London", "Manchester"],
    "RU": ["Moscow", "Saint Petersburg"],
    "AT": ["Vienna"],
    "BE": ["Brussels"],
    "CH": ["Zurich", "Geneva"],
    "SE": ["Stockholm"],
    "NO": ["Oslo"],
    "DK": ["Copenhagen"],
    "FI": ["Helsinki"],
    "PL": ["Warsaw", "Krakow"],
    "CZ": ["Prague"],
    "HU": ["Budapest"],
    "GR": ["Athens"],
    "PT": ["Lisbon"],
    "RO": ["Bucharest"],
    "BG": ["Sofia"],
    "HR": ["Zagreb"],
    "RS": ["Belgrade"],
    "BA": ["Sarajevo"],
    "ME": ["Podgorica"],
    "SI": ["Ljubljana"],
    "MK": ["Skopje"],
    "AZ": ["Baku"],
    "GE": ["Tbilisi"],
    "MD": ["Chisinau"],
    "EE": ["Tallinn"],
    "LV": ["Riga"],
    "LT": ["Vilnius"],
    "LU": ["Luxembourg"],
    "MT": ["Valletta"],
    "IE": ["Dublin"],
    
    # Africa (Easy visa priority)
    "EG": ["Cairo", "Alexandria"],
    "KE": ["Nairobi"],
    "ZA": ["Johannesburg", "Cape Town"],
    "MA": ["Casablanca", "Marrakech"],
    "TN": ["Tunis"],
    "DZ": ["Algiers"],
    "LY": ["Tripoli"],
    "ET": ["Addis Ababa"],
    "GH": ["Accra"],
    "NG": ["Lagos", "Abuja"],
    "SN": ["Dakar"],
    "CI": ["Abidjan"],
    "CM": ["Douala"],
    "CD": ["Kinshasa"],
    "AO": ["Luanda"],
    "UG": ["Kampala"],
    "TZ": ["Dar es Salaam"],
    "RW": ["Kigali"],
    "MU": ["Port Louis"],
    
    # North America
    "US": ["New York", "Los Angeles", "Chicago", "Miami", "San Francisco", "Washington DC", "Seattle", "Boston"],
    "CA": ["Toronto", "Montreal", "Vancouver"],
    "MX": ["Mexico City", "Cancun"],
    "PA": ["Panama City"],
    
    # South America (Easy visa priority)
    "BR": ["Sao Paulo", "Rio de Janeiro"],
    "AR": ["Buenos Aires"],
    "CO": ["Bogota", "Medellin"],
    "CL": ["Santiago"],
    "VE": ["Caracas"],
    
    # Oceania
    "AU": ["Melbourne", "Sydney"],
}


EASY_VISA_COUNTRIES = {
    # Visa-free or Visa-on-arrival for Indian passport holders
    "IN",  # Home country
    "AE",  # UAE - Visa on arrival
    "QA",  # Qatar - Visa on arrival
    "ID",  # Indonesia - Visa on arrival/free
    "TH",  # Thailand - Visa on arrival
    "MY",  # Malaysia - Visa on arrival
    "SG",  # Singapore - Visa-free transit, easy tourist visa
    "LK",  # Sri Lanka - Electronic Travel Authorization
    "MV",  # Maldives - Visa on arrival
    # "BD",  # Bangladesh - Visa on arrival
    "TR",  # Turkey - Visa required but easy process
    "GE",  # Georgia - Visa-free
    "KE",  # Kenya - e-Visa
    "EG",  # Egypt - Visa on arrival
    "MU",  # Mauritius - Visa on arrival
    "BR",  # Brazil - e-Visa
    "AR",  # Argentina - e-Visa  
    "CU",  # Cuba - Tourist card
    "CO",  # Colombia - Visa-free
    "BA",  # Bosnia - Visa-free
    "RS",  # Serbia - Visa-free
    "ME",  # Montenegro - Visa-free
    "MK",  # North Macedonia - Visa required but easier process
    "MD",  # Moldova - Visa-free
    "AU",  # Australia - e-Visa (though requires more documentation)
    "UZ",  # Uzbekistan - e-Visa (easy online process)
    "ZA",  # South Africa - Visa required but easier process
    "MA",  # Morocco - Visa required but easier process
    "AZ",  # Azerbaijan - e-Visa (easy online process)
    "CA",  # Canada - Visa (though requires more documentation)
    "MX",  # Mexico - Visa (though requires more documentation)
}