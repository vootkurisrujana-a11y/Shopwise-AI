import re
import json

CATEGORIES_MAP = {
    "laptop": ["laptop", "laptops", "notebook", "notebooks", "pc", "macbook", "computer", "computers"],
    "phone": ["phone", "phones", "mobile", "mobiles", "smartphone", "smartphones", "iphone"],
    "headphone": ["headphone", "headphones", "earphone", "earphones", "audio", "earbuds", "buds", "headset"],
    "camera": ["camera", "cameras", "dslr", "mirrorless", "vlog", "vlogging", "photography"],
    "smartwatch": ["watch", "watches", "smartwatch", "smartwatches", "fitness tracker", "band"]
}

KEYWORD_GROUPS = {
    "coding": ["coding", "programming", "developer", "software", "compile", "development", "python", "java", "vscode"],
    "gaming": ["gaming", "game", "games", "play", "rtx", "graphics", "gpu", "fps", "refresh rate", "120hz"],
    "portability": ["lightweight", "portable", "slim", "thin", "travel", "easy to carry"],
    "battery": ["battery", "backup", "mah", "hours", "charging", "charger", "fast charging", "long-lasting"],
    "screen": ["screen", "display", "amoled", "oled", "retina", "ips", "fhd", "refresh rate", "pixels"],
    "camera": ["camera", "photography", "photos", "vlog", "vlogging", "sensor", "lens", "megapixel", "mp", "sony imx", "ois"],
    "audio": ["bass", "sound", "noise cancelling", "anc", "music", "audiophile", "vocals", "driver"],
    "performance": ["fast", "performance", "speed", "ram", "ssd", "nvme", "ryzen", "intel", "m1", "unified", "processor"],
    "ruggedness": ["waterproof", "water resistant", "durable", "ip68", "5atm", "dust resistant"],
    "rating": ["best", "popular", "top-rated", "high rating", "rated", "excellent", "premium"]
}

def parse_query(query):
    """
    Parses a natural language query to extract:
    1. Category (laptop, phone, etc.)
    2. Budget limit (e.g. 50000, 20000)
    3. Target keywords/features (coding, camera, etc.)
    """
    query_clean = query.lower().strip()
    
    # 1. Category Extraction
    detected_category = None
    for category, keywords in CATEGORIES_MAP.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', query_clean):
                detected_category = category
                break
        if detected_category:
            break
            
    # 2. Budget Extraction
    detected_budget = None
    
    # Convert things like "50k", "20k", "1.5k" into numbers
    k_matches = re.findall(r'(\d+(?:\.\d+)?)\s*k\b', query_clean)
    if k_matches:
        # Take the first k matching number
        try:
            detected_budget = float(k_matches[0]) * 1000
        except ValueError:
            pass
            
    if not detected_budget:
        # Look for phrases like "under X", "below X", "less than X", "budget of X"
        budget_patterns = [
            r'(?:under|below|less than|budget of|within|upto|up to)\s*(?:rs\.?|₹)?\s*(\d+(?:,\d+)*)',
            r'(?:rs\.?|₹)?\s*(\d+(?:,\d+)*)\s*(?:budget|price)',
            r'(?:rs\.?|₹)\s*(\d+(?:,\d+)*)'
        ]
        for pattern in budget_patterns:
            matches = re.findall(pattern, query_clean)
            if matches:
                # Clean commas and parse
                val_str = matches[0].replace(',', '')
                try:
                    val = float(val_str)
                    # Ignore small numbers that could refer to RAM (8, 16), screen size (6.7), or ratings (4.5)
                    if val >= 500:
                        detected_budget = val
                        break
                except ValueError:
                    pass
                    
    # 3. Keyword / Feature Extraction
    detected_keywords = []
    for feature_group, keywords in KEYWORD_GROUPS.items():
        for kw in keywords:
            if len(kw) <= 3:
                if re.search(r'\b' + re.escape(kw) + r'\b', query_clean):
                    detected_keywords.append(feature_group)
                    break
            else:
                if kw in query_clean:
                    detected_keywords.append(feature_group)
                    break
                
    return {
        "category": detected_category,
        "budget": detected_budget,
        "keywords": list(set(detected_keywords))
    }

