from difflib import SequenceMatcher
import re
import numpy as np
from config import (
    SEMANTIC_THRESHOLD, 
    LEXICAL_THRESHOLD,
    HIGH_PLAGIARISM_THRESHOLD,
    CITATION_BONUS_FACTOR,
    VECTOR_SEARCH_K
)

class PlagiarismEngine:
    def __init__(self):
        self.cache = {}
    
    def lexical_similarity(self, a, b):
        """Calculate lexical similarity using SequenceMatcher."""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def ngram_overlap(self, text1, text2, n=3):
        """Calculate n-gram overlap between two texts."""
        def get_ngrams(text, n):
            words = text.lower().split()
            return set([' '.join(words[i:i+n]) for i in range(len(words)-n+1)])
        
        ngrams1 = get_ngrams(text1, n)
        ngrams2 = get_ngrams(text2, n)
        
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = len(ngrams1 & ngrams2)
        union = len(ngrams1 | ngrams2)
        
        return intersection / union if union > 0 else 0.0
    
    def semantic_score(self, embedding, store):
        """Calculate semantic similarity using vector store."""
        results = store.search(embedding, k=VECTOR_SEARCH_K)
        if not results:
            return 0.0
        
        # Use weighted average of top matches
        scores = [r[0] for r in results]
        weights = np.exp(-np.arange(len(scores)))  # Exponential decay
        weighted_score = np.average(scores, weights=weights)
        
        return weighted_score
    
    def detect_verbatim_copying(self, text, store, threshold=15):
        """Detect verbatim copying of long sequences."""
        words = text.split()
        max_match_length = 0
        
        for i in range(len(words)):
            for j in range(i + threshold, len(words) + 1):
                phrase = ' '.join(words[i:j])
                # Check if this phrase exists in corpus
                for corpus_text in store.texts:
                    if phrase.lower() in corpus_text.lower():
                        max_match_length = max(max_match_length, j - i)
        
        # Normalize by document length
        return min(max_match_length / len(words), 1.0) if words else 0.0
    
    def calculate_plagiarism_details(self, paragraph, embedding, store):
        """Calculate detailed plagiarism metrics."""
        text = paragraph["text"]
        
        # Get top matches for detailed analysis
        all_matches = store.search(embedding, k=5)
        
        # Filter out self-matches (lexical similarity > 0.95 indicates same or identical text)
        top_matches = []
        for score, match_text in all_matches:
            lexical_sim = self.lexical_similarity(text, match_text)
            # Skip self-matches (identical or near-identical text)
            if lexical_sim < 0.95:
                top_matches.append((score, match_text))
            if len(top_matches) >= 3:
                break
        
        # If all matches were self-matches, return zero plagiarism
        # (this indicates the corpus is self-referential)
        if not top_matches:
            return {
                'semantic': 0.0,
                'lexical': 0.0,
                'ngram': 0.0,
                'verbatim': 0.0,
                'combined': 0.0,
                'top_matches': []
            }
        
        # Lexical similarity with filtered top matches
        lexical_scores = []
        ngram_scores = []
        
        for score, match_text in top_matches:
            lexical_scores.append(self.lexical_similarity(text, match_text))
            ngram_scores.append(self.ngram_overlap(text, match_text, n=3))
        
        max_lexical = max(lexical_scores) if lexical_scores else 0.0
        max_ngram = max(ngram_scores) if ngram_scores else 0.0
        
        # Semantic similarity (average of filtered matches)
        semantic_scores = [score for score, _ in top_matches]
        semantic_sim = np.mean(semantic_scores) if semantic_scores else 0.0
        
        # Verbatim copying detection
        verbatim_score = self.detect_verbatim_copying(text, store)
        
        # Combined plagiarism score
        combined_score = (
            0.40 * semantic_sim +
            0.30 * max_lexical +
            0.20 * max_ngram +
            0.10 * verbatim_score
        )
        
        return {
            'semantic': semantic_sim,
            'lexical': max_lexical,
            'ngram': max_ngram,
            'verbatim': verbatim_score,
            'combined': combined_score,
            'top_matches': [(score, match_text[:100]) for score, match_text in top_matches]
        }
    
    def score(self, paragraph, embedding, store):
        """Calculate final plagiarism score with citation adjustment."""
        details = self.calculate_plagiarism_details(paragraph, embedding, store)
        base_score = details['combined']
        
        # Citation adjustment
        num_citations = len(paragraph.get("citations", []))
        if num_citations > 0:
            # Reduce plagiarism score if properly cited
            citation_discount = min(num_citations * 0.1, 0.6)
            adjusted_score = base_score * (1 - citation_discount)
        else:
            adjusted_score = base_score
        
        return min(adjusted_score, 1.0)
