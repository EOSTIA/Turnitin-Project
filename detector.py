"""
Comprehensive Detection Module
Combines plagiarism and AI detection into a unified interface.
"""

from embedding import Embedder
from vector_store import VectorStore
from plagiarism import PlagiarismEngine
from ai_detection import AIDetector
from human_score import HumanContribution
from originality import OriginalityScorer
from refinement import refinement_suggestions
import numpy as np


class IntegrityDetector:
    """
    Unified academic integrity detector.
    Combines plagiarism, AI detection, and human contribution analysis.
    """
    
    def __init__(self):
        """Initialize all detection components."""
        self.embedder = Embedder()
        self.plagiarism_engine = PlagiarismEngine()
        self.ai_detector = AIDetector()
        self.human_scorer = HumanContribution()
        self.originality_scorer = OriginalityScorer()
        self.vector_store = None
    
    def build_corpus(self, corpus_texts):
        """
        Build vector store from corpus texts.
        
        Args:
            corpus_texts: List of text strings to use as reference corpus
        """
        if not corpus_texts:
            # Create empty store
            default_embedding = self.embedder.encode(["test"])[0]
            self.vector_store = VectorStore(dim=len(default_embedding))
            return
        
        # Encode corpus
        embeddings = self.embedder.encode(corpus_texts)
        
        # Create vector store
        self.vector_store = VectorStore(dim=len(embeddings[0]))
        self.vector_store.add(embeddings, corpus_texts)
    
    def analyze_text(self, text, citations=None):
        """
        Analyze a single text for integrity issues.
        
        Args:
            text: Text string to analyze
            citations: Optional list of citations
        
        Returns:
            Dictionary with all scores and analysis
        """
        if not text or len(text.strip()) < 20:
            return {
                "error": "Text too short for analysis",
                "min_length": 20
            }
        
        # Prepare paragraph structure
        paragraph = {
            "text": text,
            "citations": citations or []
        }
        
        # Encode text
        embedding = self.embedder.encode([text])[0]
        
        # Calculate plagiarism score
        plagiarism_score = 0.0
        if self.vector_store and self.vector_store.get_size() > 0:
            plagiarism_score = self.plagiarism_engine.score(
                paragraph, 
                embedding, 
                self.vector_store
            )
        
        # Calculate AI detection score
        ai_score = self.ai_detector.score(text)
        
        # Calculate human contribution score
        human_score = self.human_scorer.score(
            plagiarism_score, 
            ai_score, 
            citations or []
        )
        
        # Calculate originality score
        originality_score = self.originality_scorer.score(
            plagiarism_score, 
            ai_score
        )
        
        # Get refinement suggestions
        suggestions = refinement_suggestions(
            plagiarism_score,
            ai_score,
            human_contribution=human_score,
            citations=len(citations) if citations else 0
        )
        
        # Get qualitative assessments
        human_level = self.human_scorer.get_contribution_level(human_score)
        originality_level = self.originality_scorer.get_originality_level(originality_score)
        
        return {
            "scores": {
                "plagiarism": round(plagiarism_score, 3),
                "ai_detection": round(ai_score, 3),
                "human_contribution": round(human_score, 3),
                "originality": round(originality_score, 3)
            },
            "assessments": {
                "human_contribution": human_level,
                "originality": originality_level
            },
            "flags": {
                "high_plagiarism": plagiarism_score > 0.4,
                "high_ai": ai_score > 0.6,
                "low_human": human_score < 0.5,
                "low_originality": originality_score < 0.5
            },
            "refinement_suggestions": suggestions,
            "status": "PASS" if (plagiarism_score < 0.3 and ai_score < 0.5) else "NEEDS_REVIEW"
        }
    
    def batch_analyze(self, texts, citations_list=None):
        """
        Analyze multiple texts in batch.
        
        Args:
            texts: List of text strings
            citations_list: Optional list of citation lists (one per text)
        
        Returns:
            List of analysis results
        """
        results = []
        
        for idx, text in enumerate(texts):
            citations = citations_list[idx] if citations_list and idx < len(citations_list) else None
            result = self.analyze_text(text, citations)
            result["index"] = idx
            results.append(result)
        
        return results
    
    def compare_texts(self, text1, text2):
        """
        Compare two texts for similarity.
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Dictionary with similarity metrics
        """
        # Encode both texts
        embeddings = self.embedder.encode([text1, text2])
        
        # Cosine similarity (using normalized embeddings)
        semantic_similarity = float(np.dot(embeddings[0], embeddings[1]))
        
        # Lexical similarity
        lexical_similarity = self.plagiarism_engine.lexical_similarity(text1, text2)
        
        # N-gram overlap
        ngram_similarity = self.plagiarism_engine.ngram_overlap(text1, text2, n=3)
        
        return {
            "semantic_similarity": round(semantic_similarity, 3),
            "lexical_similarity": round(lexical_similarity, 3),
            "ngram_similarity": round(ngram_similarity, 3),
            "overall_similarity": round(
                0.5 * semantic_similarity + 
                0.3 * lexical_similarity + 
                0.2 * ngram_similarity, 
                3
            ),
            "assessment": "High similarity" if semantic_similarity > 0.8 else 
                         "Moderate similarity" if semantic_similarity > 0.6 else
                         "Low similarity"
        }


class StreamingDetector(IntegrityDetector):
    """
    Streaming version of integrity detector for real-time analysis.
    Useful for analyzing content as it's being written.
    """
    
    def __init__(self, update_callback=None):
        """
        Initialize streaming detector.
        
        Args:
            update_callback: Optional callback function called with each analysis result
        """
        super().__init__()
        self.update_callback = update_callback
        self.analysis_history = []
    
    def stream_analyze(self, text_chunks, citations_list=None):
        """
        Analyze text chunks as they arrive.
        
        Args:
            text_chunks: Iterable of text chunks
            citations_list: Optional list of citations per chunk
        
        Returns:
            List of all analysis results
        """
        results = []
        
        for idx, chunk in enumerate(text_chunks):
            citations = citations_list[idx] if citations_list and idx < len(citations_list) else None
            
            # Analyze chunk
            result = self.analyze_text(chunk, citations)
            result["chunk_index"] = idx
            
            # Store in history
            self.analysis_history.append(result)
            results.append(result)
            
            # Call update callback if provided
            if self.update_callback:
                self.update_callback(result)
        
        return results
    
    def get_trends(self):
        """
        Get trends from analysis history.
        
        Returns:
            Dictionary with trend information
        """
        if not self.analysis_history:
            return {"error": "No analysis history"}
        
        plagiarism_scores = [r["scores"]["plagiarism"] for r in self.analysis_history]
        ai_scores = [r["scores"]["ai_detection"] for r in self.analysis_history]
        human_scores = [r["scores"]["human_contribution"] for r in self.analysis_history]
        
        return {
            "plagiarism_trend": "increasing" if plagiarism_scores[-1] > plagiarism_scores[0] else "decreasing",
            "ai_trend": "increasing" if ai_scores[-1] > ai_scores[0] else "decreasing",
            "human_trend": "increasing" if human_scores[-1] > human_scores[0] else "decreasing",
            "average_scores": {
                "plagiarism": round(np.mean(plagiarism_scores), 3),
                "ai": round(np.mean(ai_scores), 3),
                "human": round(np.mean(human_scores), 3)
            }
        }