def score_product(product, parsed_query, elasticity_mode="strict"):
    """
    Scores a single product based on the parsed query filters and parameters.
    Returns (score, explanation)
    """
    target_budget = parsed_query["budget"]
    keywords = parsed_query["keywords"]
    
    score = 0.0
    reasons = []
    
    # Base Score: Product Rating contributes up to 10 points (rating * 2)
    score += product["rating"] * 2.0
    
    # Price evaluation against budget
    price = product["price"]
    is_over_budget = False
    
    if target_budget:
        limit_strict = target_budget
        limit_flex = target_budget * 1.10
        limit_value = target_budget * 1.20
        
        allowed_limit = limit_strict
        if elasticity_mode == "flexible":
            allowed_limit = limit_flex
        elif elasticity_mode == "value":
            allowed_limit = limit_value
            
        if price > allowed_limit:
            # Strictly filter out products exceeding allowed limit
            return -1, None
            
        if price > target_budget:
            # Over original budget, but within elasticity limit. Add mild penalty, explain upgrade
            is_over_budget = True
            diff_pct = ((price - target_budget) / target_budget) * 100
            score -= 3.0  # cost penalty
            reasons.append(f"Priced slightly above target budget (+{diff_pct:.0f}%), but recommended for its premium performance.")
        else:
            # Under budget - reward products that utilize budget well, but leave some saving
            # Prefer products within 70% to 100% of budget as they are usually higher spec than 30% budget
            ratio = price / target_budget
            if ratio >= 0.7:
                score += 4.0
                reasons.append(f"Excellent budget utilization at ₹{price:,.2f} (under your ₹{target_budget:,.2f} limit).")
            else:
                score += 2.0
                reasons.append(f"Highly affordable option, saving you ₹{target_budget - price:,.2f} relative to your budget.")
    
    # Keyword/Feature Matching (check in name, description, and specs)
    matched_kws = []
    product_content = (product["name"] + " " + product["description"] + " " + json.dumps(product["specs_dict"])).lower()
    
    for kw in keywords:
        kw_matched = False
        # Search the synonyms/terms in KEYWORD_GROUPS
        for term in KEYWORD_GROUPS[kw]:
            if term in product_content:
                score += 4.0
                kw_matched = True
                break
        if kw_matched:
            matched_kws.append(kw)
            
    if matched_kws:
        reasons.append(f"Directly supports required features: {', '.join(matched_kws)}.")
    
    # Highlight rating
    if product["rating"] >= 4.5:
        score += 2.0
        reasons.append(f"Highly acclaimed by users, holding an exceptional {product['rating']}★ rating.")
        
    # Compile reasoning text
    if not reasons:
        explanation = f"Matches Category '{product['category'].capitalize()}' and provides great overall value."
    else:
        explanation = " ".join(reasons)
        
    return score, explanation

def get_recommendations(products, query, elasticity_mode="strict"):
    """
    Filters and ranks products based on NL query and budget elasticity.
    """
    parsed = parse_query(query)
    
    scored_list = []
    for p in products:
        # Category filter: if category is parsed, only recommend matching category
        if parsed["category"] and p["category"] != parsed["category"]:
            continue
            
        score, explanation = score_product(p, parsed, elasticity_mode)
        if score >= 0:
            scored_list.append({
                "product": p,
                "score": score,
                "explanation": explanation
            })
            
    # Sort by score descending, then rating descending
    scored_list.sort(key=lambda x: (x["score"], x["product"]["rating"]), reverse=True)
    
    # Extract top 3 recommendations
    recommendations = scored_list[:3]
    
    return {
        "parsed_query": parsed,
        "recommendations": recommendations
    }

def calculate_feature_scores(product):
    """
    Programmatically calculates scores (0-100) for comparison dimensions.
    Dimensions: Performance, Portability/Battery, Camera/Media, Build Quality
    """
    category = product["category"]
    specs = product["specs_dict"]
    rating = product["rating"]
    price = product["price"]
    
    perf = 50.0 + (rating * 5.0) # Base 70-75
    port = 50.0 + (rating * 5.0)
    media = 50.0 + (rating * 5.0)
    build = 60.0 + (rating * 6.0) # Base 84-90
    
    # Customize based on specific specifications parsing
    if category == "laptop":
        # Performance
        ram = specs.get("RAM", "").lower()
        if "16gb" in ram:
            perf += 15
        elif "8gb" in ram:
            perf += 5
            
        cpu = specs.get("CPU", "").lower()
        if "ryzen 7" in cpu or "m1" in cpu:
            perf += 15
        elif "ryzen 5" in cpu or "i3" in cpu:
            perf += 5
            
        # Portability
        weight = specs.get("Weight", "").lower()
        if "1.2" in weight or "1.3" in weight or "1.4" in weight:
            port += 15
        elif "2.4" in weight:
            port -= 10 # heavy gaming laptop
            
        # Battery
        battery = specs.get("Battery", "").lower()
        if "15 hours" in battery:
            port += 15
        elif "8 hours" in battery:
            port += 5
        elif "5 hours" in battery:
            port -= 5
            
        media += 10 # standard display rating
        
    elif category == "phone":
        # Camera
        cam = specs.get("Camera", "").lower()
        if "108mp" in cam:
            media += 20
        elif "50mp" in cam or "64mp" in cam:
            media += 12
        elif "48mp" in cam:
            media += 5
            
        # Performance
        proc = specs.get("Processor", "").lower()
        if "snapdragon" in proc or "dimensity 1080" in proc:
            perf += 10
            
        ram = specs.get("RAM", "").lower()
        if "8gb" in ram:
            perf += 10
        elif "6gb" in ram:
            perf += 5
            
        # Battery / Portability
        port += 10 # phones are portable
        bat = specs.get("Battery", "").lower()
        if "5000mah" in bat:
            port += 10
            
    elif category == "headphone":
        # Media / Audio
        anc = specs.get("Noise_Cancelling", "").lower()
        if "active" in anc or "anc" in anc:
            media += 20
            
        # Portability
        type_hp = specs.get("Type", "").lower()
        if "in-ear" in type_hp:
            port += 15
        elif "on-ear" in type_hp or "over-ear" in type_hp:
            port += 5
            
        bat = specs.get("Battery", "").lower()
        if "30 hours" in bat or "40 hours" in bat:
            port += 10
            
    elif category == "camera":
        # Media
        res = specs.get("Resolution", "").lower()
        if "24" in res or "32" in res:
            media += 20
            
        vid = specs.get("Video", "").lower()
        if "4k" in vid:
            media += 15
            
        # Portability
        weight = specs.get("Weight", "").lower()
        if "387" in weight or "400" in weight:
            port += 10
            
    elif category == "smartwatch":
        # Ruggedness / Build Quality
        water = specs.get("Water_Resistance", "").lower()
        if "5atm" in water:
            build += 12
        elif "ip68" in water:
            build += 5
            
        # Portability/Battery
        bat = specs.get("Battery", "").lower()
        if "14 days" in bat:
            port += 20
        elif "7 days" in bat:
            port += 10
            
        # Sensors
        sens = specs.get("Sensors", "").lower()
        if "gps" in sens:
            perf += 10
            
    # Normalize limits (0 - 100)
    return {
        "performance": min(max(int(perf), 0), 100),
        "portability": min(max(int(port), 0), 100),
        "media": min(max(int(media), 0), 100),
        "build": min(max(int(build), 0), 100)
    }

