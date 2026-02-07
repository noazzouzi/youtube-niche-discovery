"""
Comprehensive CPM Database for YouTube Niche Discovery
Sources: Lenostube, Outlierkit, FirstGrowthAgency, SMBillion, Reddit r/PartneredYoutube
Last Updated: 2025
"""

from typing import Dict, List, Tuple, Any

# =============================================================================
# CPM DATABASE - 70+ Categories with Real Data
# =============================================================================

CPM_DATABASE: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # TIER 1: ULTRA-PREMIUM ($15-50+)
    # =========================================================================
    "credit_cards": {
        "keywords": ["credit card", "rewards card", "credit score", "credit limit", "credit card review", "best credit cards"],
        "cpm_range": (20.0, 50.0),
        "avg_cpm": 35.0,
        "source": "Outlierkit 2025, Lenostube",
        "notes": "Banks compete aggressively; Q4 peaks",
        "parent_category": "finance"
    },
    "insurance": {
        "keywords": ["insurance", "life insurance", "car insurance", "health insurance", "home insurance"],
        "cpm_range": (25.0, 55.0),
        "avg_cpm": 40.0,
        "source": "Lenostube, industry data",
        "notes": "Highest CPM niche overall",
        "parent_category": "finance"
    },
    "loans_mortgages": {
        "keywords": ["mortgage", "loan", "home loan", "personal loan", "refinance", "lending"],
        "cpm_range": (20.0, 45.0),
        "avg_cpm": 32.0,
        "source": "Outlierkit",
        "notes": "High-value financial products",
        "parent_category": "finance"
    },
    "affiliate_marketing": {
        "keywords": ["affiliate marketing", "affiliate income", "affiliate program", "affiliate tips"],
        "cpm_range": (12.0, 22.0),
        "avg_cpm": 17.0,
        "source": "SMBillion analysis of 100+ creators",
        "notes": "Highest verified CPM niche for creators",
        "parent_category": "business"
    },
    "make_money_online": {
        "keywords": ["make money online", "passive income", "side hustle", "online business", "work from home income"],
        "cpm_range": (10.0, 50.0),
        "avg_cpm": 18.0,
        "source": "FirstGrowthAgency 2024",
        "notes": "High variance; depends on audience",
        "parent_category": "business"
    },
    "personal_finance": {
        "keywords": ["personal finance", "budgeting", "financial planning", "money management", "save money", "financial freedom"],
        "cpm_range": (12.0, 22.0),
        "avg_cpm": 15.0,
        "source": "Lenostube, Outlierkit verified",
        "notes": "Graham Stephan reports $16-20 RPM",
        "parent_category": "finance"
    },
    "investing": {
        "keywords": ["investing", "stocks", "investment", "portfolio", "dividend", "stock market", "value investing"],
        "cpm_range": (12.0, 22.0),
        "avg_cpm": 14.0,
        "source": "Outlierkit, Andrei Jikh data",
        "notes": "Andrei Jikh reports $8-12 RPM",
        "parent_category": "finance"
    },
    "b2b_software": {
        "keywords": ["saas", "b2b", "enterprise software", "crm", "erp", "salesforce", "hubspot"],
        "cpm_range": (15.0, 30.0),
        "avg_cpm": 20.0,
        "source": "Outlierkit",
        "notes": "Enterprise software buyers are premium audience",
        "parent_category": "technology"
    },

    # =========================================================================
    # TIER 2: PREMIUM ($8-15)
    # =========================================================================
    "cryptocurrency": {
        "keywords": ["crypto", "bitcoin", "ethereum", "blockchain", "defi", "nft", "cryptocurrency", "altcoin"],
        "cpm_range": (8.0, 18.0),
        "avg_cpm": 12.0,
        "source": "SMBillion, declining from 2021 peak",
        "notes": "Down from $15-25 in 2021-2022",
        "parent_category": "finance"
    },
    "trading": {
        "keywords": ["trading", "day trading", "forex", "options", "stock trading", "swing trading", "technical analysis"],
        "cpm_range": (8.0, 18.0),
        "avg_cpm": 12.0,
        "source": "SMBillion verified",
        "parent_category": "finance"
    },
    "digital_marketing": {
        "keywords": ["digital marketing", "seo", "ppc", "marketing strategy", "social media marketing", "content marketing", "google ads"],
        "cpm_range": (8.0, 18.0),
        "avg_cpm": 12.5,
        "source": "FirstGrowthAgency",
        "parent_category": "business"
    },
    "real_estate": {
        "keywords": ["real estate", "property", "real estate investing", "rental property", "house flipping", "airbnb"],
        "cpm_range": (10.0, 16.0),
        "avg_cpm": 12.0,
        "source": "Outlierkit",
        "parent_category": "finance"
    },
    "legal_content": {
        "keywords": ["legal", "law", "attorney", "lawyer", "court", "lawsuit", "legal advice"],
        "cpm_range": (12.0, 18.0),
        "avg_cpm": 14.0,
        "source": "Outlierkit, Lenostube",
        "parent_category": "education"
    },
    "vpn_cybersecurity": {
        "keywords": ["vpn", "privacy", "cybersecurity", "online security", "antivirus", "password manager"],
        "cpm_range": (10.0, 20.0),
        "avg_cpm": 15.0,
        "source": "SMBillion - sponsored content heavy",
        "parent_category": "technology"
    },
    "dropshipping_ecommerce": {
        "keywords": ["dropshipping", "ecommerce", "print on demand", "shopify", "amazon fba", "online store"],
        "cpm_range": (7.0, 14.0),
        "avg_cpm": 10.0,
        "source": "SMBillion",
        "parent_category": "business"
    },
    "entrepreneurship": {
        "keywords": ["entrepreneur", "startup", "business owner", "small business", "founder", "solopreneur"],
        "cpm_range": (8.0, 15.0),
        "avg_cpm": 11.0,
        "source": "Lenostube",
        "parent_category": "business"
    },
    "tax_accounting": {
        "keywords": ["tax", "taxes", "accounting", "bookkeeping", "tax tips", "cpa", "tax return"],
        "cpm_range": (12.0, 20.0),
        "avg_cpm": 15.0,
        "source": "Seasonal peaks in Q1",
        "parent_category": "finance"
    },
    "storytelling_narrative": {
        "keywords": ["story", "storytime", "narrative", "betrayal", "revenge story", "story animated"],
        "cpm_range": (8.0, 15.0),
        "avg_cpm": 10.0,
        "source": "Outlierkit - $12.82 RPM for betrayal narratives",
        "parent_category": "entertainment"
    },

    # =========================================================================
    # TIER 3: MODERATE-HIGH ($5-12)
    # =========================================================================
    "education": {
        "keywords": ["education", "educational", "learn", "course", "tutorial", "how to", "explained"],
        "cpm_range": (10.0, 25.0),
        "avg_cpm": 12.0,
        "source": "Lenostube, Khan Academy data",
        "parent_category": "education"
    },
    "technology": {
        "keywords": ["technology", "tech review", "gadget", "smartphone", "laptop", "tech news"],
        "cpm_range": (5.0, 30.0),
        "avg_cpm": 8.0,
        "source": "Lenostube - wide variance",
        "parent_category": "technology"
    },
    "health_wellness": {
        "keywords": ["health", "wellness", "medical", "healthcare", "nutrition", "mental health"],
        "cpm_range": (7.0, 20.0),
        "avg_cpm": 10.0,
        "source": "Lenostube",
        "parent_category": "health"
    },
    "weight_loss": {
        "keywords": ["weight loss", "diet", "keto", "intermittent fasting", "fat loss", "calorie deficit"],
        "cpm_range": (8.0, 15.0),
        "avg_cpm": 10.0,
        "source": "FirstGrowthAgency - supplement advertisers",
        "parent_category": "health"
    },
    "software_tutorials": {
        "keywords": ["software tutorial", "app tutorial", "photoshop", "excel", "programming", "coding tutorial"],
        "cpm_range": (8.0, 15.0),
        "avg_cpm": 10.0,
        "source": "Outlierkit",
        "parent_category": "technology"
    },
    "ai_tools": {
        "keywords": ["ai", "artificial intelligence", "chatgpt", "machine learning", "ai tools", "midjourney", "claude"],
        "cpm_range": (6.0, 15.0),
        "avg_cpm": 9.0,
        "source": "Emerging niche, growing advertisers",
        "parent_category": "technology"
    },
    "career_advice": {
        "keywords": ["career", "job search", "resume", "interview", "career advice", "linkedin", "job hunting"],
        "cpm_range": (6.0, 12.0),
        "avg_cpm": 8.0,
        "source": "SMBillion",
        "parent_category": "education"
    },
    "personal_development": {
        "keywords": ["personal development", "self improvement", "productivity", "motivation", "self help", "habits"],
        "cpm_range": (8.0, 20.0),
        "avg_cpm": 10.0,
        "source": "Outlierkit",
        "parent_category": "lifestyle"
    },
    "language_learning": {
        "keywords": ["language learning", "learn english", "learn spanish", "learn japanese", "polyglot", "duolingo"],
        "cpm_range": (6.0, 12.0),
        "avg_cpm": 8.5,
        "source": "Outlierkit - $11.88 RPM for English podcasts",
        "parent_category": "education"
    },
    "home_improvement": {
        "keywords": ["home improvement", "diy", "renovation", "home decor", "interior design", "woodworking"],
        "cpm_range": (7.0, 15.0),
        "avg_cpm": 9.0,
        "source": "FirstGrowthAgency",
        "parent_category": "lifestyle"
    },
    "sleep_meditation": {
        "keywords": ["sleep", "relaxation", "ambient", "white noise", "meditation", "healing", "calming"],
        "cpm_range": (4.0, 10.0),
        "avg_cpm": 7.0,
        "source": "Outlierkit - $10.92 RPM for healing content",
        "parent_category": "health"
    },
    "travel": {
        "keywords": ["travel", "vacation", "trip", "destination", "hotel", "flight", "travel vlog", "backpacking"],
        "cpm_range": (6.0, 20.0),
        "avg_cpm": 8.0,
        "source": "Lenostube - seasonal variance",
        "parent_category": "lifestyle"
    },
    "photography": {
        "keywords": ["photography", "camera", "photo editing", "lightroom", "portrait", "landscape photography"],
        "cpm_range": (7.0, 10.0),
        "avg_cpm": 7.5,
        "source": "SMBillion",
        "parent_category": "creative"
    },

    # =========================================================================
    # TIER 4: MODERATE ($4-8)
    # =========================================================================
    "beauty_fashion": {
        "keywords": ["beauty", "makeup", "skincare", "fashion", "style", "haul", "grwm", "get ready with me"],
        "cpm_range": (5.0, 18.0),
        "avg_cpm": 7.0,
        "source": "Lenostube",
        "parent_category": "lifestyle"
    },
    "cooking": {
        "keywords": ["cooking", "recipe", "food", "baking", "kitchen", "chef", "meal prep", "restaurant"],
        "cpm_range": (4.0, 8.0),
        "avg_cpm": 5.0,
        "source": "Lenostube, FirstGrowthAgency",
        "parent_category": "lifestyle"
    },
    "fitness": {
        "keywords": ["fitness", "workout", "gym", "exercise", "bodybuilding", "yoga", "crossfit", "home workout"],
        "cpm_range": (3.0, 8.0),
        "avg_cpm": 5.0,
        "source": "Lenostube - supplement ads",
        "parent_category": "health"
    },
    "automotive": {
        "keywords": ["car", "automotive", "vehicle", "car review", "motorcycle", "auto repair", "car mod"],
        "cpm_range": (4.0, 8.0),
        "avg_cpm": 5.5,
        "source": "Lenostube",
        "parent_category": "lifestyle"
    },
    "pets_animals": {
        "keywords": ["pet", "dog", "cat", "animal", "puppy", "kitten", "pet care", "pet training"],
        "cpm_range": (3.0, 7.0),
        "avg_cpm": 4.5,
        "source": "FirstGrowthAgency",
        "parent_category": "lifestyle"
    },
    "parenting": {
        "keywords": ["parenting", "baby", "toddler", "mom", "dad", "family", "pregnancy", "motherhood"],
        "cpm_range": (4.0, 10.0),
        "avg_cpm": 6.0,
        "source": "Family-friendly content premium",
        "parent_category": "lifestyle"
    },
    "relationships": {
        "keywords": ["relationship", "dating", "marriage", "love", "breakup", "dating advice", "couples"],
        "cpm_range": (4.0, 10.0),
        "avg_cpm": 6.0,
        "source": "FirstGrowthAgency",
        "parent_category": "lifestyle"
    },
    "sustainable_living": {
        "keywords": ["sustainable", "eco-friendly", "zero waste", "environment", "green living", "minimalism"],
        "cpm_range": (5.0, 10.0),
        "avg_cpm": 6.5,
        "source": "FirstGrowthAgency - emerging niche",
        "parent_category": "lifestyle"
    },
    "gardening": {
        "keywords": ["gardening", "garden", "plants", "houseplants", "landscaping", "vegetable garden"],
        "cpm_range": (4.0, 8.0),
        "avg_cpm": 5.5,
        "source": "Lenostube",
        "parent_category": "lifestyle"
    },
    "crafts_diy": {
        "keywords": ["crafts", "diy", "handmade", "sewing", "knitting", "crochet", "scrapbooking"],
        "cpm_range": (3.0, 7.0),
        "avg_cpm": 4.5,
        "source": "Lenostube",
        "parent_category": "creative"
    },
    "book_reviews": {
        "keywords": ["book review", "books", "booktube", "reading", "book recommendations", "literature"],
        "cpm_range": (4.0, 8.0),
        "avg_cpm": 5.5,
        "source": "SMBillion",
        "parent_category": "entertainment"
    },
    "science": {
        "keywords": ["science", "physics", "chemistry", "biology", "space", "astronomy", "science explained"],
        "cpm_range": (5.0, 10.0),
        "avg_cpm": 7.0,
        "source": "Education tier",
        "parent_category": "education"
    },
    "history": {
        "keywords": ["history", "historical", "ancient", "world war", "civilization", "documentary"],
        "cpm_range": (4.0, 9.0),
        "avg_cpm": 6.0,
        "source": "Education tier",
        "parent_category": "education"
    },
    "news_commentary": {
        "keywords": ["news", "politics", "current events", "commentary", "analysis", "opinion"],
        "cpm_range": (3.0, 8.0),
        "avg_cpm": 4.5,
        "source": "Varies by topic sensitivity",
        "parent_category": "entertainment"
    },
    "true_crime": {
        "keywords": ["true crime", "mystery", "crime", "investigation", "murder", "cold case", "unsolved"],
        "cpm_range": (3.0, 7.0),
        "avg_cpm": 4.5,
        "source": "Popular but advertiser-sensitive",
        "parent_category": "entertainment"
    },
    "film_analysis": {
        "keywords": ["film", "movie review", "movie analysis", "cinema", "film essay", "video essay"],
        "cpm_range": (3.0, 7.0),
        "avg_cpm": 4.5,
        "source": "Entertainment tier with educational angle",
        "parent_category": "entertainment"
    },

    # =========================================================================
    # TIER 5: ENTERTAINMENT ($2-6)
    # =========================================================================
    "gaming": {
        "keywords": ["gaming", "video game", "gameplay", "gamer", "esports", "streamer", "lets play", "walkthrough"],
        "cpm_range": (2.0, 6.0),
        "avg_cpm": 3.5,
        "source": "Lenostube, PewDiePie data $2-4 RPM",
        "parent_category": "gaming"
    },
    "entertainment": {
        "keywords": ["entertainment", "reaction", "challenge", "prank", "funny", "viral"],
        "cpm_range": (2.0, 8.0),
        "avg_cpm": 4.0,
        "source": "Lenostube - Mr Beast at $3-5 RPM",
        "parent_category": "entertainment"
    },
    "comedy": {
        "keywords": ["comedy", "funny", "humor", "sketch", "parody", "meme", "satire"],
        "cpm_range": (2.0, 5.0),
        "avg_cpm": 3.0,
        "source": "Lenostube",
        "parent_category": "entertainment"
    },
    "vlogs": {
        "keywords": ["vlog", "daily vlog", "lifestyle vlog", "day in my life", "vlogger"],
        "cpm_range": (2.0, 5.0),
        "avg_cpm": 3.0,
        "source": "Lenostube",
        "parent_category": "entertainment"
    },
    "sports": {
        "keywords": ["sports", "football", "basketball", "soccer", "nba", "nfl", "mlb", "sports highlights"],
        "cpm_range": (2.0, 6.0),
        "avg_cpm": 3.5,
        "source": "General entertainment tier",
        "parent_category": "entertainment"
    },
    "asmr": {
        "keywords": ["asmr", "relaxation", "tingles", "asmr eating", "asmr roleplay"],
        "cpm_range": (2.0, 5.0),
        "avg_cpm": 3.0,
        "source": "Entertainment tier",
        "parent_category": "entertainment"
    },
    "unboxing": {
        "keywords": ["unboxing", "haul", "first impressions", "product review"],
        "cpm_range": (3.0, 7.0),
        "avg_cpm": 4.5,
        "source": "SMBillion",
        "parent_category": "entertainment"
    },

    # =========================================================================
    # ANIME/MANGA/WEBTOON (IMPORTANT CATEGORY)
    # =========================================================================
    "anime": {
        "keywords": ["anime", "anime review", "anime explained", "anime recap", "anime reaction"],
        "cpm_range": (2.0, 5.0),
        "avg_cpm": 3.0,
        "source": "Reddit r/PartneredYoutube",
        "notes": "Similar to entertainment tier",
        "parent_category": "entertainment"
    },
    "manga": {
        "keywords": ["manga", "manga recap", "manga review", "manga explained", "manga reading"],
        "cpm_range": (2.5, 6.0),
        "avg_cpm": 4.0,
        "source": "Reddit - $2.5-6 RPM reported",
        "notes": "Slightly higher than anime due to reading audience",
        "parent_category": "entertainment"
    },
    "manhwa": {
        "keywords": ["manhwa", "manhwa recap", "korean manhwa", "manhwa review", "manhwa explained"],
        "cpm_range": (3.0, 6.0),
        "avg_cpm": 4.5,
        "source": "Outlierkit - $10.45 RPM for top performers",
        "notes": "Growing niche with webtoon adaptations",
        "parent_category": "entertainment"
    },
    "webtoon": {
        "keywords": ["webtoon", "webtoon recap", "solo leveling", "tower of god", "webtoon review"],
        "cpm_range": (3.0, 6.0),
        "avg_cpm": 4.5,
        "source": "Growing with anime adaptations",
        "parent_category": "entertainment"
    },

    # =========================================================================
    # CREATIVE/ARTS
    # =========================================================================
    "art": {
        "keywords": ["art", "drawing", "painting", "illustration", "digital art", "artist", "speedpaint"],
        "cpm_range": (2.0, 6.0),
        "avg_cpm": 3.5,
        "source": "Creative niche, lower commercial intent",
        "parent_category": "creative"
    },
    "music_production": {
        "keywords": ["music production", "beat making", "producing", "fl studio", "ableton", "music tutorial"],
        "cpm_range": (3.0, 7.0),
        "avg_cpm": 4.5,
        "source": "SMBillion",
        "parent_category": "creative"
    },
    "music": {
        "keywords": ["music", "song", "cover", "music video", "musician", "singer", "original song"],
        "cpm_range": (1.0, 4.0),
        "avg_cpm": 2.0,
        "source": "Lenostube - lowest CPM niche",
        "notes": "Copyrighted content issues",
        "parent_category": "entertainment"
    },

    # =========================================================================
    # SPECIAL CATEGORIES
    # =========================================================================
    "kids_content": {
        "keywords": ["kids", "children", "nursery rhyme", "cartoon", "family friendly", "for kids"],
        "cpm_range": (1.0, 4.0),
        "avg_cpm": 2.0,
        "source": "COPPA restrictions limit monetization",
        "notes": "Lower CPM due to ad restrictions",
        "parent_category": "kids"
    },
    "compilation": {
        "keywords": ["compilation", "best of", "top 10", "fails", "wins", "moments"],
        "cpm_range": (1.5, 4.0),
        "avg_cpm": 2.5,
        "source": "Lenostube",
        "notes": "Often demonetized or limited ads",
        "parent_category": "entertainment"
    },
    "shorts_content": {
        "keywords": ["shorts", "short form", "tiktok", "reels", "vertical video"],
        "cpm_range": (0.05, 0.15),
        "avg_cpm": 0.10,
        "source": "YouTube Shorts RPM data",
        "notes": "Shorts have significantly lower CPM",
        "parent_category": "entertainment"
    },
    "podcast": {
        "keywords": ["podcast", "interview", "talk show", "conversation", "discussion"],
        "cpm_range": (3.0, 10.0),
        "avg_cpm": 5.5,
        "source": "Varies by topic",
        "parent_category": "entertainment"
    },
    "documentary": {
        "keywords": ["documentary", "doc", "investigative", "in-depth", "deep dive"],
        "cpm_range": (4.0, 10.0),
        "avg_cpm": 6.0,
        "source": "Education tier",
        "parent_category": "education"
    },
    "luxury": {
        "keywords": ["luxury", "expensive", "millionaire", "billionaire", "rich lifestyle", "supercar"],
        "cpm_range": (5.0, 12.0),
        "avg_cpm": 7.5,
        "source": "Premium audience",
        "parent_category": "lifestyle"
    },
    "outdoor_adventure": {
        "keywords": ["outdoor", "hiking", "camping", "adventure", "survival", "bushcraft"],
        "cpm_range": (3.0, 7.0),
        "avg_cpm": 4.5,
        "source": "Lenostube",
        "parent_category": "lifestyle"
    },
    "fishing_hunting": {
        "keywords": ["fishing", "hunting", "angling", "bass fishing", "deer hunting"],
        "cpm_range": (4.0, 8.0),
        "avg_cpm": 5.5,
        "source": "SMBillion",
        "parent_category": "lifestyle"
    },
}


