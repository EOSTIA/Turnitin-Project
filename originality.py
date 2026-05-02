from config import AI_PENALTY_FACTOR
import math

class OriginalityScorer:
    """
    Calculate originality score based on plagiarism and AI detection.
    Higher scores indicate more original content.
    """
    
    def calculate_plagiarism_penalty(self, plagiarism):
        """
        Calculate penalty from plagiarism score.
        Uses non-linear scaling to heavily penalize high plagiarism.
        """
        if plagiarism > 0.7:
            # Exponential penalty for very high plagiarism
            return 1.0 - math.exp(-3 * plagiarism)
        elif plagiarism > 0.4:
            # Strong penalty for high plagiarism
            return plagiarism * 1.2
        else:
            # Linear for low plagiarism
            return plagiarism
    
    def calculate_ai_penalty(self, ai_score):
        """
        Calculate penalty from AI detection score.
        AI-generated content gets a penalty but slightly less severe than plagiarism.
        """
        # AI penalty is scaled by AI_PENALTY_FACTOR (default 0.7)
        base_penalty = ai_score * AI_PENALTY_FACTOR
        
        # Additional penalty for very high AI scores
        if ai_score > 0.7:
            base_penalty += (ai_score - 0.7) * 0.3
        
        return min(base_penalty, 1.0)
    
    def score(self, plagiarism, ai_score):
        """
        Calculate originality score.
        
        Args:
            plagiarism: Plagiarism score (0-1)
            ai_score: AI detection score (0-1)
        
        Returns:
            Originality score (0-1, higher = more original)
        """
        # Calculate individual penalties
        plag_penalty = self.calculate_plagiarism_penalty(plagiarism)
        ai_penalty = self.calculate_ai_penalty(ai_score)
        
        # Use the maximum penalty (worst of the two)
        # This ensures that high plagiarism OR high AI detection lowers originality
        max_penalty = max(plag_penalty, ai_penalty)
        
        # Calculate originality (1 - penalty)
        originality = 1.0 - max_penalty
        
        # Ensure score is in valid range
        originality = max(0.0, min(originality, 1.0))
        
        return originality
    
    def get_originality_level(self, score):
        """
        Get qualitative assessment of originality.
        
        Args:
            score: Originality score (0-1)
        
        Returns:
            String describing the originality level
        """
        if score >= 0.85:
            return "Exceptional - Highly original work"
        elif score >= 0.70:
            return "Excellent - Strong originality"
        elif score >= 0.55:
            return "Good - Adequate originality"
        elif score >= 0.40:
            return "Fair - Some concerns about originality"
        elif score >= 0.25:
            return "Poor - Significant originality issues"
        else:
            return "Very Poor - Severe originality concerns"
    
    def get_detailed_analysis(self, plagiarism, ai_score):
        """
        Get detailed originality analysis.
        
        Args:
            plagiarism: Plagiarism score (0-1)
            ai_score: AI detection score (0-1)
        
        Returns:
            Dictionary with detailed analysis
        """
        originality = self.score(plagiarism, ai_score)
        
        return {
            'originality_score': round(originality, 3),
            'originality_level': self.get_originality_level(originality),
            'plagiarism_impact': round(self.calculate_plagiarism_penalty(plagiarism), 3),
            'ai_impact': round(self.calculate_ai_penalty(ai_score), 3),
            'primary_concern': 'plagiarism' if plagiarism > ai_score * AI_PENALTY_FACTOR else 'ai_generation' if ai_score > 0.3 else 'none'
        }
