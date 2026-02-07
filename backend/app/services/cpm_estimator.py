"""
CPM Estimator Service
Provides accurate CPM estimation with fuzzy matching, geographic adjustments, and seasonal modifiers.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from app.data.cpm_database import (
    CPM_DATABASE,
    CATEGORY_FALLBACKS,
    GEOGRAPHIC_MULTIPLIERS,
    SEASONAL_MULTIPLIERS,
    DEFAULT_CPM,
    get_all_keywords,
    get_keyword_to_category_map,
)

logger = logging.getLogger(__name__)

# Try to import rapidfuzz for better matching, fall back to basic if unavailable
try:
    from rapidfuzz import fuzz, process
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False
    logger.warning("rapidfuzz not installed, using basic string matching")


class CPMEstimator:
    """
    Advanced CPM estimation with hierarchical fuzzy matching.
    
    Features:
    - Exact keyword matching
    - Fuzzy matching (if rapidfuzz available)
    - Category-based fallbacks
    - Geographic multipliers (35+ countries)
    - Seasonal adjustments (Q4 peak, Jan low)
    """
    
    def __init__(self):
        self.db = CPM_DATABASE
        self.keyword_to_category = get_keyword_to_category_map()
        self.all_keywords = list(self.keyword_to_category.keys())
        logger.info(f"CPMEstimator initialized with {len(self.db)} categories, {len(self.all_keywords)} keywords")
    
    def estimate_cpm(
        self,
        niche_name: str,
        niche_category: Optional[str] = None,
        country_code: str = "US",
        apply_seasonal: bool = True,
        apply_geographic: bool = True,
    ) -> Dict[str, Any]:
        """
        Estimate CPM using multi-level matching.
        
        Args:
            niche_name: The niche/topic name (e.g., "manga recap channel")
            niche_category: Optional category hint
            country_code: Viewer country for geographic adjustment (default: US)
            apply_seasonal: Whether to apply seasonal multipliers
            apply_geographic: Whether to apply geographic multipliers
            
        Returns:
            dict with:
                - cpm: Estimated CPM (adjusted)
                - cpm_range: (min, max) tuple
                - base_cpm: CPM before adjustments
                - confidence: 0.0-1.0 score
                - source: Data source citation
                - match_type: How the match was made
                - category: Matched category name
                - adjustments: Dict of applied multipliers
        """
        niche_lower = niche_name.lower().strip()
        niche_words = set(re.findall(r'\b\w+\b', niche_lower))
        
        # Level 1: Exact keyword match
        result = self._exact_match(niche_words, niche_lower)
        if result:
            return self._apply_adjustments(result, country_code, apply_seasonal, apply_geographic)
        
        # Level 2: Fuzzy keyword match (85%+ similarity)
        if HAS_RAPIDFUZZ:
            result = self._fuzzy_match(niche_lower)
            if result:
                return self._apply_adjustments(result, country_code, apply_seasonal, apply_geographic)
        
        # Level 3: Substring match (fallback fuzzy)
        result = self._substring_match(niche_lower)
        if result:
            return self._apply_adjustments(result, country_code, apply_seasonal, apply_geographic)
        
        # Level 4: Category-based fallback
        if niche_category:
            result = self._category_fallback(niche_category)
            if result:
                return self._apply_adjustments(result, country_code, apply_seasonal, apply_geographic)
        
        # Level 5: Infer category from niche name
        result = self._infer_category(niche_lower)
        if result:
            return self._apply_adjustments(result, country_code, apply_seasonal, apply_geographic)
        
        # Level 6: Default with low confidence
        return self._apply_adjustments({
            "cpm": DEFAULT_CPM,
            "cpm_range": (2.0, 5.0),
            "base_cpm": DEFAULT_CPM,
            "confidence": 0.3,
            "source": "Global YouTube average",
            "match_type": "default",
            "category": "unknown",
        }, country_code, apply_seasonal, apply_geographic)
    
    def _exact_match(self, niche_words: set, niche_lower: str) -> Optional[Dict[str, Any]]:
        """Check for exact keyword matches in the niche name."""
        best_match = None
        best_match_score = 0
        
        for category, data in self.db.items():
            for keyword in data["keywords"]:
                kw_lower = keyword.lower()
                kw_words = set(kw_lower.split())
                
                # Full phrase match - keyword is contained in niche
                if kw_lower in niche_lower:
                    # Score by length of matched keyword (longer = better)
                    score = len(kw_lower)
                    if score > best_match_score:
                        best_match = (category, data, keyword, "exact")
                        best_match_score = score
                
                # Word overlap match
                elif kw_words.issubset(niche_words):
                    score = len(kw_words)
                    if score > best_match_score:
                        best_match = (category, data, keyword, "exact_words")
                        best_match_score = score
        
        if best_match:
            cat, data, matched_kw, match_type = best_match
            return {
                "cpm": data["avg_cpm"],
                "cpm_range": data["cpm_range"],
                "base_cpm": data["avg_cpm"],
                "confidence": 0.95 if match_type == "exact" else 0.90,
                "source": data.get("source", "CPM Database"),
                "match_type": match_type,
                "category": cat,
                "matched_keyword": matched_kw,
            }
        return None
    
    def _fuzzy_match(self, niche_lower: str, threshold: int = 80) -> Optional[Dict[str, Any]]:
        """Fuzzy match against all keywords using rapidfuzz."""
        if not HAS_RAPIDFUZZ:
            return None
        
        try:
            # Use token_set_ratio for better partial matching
            matches = process.extract(
                niche_lower,
                self.all_keywords,
                scorer=fuzz.token_set_ratio,
                limit=3
            )
            
            if matches and matches[0][1] >= threshold:
                best_keyword = matches[0][0]
                match_score = matches[0][1]
                category = self.keyword_to_category[best_keyword]
                data = self.db[category]
                
                # Confidence scales with match score
                confidence = (match_score / 100) * 0.85
                
                return {
                    "cpm": data["avg_cpm"],
                    "cpm_range": data["cpm_range"],
                    "base_cpm": data["avg_cpm"],
                    "confidence": confidence,
                    "source": data.get("source", "CPM Database"),
                    "match_type": f"fuzzy ({match_score}%)",
                    "category": category,
                    "matched_keyword": best_keyword,
                }
        except Exception as e:
            logger.warning(f"Fuzzy match error: {e}")
        
        return None
    
    def _substring_match(self, niche_lower: str) -> Optional[Dict[str, Any]]:
        """Simple substring matching as fallback."""
        best_match = None
        best_match_len = 0
        
        for keyword in self.all_keywords:
            # Check if keyword appears in niche or vice versa
            if keyword in niche_lower or niche_lower in keyword:
                if len(keyword) > best_match_len:
                    best_match = keyword
                    best_match_len = len(keyword)
            # Also check individual words
            else:
                kw_words = keyword.split()
                for word in kw_words:
                    if len(word) > 3 and word in niche_lower:
                        if len(word) > best_match_len:
                            best_match = keyword
                            best_match_len = len(word)
        
        if best_match:
            category = self.keyword_to_category[best_match]
            data = self.db[category]
            return {
                "cpm": data["avg_cpm"],
                "cpm_range": data["cpm_range"],
                "base_cpm": data["avg_cpm"],
                "confidence": 0.70,
                "source": data.get("source", "CPM Database"),
                "match_type": "substring",
                "category": category,
                "matched_keyword": best_match,
            }
        return None
    
    def _category_fallback(self, category: str) -> Optional[Dict[str, Any]]:
        """Fall back to parent category-level CPM."""
        cat_lower = category.lower()
        
        for fallback_cat, fallback_cpm in CATEGORY_FALLBACKS.items():
            if fallback_cat in cat_lower or cat_lower in fallback_cat:
                return {
                    "cpm": fallback_cpm,
                    "cpm_range": (fallback_cpm * 0.7, fallback_cpm * 1.3),
                    "base_cpm": fallback_cpm,
                    "confidence": 0.60,
                    "source": f"Category fallback ({fallback_cat})",
                    "match_type": "category",
                    "category": fallback_cat,
                }
        return None
    
    def _infer_category(self, niche_lower: str) -> Optional[Dict[str, Any]]:
        """Try to infer category from common words in niche name."""
        # Map of common words to parent categories
        category_hints = {
            "money": "finance",
            "earn": "finance",
            "invest": "finance",
            "stock": "finance",
            "bank": "finance",
            "wealth": "finance",
            "game": "gaming",
            "play": "gaming",
            "stream": "gaming",
            "tech": "technology",
            "code": "technology",
            "program": "technology",
            "software": "technology",
            "app": "technology",
            "health": "health",
            "fit": "health",
            "diet": "health",
            "workout": "health",
            "learn": "education",
            "teach": "education",
            "course": "education",
            "school": "education",
            "vlog": "entertainment",
            "react": "entertainment",
            "funny": "entertainment",
            "comedy": "entertainment",
            "anime": "entertainment",
            "manga": "entertainment",
            "cook": "lifestyle",
            "recipe": "lifestyle",
            "travel": "lifestyle",
            "beauty": "lifestyle",
            "fashion": "lifestyle",
            "draw": "creative",
            "art": "creative",
            "music": "creative",
            "paint": "creative",
            "kid": "kids",
            "child": "kids",
            "nursery": "kids",
            "business": "business",
            "market": "business",
            "sell": "business",
        }
        
        niche_words = niche_lower.split()
        for word in niche_words:
            for hint, category in category_hints.items():
                if hint in word:
                    return self._category_fallback(category)
        
        return None
    
    def _apply_adjustments(
        self,
        result: Dict[str, Any],
        country_code: str,
        apply_seasonal: bool,
        apply_geographic: bool,
    ) -> Dict[str, Any]:
        """Apply geographic and seasonal adjustments to CPM estimate."""
        
        base_cpm = result["cpm"]
        geo_mult = 1.0
        seasonal_mult = 1.0
        
        # Geographic multiplier
        if apply_geographic:
            geo_mult = GEOGRAPHIC_MULTIPLIERS.get(country_code.upper(), 0.5)
        
        # Seasonal multiplier
        if apply_seasonal:
            month = datetime.now().month
            seasonal_mult = SEASONAL_MULTIPLIERS.get(month, 1.0)
        
        # Apply multipliers
        adjusted_cpm = base_cpm * geo_mult * seasonal_mult
        adjusted_range = (
            result["cpm_range"][0] * geo_mult * seasonal_mult,
            result["cpm_range"][1] * geo_mult * seasonal_mult,
        )
        
        result["cpm"] = round(adjusted_cpm, 2)
        result["cpm_range"] = (round(adjusted_range[0], 2), round(adjusted_range[1], 2))
        result["adjustments"] = {
            "geographic_multiplier": geo_mult,
            "seasonal_multiplier": seasonal_mult,
            "country": country_code.upper(),
            "month": datetime.now().month,
        }
        
        return result
    
    def get_cpm_for_category(self, category: str) -> float:
        """Get the average CPM for a specific category name."""
        category_lower = category.lower().replace(" ", "_").replace("-", "_")
        
        # Direct category match
        if category_lower in self.db:
            return self.db[category_lower]["avg_cpm"]
        
        # Fallback to parent category
        for parent, fallback_cpm in CATEGORY_FALLBACKS.items():
            if parent in category_lower:
                return fallback_cpm
        
        return DEFAULT_CPM
    
    def get_cpm_tier(self, cpm: float) -> str:
        """Get the tier name based on CPM value."""
        if cpm >= 15:
            return "ultra_premium"
        elif cpm >= 8:
            return "premium"
        elif cpm >= 5:
            return "moderate_high"
        elif cpm >= 3:
            return "moderate"
        else:
            return "entertainment"
    
    def list_categories(self) -> List[Dict[str, Any]]:
        """List all categories with their CPM data."""
        result = []
        for name, data in self.db.items():
            result.append({
                "name": name,
                "avg_cpm": data["avg_cpm"],
                "cpm_range": data["cpm_range"],
                "keywords": data["keywords"][:3],  # First 3 keywords
                "source": data.get("source", ""),
            })
        return sorted(result, key=lambda x: x["avg_cpm"], reverse=True)


# Singleton instance for easy import
_estimator_instance: Optional[CPMEstimator] = None


def get_cpm_estimator() -> CPMEstimator:
    """Get or create the singleton CPMEstimator instance."""
    global _estimator_instance
    if _estimator_instance is None:
        _estimator_instance = CPMEstimator()
    return _estimator_instance


def estimate_cpm(
    niche_name: str,
    niche_category: Optional[str] = None,
    country_code: str = "US",
) -> Dict[str, Any]:
    """Convenience function to estimate CPM without instantiating the class."""
    estimator = get_cpm_estimator()
    return estimator.estimate_cpm(niche_name, niche_category, country_code)
