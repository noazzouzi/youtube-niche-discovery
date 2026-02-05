"""
Recommendation Engine Module for YouTube Niche Discovery Engine

This module generates and scores niche recommendations using a two-phase approach
to find related niches that might score better than the original.
"""

import logging
from typing import List, Set

from .scorer import NicheScorer

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generate and score niche recommendations"""
    
    def __init__(self, niche_scorer: NicheScorer):
        self.niche_scorer = niche_scorer
        logger.info("RecommendationEngine initialized")
    
    def get_recommendations(self, original_niche: str, original_score: float, max_recommendations: int = 8) -> List[dict]:
        """Get scored recommendations using two-phase approach"""
        logger.info(f"Generating recommendations for: {original_niche}")
        
        # Generate related niches
        related_niches = self._generate_related_niches(original_niche)
        
        # Phase 1: Quick score ALL candidates
        logger.info("Phase 1: Quick scoring all candidates...")
        candidates = []
        for niche in related_niches[:max_recommendations]:
            try:
                quick_score = self.niche_scorer.quick_score(niche)
                candidates.append({
                    'niche': niche,
                    'score': quick_score,
                    'better': quick_score > original_score
                })
            except Exception as e:
                logger.warning(f"Quick score error for {niche}: {e}")
        
        # Sort by quick score and take top candidates for Phase 2
        candidates.sort(key=lambda x: x['score'], reverse=True)
        top_candidates = candidates[:3]  # Only full-score top 3
        
        # Phase 2: Full scoring for top 3
        logger.info("Phase 2: Full scoring for top 3 candidates...")
        final_recommendations = []
        
        for candidate in top_candidates:
            try:
                # Get full score with real APIs
                full_result = self.niche_scorer.full_score(candidate['niche'])
                final_recommendations.append({
                    'niche': candidate['niche'],
                    'score': full_result['total_score'],
                    'better': full_result['total_score'] > original_score,
                    'confidence': 'HIGH (Real APIs)'
                })
            except Exception as e:
                logger.warning(f"Full score error for {candidate['niche']}: {e}")
                # Fallback to quick score
                final_recommendations.append({
                    'niche': candidate['niche'],
                    'score': candidate['score'],
                    'better': candidate['better'],
                    'confidence': 'ESTIMATED'
                })
        
        # Add remaining candidates with quick scores
        remaining_candidates = candidates[3:5]  # Take 2 more with quick scores
        for candidate in remaining_candidates:
            final_recommendations.append({
                'niche': candidate['niche'],
                'score': candidate['score'],
                'better': candidate['better'],
                'confidence': 'ESTIMATED'
            })
        
        # Sort by score
        final_recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        logger.info(f"Generated {len(final_recommendations)} recommendations")
        return final_recommendations[:5]  # Return top 5
    
    def _generate_related_niches(self, original_niche: str) -> List[str]:
        """Generate related niche variations"""
        niche_lower = original_niche.lower()
        related_niches: Set[str] = set()
        
        # Synonym substitutions
        synonyms = {
            'tv show': ['drama', 'series', 'television', 'show'],
            'tutorial': ['guide', 'how to', 'lesson', 'course'],
            'tips': ['advice', 'hacks', 'guide', 'tricks'],
            'review': ['analysis', 'breakdown', 'reaction'],
            'beginner': ['starter', 'newbie', 'basic', 'intro'],
            'ai': ['artificial intelligence', 'machine learning', 'chatgpt'],
            'crypto': ['cryptocurrency', 'bitcoin', 'blockchain']
        }
        
        # Generate variations
        for original_word, replacements in synonyms.items():
            if original_word in niche_lower:
                for replacement in replacements:
                    variant = niche_lower.replace(original_word, replacement)
                    if variant != niche_lower and len(variant) > 3:
                        related_niches.add(variant)
        
        # Content type variations
        content_types = [
            'reviews', 'tutorial', 'guide', 'tips', 'for beginners',
            'analysis', 'explained', '2024', 'how to'
        ]
        
        base_words = niche_lower.split()
        if base_words:
            clean_base = ' '.join([w for w in base_words 
                                 if w not in ['tutorial', 'tips', 'guide', 'how', 'to']])
            
            for content_type in content_types:
                if content_type not in niche_lower:
                    variants = [f"{clean_base} {content_type}", f"{content_type} {clean_base}"]
                    for variant in variants:
                        if len(variant.strip()) > 3:
                            related_niches.add(variant.strip())
        
        result = list(related_niches)[:12]
        logger.debug(f"Generated {len(result)} related niches")
        return result