def generate_comparison_verdict(products):
    """
    Accepts 2 or 3 products, calculates spec attributes and generates a comprehensive,
    innovative comparison 'AI Verdict'.
    """
    if len(products) < 2:
        return "Please select at least 2 products to compare."
        
    p1 = products[0]
    p2 = products[1]
    p3 = products[2] if len(products) > 2 else None
    
    # Calculate feature scores for analysis
    scores1 = calculate_feature_scores(p1)
    scores2 = calculate_feature_scores(p2)
    scores3 = calculate_feature_scores(p3) if p3 else None
    
    # Identify standouts
    # 1. Best Price
    cheapest = p1
    if p2["price"] < cheapest["price"]:
        cheapest = p2
    if p3 and p3["price"] < cheapest["price"]:
        cheapest = p3
        
    # 2. Best Rating
    highest_rated = p1
    if p2["rating"] > highest_rated["rating"]:
        highest_rated = p2
    if p3 and p3["rating"] > highest_rated["rating"]:
        highest_rated = p3
        
    # 3. Best Performance Score
    highest_perf = p1
    perf_val = scores1["performance"]
    if scores2["performance"] > perf_val:
        highest_perf = p2
        perf_val = scores2["performance"]
    if p3 and scores3["performance"] > perf_val:
        highest_perf = p3
        perf_val = scores3["performance"]

    # 4. Best Battery/Portability
    highest_port = p1
    port_val = scores1["portability"]
    if scores2["portability"] > port_val:
        highest_port = p2
        port_val = scores2["portability"]
    if p3 and scores3["portability"] > port_val:
        highest_port = p3
        port_val = scores3["portability"]

    # Write dynamically structured text
    verdict_text = f"<h3>AI Verdict Analysis</h3>"
    verdict_text += f"<p>Our recommendation engine analyzed specifications and customer satisfaction ratings for these products. Here is the custom purchase guide:</p>"
    
    verdict_text += f"<ul>"
    verdict_text += f"<li><strong>Best Value Pick:</strong> <em>{highest_rated['name']}</em> holds the highest customer rating of {highest_rated['rating']}★ and provides great consumer utility.</li>"
    verdict_text += f"<li><strong>Top Performance:</strong> <em>{highest_perf['name']}</em> scores highest in execution specs ({scores1['performance'] if highest_perf == p1 else (scores2['performance'] if highest_perf == p2 else scores3['performance'])}/100) making it ideal for intensive usage workloads.</li>"
    verdict_text += f"<li><strong>Budget Choice:</strong> <em>{cheapest['name']}</em> is the most pocket-friendly selection, priced at just <strong>₹{cheapest['price']:,.2f}</strong>, allowing you to save money.</li>"
    verdict_text += f"</ul>"
    
    # Specific advice depending on whether prices are very different
    price_diff = abs(p1["price"] - p2["price"])
    if price_diff > 15000:
        verdict_text += f"<p><strong>Smart Buying Advice:</strong> There is a significant price gap of ₹{price_diff:,.2f} between these options. We recommend upgrading to the premium choice only if you need the specialized specifications (like better CPU/Camera), otherwise the budget option delivers excellent basic utility.</p>"
    else:
        verdict_text += f"<p><strong>Smart Buying Advice:</strong> With the prices being relatively close, the {highest_rated['name']} is generally the safer investment due to superior rating and warranty features.</p>"
        
    return verdict_text
