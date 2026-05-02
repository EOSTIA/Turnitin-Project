from config import HIGH_PLAGIARISM_THRESHOLD, AI_HIGH_THRESHOLD, AI_MEDIUM_THRESHOLD

def refinement_suggestions(plagiarism, ai_score, human_contribution=None, citations=None):
    """
    Generate detailed, actionable refinement suggestions based on scores.
    
    Args:
        plagiarism: Plagiarism score (0-1)
        ai_score: AI detection score (0-1)
        human_contribution: Human contribution score (0-1)
        citations: Number of citations
    
    Returns:
        List of detailed suggestions
    """
    suggestions = []
    priority_level = "LOW"
    
    # Plagiarism-specific suggestions
    if plagiarism > 0.7:
        priority_level = "CRITICAL"
        suggestions.append({
            "category": "Plagiarism",
            "severity": "Critical",
            "issue": f"Very high plagiarism detected ({plagiarism:.1%})",
            "actions": [
                "Completely rewrite the content in your own words",
                "Add proper citations for all borrowed ideas",
                "Ensure paraphrasing is substantive, not just word substitution",
                "Consider removing this section if it cannot be properly attributed"
            ]
        })
    elif plagiarism > 0.4:
        priority_level = "HIGH" if priority_level != "CRITICAL" else priority_level
        suggestions.append({
            "category": "Plagiarism",
            "severity": "High",
            "issue": f"Significant plagiarism detected ({plagiarism:.1%})",
            "actions": [
                "Rephrase content using original language and reasoning",
                "Add citations for any borrowed concepts or data",
                "Incorporate your own analysis and interpretation",
                "Use quotation marks for any direct quotes"
            ]
        })
    elif plagiarism > 0.25:
        priority_level = "MEDIUM" if priority_level not in ["CRITICAL", "HIGH"] else priority_level
        suggestions.append({
            "category": "Plagiarism",
            "severity": "Medium",
            "issue": f"Moderate plagiarism detected ({plagiarism:.1%})",
            "actions": [
                "Review for potential uncited sources",
                "Ensure proper paraphrasing of referenced material",
                "Add citations where needed"
            ]
        })
    
    # AI-generated content suggestions
    if ai_score > 0.7:
        priority_level = "CRITICAL"
        suggestions.append({
            "category": "AI Detection",
            "severity": "Critical",
            "issue": f"Very high AI-generated content probability ({ai_score:.1%})",
            "actions": [
                "Add personal insights, experiences, and unique perspectives",
                "Include specific examples from your own research or analysis",
                "Vary sentence structure and length more naturally",
                "Add domain-specific nuances that reflect deep understanding",
                "Include critical evaluation and original argumentation",
                "Remove generic, templated language"
            ]
        })
    elif ai_score > 0.6:
        priority_level = "HIGH" if priority_level != "CRITICAL" else priority_level
        suggestions.append({
            "category": "AI Detection",
            "severity": "High",
            "issue": f"High AI-generated content probability ({ai_score:.1%})",
            "actions": [
                "Increase human contribution with interpretation and critique",
                "Add specific, concrete examples from your research",
                "Incorporate personal analysis and comparison",
                "Use more varied and natural language patterns",
                "Add rhetorical questions or conversational elements where appropriate"
            ]
        })
    elif ai_score > 0.35:
        priority_level = "MEDIUM" if priority_level not in ["CRITICAL", "HIGH"] else priority_level
        suggestions.append({
            "category": "AI Detection",
            "severity": "Medium",
            "issue": f"Moderate AI-generated content indicators ({ai_score:.1%})",
            "actions": [
                "Add more personal voice and writing style",
                "Include specific examples and evidence",
                "Vary sentence structure for more natural flow",
                "Add transitional phrases that reflect your thinking process"
            ]
        })
    
    # Citation-related suggestions
    if citations is not None:
        if citations == 0 and plagiarism > 0.2:
            suggestions.append({
                "category": "Citations",
                "severity": "High",
                "issue": "No citations found despite similarity to existing work",
                "actions": [
                    "Add proper citations for all referenced material",
                    "Use consistent citation format",
                    "Ensure all data, concepts, and ideas are properly attributed"
                ]
            })
        elif citations < 2 and plagiarism > 0.3:
            suggestions.append({
                "category": "Citations",
                "severity": "Medium",
                "issue": "Insufficient citations given the content overlap",
                "actions": [
                    "Review content for additional sources that should be cited",
                    "Ensure all borrowed ideas are properly attributed"
                ]
            })
    
    # Human contribution suggestions
    if human_contribution is not None and human_contribution < 0.4:
        priority_level = "HIGH" if priority_level not in ["CRITICAL"] else priority_level
        suggestions.append({
            "category": "Human Contribution",
            "severity": "High",
            "issue": f"Low human contribution score ({human_contribution:.1%})",
            "actions": [
                "Add original analysis and critical thinking",
                "Include your unique perspective on the topic",
                "Synthesize information in novel ways",
                "Add practical implications or applications",
                "Include case studies or real-world examples from your experience"
            ]
        })
    elif human_contribution is not None and human_contribution < 0.6:
        priority_level = "MEDIUM" if priority_level not in ["CRITICAL", "HIGH"] else priority_level
        suggestions.append({
            "category": "Human Contribution",
            "severity": "Medium",
            "issue": f"Moderate human contribution ({human_contribution:.1%})",
            "actions": [
                "Strengthen original analysis",
                "Add more critical evaluation",
                "Include additional examples or evidence"
            ]
        })
    
    # Combined issues
    if plagiarism > 0.4 and ai_score > 0.6:
        suggestions.append({
            "category": "Combined Issues",
            "severity": "Critical",
            "issue": "Both high plagiarism and AI detection scores",
            "actions": [
                "This section requires complete revision",
                "Start from scratch with original writing",
                "Focus on your unique insights and analysis",
                "Properly cite any referenced material",
                "Consult with academic integrity guidelines"
            ]
        })
    
    # If no issues found
    if not suggestions:
        suggestions.append({
            "category": "Quality",
            "severity": "Good",
            "issue": "No major integrity issues detected",
            "actions": [
                "Content appears original and properly cited",
                "Consider minor copyediting for clarity",
                "Verify all citations are formatted correctly"
            ]
        })
        priority_level = "LOW"
    
    return {
        "priority": priority_level,
        "suggestions": suggestions,
        "overall_assessment": get_overall_assessment(plagiarism, ai_score, human_contribution)
    }

def get_overall_assessment(plagiarism, ai_score, human_contribution):
    """
    Provide an overall assessment of the content.
    """
    if plagiarism > 0.7 or ai_score > 0.7:
        return "REQUIRES MAJOR REVISION - Serious integrity concerns detected"
    elif plagiarism > 0.4 or ai_score > 0.6:
        return "NEEDS IMPROVEMENT - Significant revisions recommended"
    elif plagiarism > 0.25 or ai_score > 0.35:
        return "ACCEPTABLE WITH REVISIONS - Minor improvements needed"
    elif human_contribution and human_contribution < 0.5:
        return "GOOD - Consider adding more original analysis"
    else:
        return "EXCELLENT - Content shows strong originality and proper attribution"
