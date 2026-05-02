import math
from config import (
    HUMAN_REWRITE_WEIGHT,
    HUMAN_NOVELTY_WEIGHT,
    HUMAN_ETHICAL_WEIGHT
)

class HumanContribution:
    """
    Calculate human contribution score based on multiple factors.
    Higher scores indicate more human involvement and original work.
    """
    
    def calculate_novelty_score(self, citations):
        """
        Calculate novelty based on citations.
        More citations can indicate research depth, but too many might indicate over-reliance.
        """
        if isinstance(citations, list):
            num_citations = len(citations)
        else:
            num_citations = int(citations) if citations else 0
        
        # Optimal citation range: 3-7 citations per paragraph shows good research
        if num_citations == 0:
            return 0.0
        elif num_citations <= 3:
            return min(num_citations / 3.0, 1.0)
        elif num_citations <= 7:
            return 1.0  # Optimal range
        else:
            # Diminishing returns after 7 citations
            return max(1.0 - (num_citations - 7) * 0.05, 0.5)
    
    def calculate_rewrite_depth(self, ai_score):
        """
        Calculate how much the text has been rewritten by a human.
        Lower AI score = higher rewrite depth.
        """
        # Non-linear relationship - heavily penalize high AI scores
        rewrite = 1 - ai_score
        
        # Apply sigmoid-like transformation for better differentiation
        # This makes the score more sensitive in the critical 0.4-0.7 AI range
        if ai_score > 0.7:
            rewrite = rewrite * 0.5  # Heavy penalty for very high AI
        elif ai_score > 0.5:
            rewrite = rewrite * 0.8  # Moderate penalty
        
        return max(rewrite, 0.0)
    
    def calculate_ethical_score(self, plagiarism):
        """
        Calculate ethical score based on plagiarism.
        Lower plagiarism = higher ethical score.
        """
        # Non-linear penalty for plagiarism
        ethical = 1 - plagiarism
        
        # Apply heavier penalty for high plagiarism
        if plagiarism > 0.6:
            ethical = ethical * 0.3  # Severe penalty
        elif plagiarism > 0.4:
            ethical = ethical * 0.6  # Moderate penalty
        
        return max(ethical, 0.0)
    
    def calculate_consistency_bonus(self, plagiarism, ai_score):
        """
        Bonus for consistent low scores (both plagiarism and AI are low).
        This rewards genuinely original work.
        """
        if plagiarism < 0.2 and ai_score < 0.3:
            return 0.1  # 10% bonus for excellent work
        elif plagiarism < 0.3 and ai_score < 0.4:
            return 0.05  # 5% bonus for good work
        return 0.0
    
    def score(self, plagiarism, ai_score, citations):
        """
        Calculate comprehensive human contribution score.
        
        Args:
            plagiarism: Plagiarism score (0-1, higher = more plagiarism)
            ai_score: AI detection score (0-1, higher = more likely AI)
            citations: List of citations or count
        
        Returns:
            Human contribution score (0-1, higher = more human contribution)
        """
        # Normalize citations input
        if isinstance(citations, list):
            citations = len(citations)
        elif citations is None:
            citations = 0
        
        # Calculate individual components
        novelty = self.calculate_novelty_score(citations)
        rewrite_depth = self.calculate_rewrite_depth(ai_score)
        ethical = self.calculate_ethical_score(plagiarism)
        
        # Calculate weighted score
        base_score = (
            HUMAN_REWRITE_WEIGHT * rewrite_depth +
            HUMAN_NOVELTY_WEIGHT * novelty +
            HUMAN_ETHICAL_WEIGHT * ethical
        )
        
        # Add consistency bonus
        consistency_bonus = self.calculate_consistency_bonus(plagiarism, ai_score)
        final_score = min(base_score + consistency_bonus, 1.0)
        
        return max(final_score, 0.0)  # Ensure score is in [0, 1]
    
    def get_contribution_level(self, score):
        """
        Get qualitative assessment of human contribution.
        
        Args:
            score: Human contribution score (0-1)
        
        Returns:
            String describing the contribution level
        """
        if score >= 0.8:
            return "Excellent - High human contribution"
        elif score >= 0.65:
            return "Good - Substantial human contribution"
        elif score >= 0.5:
            return "Moderate - Adequate human contribution"
        elif score >= 0.35:
            return "Low - Limited human contribution"
        else:
            return "Very Low - Minimal human contribution"