# =============================================================================
# PARENT CATEGORY FALLBACKS
# =============================================================================

CATEGORY_FALLBACKS: Dict[str, float] = {
    "finance": 12.0,
    "business": 9.0,
    "education": 8.0,
    "technology": 7.0,
    "health": 6.0,
    "lifestyle": 4.5,
    "entertainment": 3.5,
    "creative": 3.5,
    "gaming": 3.0,
    "kids": 2.0,
}


# =============================================================================
# GEOGRAPHIC MULTIPLIERS (Based on US = 1.0)
# =============================================================================

GEOGRAPHIC_MULTIPLIERS: Dict[str, float] = {
    # Tier 1: Premium Markets
    "AU": 1.10,   # Australia - $36.21 avg CPM
    "US": 1.00,   # United States - $32.75 avg CPM (baseline)
    "CA": 0.90,   # Canada - $29.15 avg CPM
    "NO": 0.85,   # Norway
    "CH": 0.85,   # Switzerland
    "NZ": 0.80,   # New Zealand
    
    # Tier 2: Strong Western Markets
    "GB": 0.65,   # United Kingdom - $21.59 avg CPM
    "UK": 0.65,   # United Kingdom (alt code)
    "DE": 0.60,   # Germany
    "AT": 0.58,   # Austria
    "NL": 0.55,   # Netherlands
    "SE": 0.55,   # Sweden
    "DK": 0.55,   # Denmark
    "FI": 0.50,   # Finland
    "BE": 0.50,   # Belgium
    "IE": 0.55,   # Ireland
    "FR": 0.50,   # France
    
    # Tier 3: Moderate Markets
    "ES": 0.40,   # Spain
    "IT": 0.40,   # Italy
    "PT": 0.35,   # Portugal
    "JP": 0.45,   # Japan
    "KR": 0.40,   # South Korea
    "SG": 0.45,   # Singapore
    "HK": 0.40,   # Hong Kong
    "TW": 0.35,   # Taiwan
    "IL": 0.45,   # Israel
    "AE": 0.50,   # UAE
    "SA": 0.45,   # Saudi Arabia
    
    # Tier 4: Developing Markets
    "MX": 0.15,   # Mexico
    "BR": 0.12,   # Brazil
    "AR": 0.10,   # Argentina
    "CL": 0.15,   # Chile
    "CO": 0.10,   # Colombia
    "PL": 0.20,   # Poland
    "CZ": 0.20,   # Czech Republic
    "RU": 0.08,   # Russia
    "TR": 0.10,   # Turkey
    "ZA": 0.15,   # South Africa
    "EG": 0.05,   # Egypt
    "NG": 0.03,   # Nigeria
    "KE": 0.04,   # Kenya
    
    # Tier 5: Low CPM Markets
    "IN": 0.025,  # India - $0.83 avg CPM
    "PH": 0.015,  # Philippines - $0.48 avg CPM
    "PK": 0.011,  # Pakistan
    "BD": 0.02,   # Bangladesh
    "ID": 0.025,  # Indonesia
    "VN": 0.02,   # Vietnam
    "TH": 0.03,   # Thailand
    "MY": 0.05,   # Malaysia
}


# =============================================================================
# SEASONAL MULTIPLIERS
# =============================================================================

SEASONAL_MULTIPLIERS: Dict[int, float] = {
    1: 0.65,   # January - Post-holiday budget reset (lowest)
    2: 0.75,   # February - Recovering
    3: 0.90,   # March - Q1 end spending
    4: 1.10,   # April - Q2 budgets kick in
    5: 1.10,   # May - Stable
    6: 0.95,   # June - Pre-summer
    7: 0.75,   # July - Summer slump
    8: 0.70,   # August - Lowest summer point
    9: 0.85,   # September - Back to school
    10: 1.15,  # October - Q4 begins
    11: 1.30,  # November - Pre-holiday surge
    12: 1.50,  # December - Holiday peak (highest)
}


# =============================================================================
# GLOBAL DEFAULT
# =============================================================================

DEFAULT_CPM: float = 3.50  # Based on global YouTube average across all niches


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_all_keywords() -> List[str]:
    """Get a flat list of all keywords for fuzzy matching."""
    keywords = []
    for category_data in CPM_DATABASE.values():
        keywords.extend(category_data["keywords"])
    return keywords


def get_keyword_to_category_map() -> Dict[str, str]:
    """Build a map from keyword to category name."""
    mapping = {}
    for category_name, category_data in CPM_DATABASE.items():
        for keyword in category_data["keywords"]:
            mapping[keyword.lower()] = category_name
    return mapping


def get_category_count() -> int:
    """Return the total number of categories."""
    return len(CPM_DATABASE)


def get_keyword_count() -> int:
    """Return the total number of keywords."""
    return sum(len(data["keywords"]) for data in CPM_DATABASE.values())
