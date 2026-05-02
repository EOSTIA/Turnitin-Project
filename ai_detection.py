import torch
import numpy as np
import re
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    GPT2Tokenizer,
    GPT2LMHeadModel
)
from config import (
    USE_PERPLEXITY,
    USE_BURSTINESS,
    USE_STYLOMETRY,
    USE_CLASSIFIER,
    PERPLEXITY_AI_THRESHOLD,
    PERPLEXITY_HUMAN_THRESHOLD,
    STYLOMETRY_VARIANCE_THRESHOLD
)

class AIDetector:
    def __init__(self):
        # Initialize classifier for AI detection
        try:
            # Try to load specialized AI detection model
            self.cls_tokenizer = AutoTokenizer.from_pretrained("Hello-SimpleAI/chatgpt-detector-roberta")
            self.cls_model = AutoModelForSequenceClassification.from_pretrained(
                "Hello-SimpleAI/chatgpt-detector-roberta"
            )
        except Exception as e:
            print(f"Warning: Could not load specialized AI detector, falling back to roberta-base: {e}")
            self.cls_tokenizer = AutoTokenizer.from_pretrained("roberta-base")
            self.cls_model = AutoModelForSequenceClassification.from_pretrained(
                "roberta-base", num_labels=2
            )
        
        # Initialize language model for perplexity
        if USE_PERPLEXITY:
            self.lm_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
            self.lm_model = GPT2LMHeadModel.from_pretrained("gpt2")
            self.lm_tokenizer.pad_token = self.lm_tokenizer.eos_token
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.cls_model.to(self.device)
        if USE_PERPLEXITY:
            self.lm_model.to(self.device)
    
    def perplexity(self, text):
        """Calculate perplexity - AI text typically has lower perplexity."""
        if not USE_PERPLEXITY or not text.strip():
            return 50.0
        
        try:
            # Split into chunks if text is too long
            max_length = 512
            inputs = self.lm_tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                max_length=max_length,
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.lm_model(**inputs, labels=inputs["input_ids"])
                loss = outputs.loss
            
            perplexity = torch.exp(loss).item()
            return min(perplexity, 500.0)  # Cap at 500
        except Exception as e:
            print(f"Perplexity calculation error: {e}")
            return 50.0
    
    def burstiness(self, text):
        """Calculate burstiness - AI text tends to be less bursty."""
        if not USE_BURSTINESS:
            return 0.5
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sentences) < 3:
            return 0.5
        
        sentence_lengths = [len(s.split()) for s in sentences]
        
        # Calculate burstiness as variation in sentence length
        mean_len = np.mean(sentence_lengths)
        std_len = np.std(sentence_lengths)
        
        if mean_len == 0:
            return 0.5
        
        # Coefficient of variation
        cv = std_len / mean_len
        
        # AI text typically has CV < 0.4, human text CV > 0.6
        # Convert to AI probability (lower burstiness = higher AI probability)
        burstiness_score = 1 - min(cv / 1.0, 1.0)
        
        return burstiness_score
    
    def classifier_prob(self, text):
        """Use transformer classifier to detect AI-generated text."""
        if not USE_CLASSIFIER or not text.strip():
            return 0.5
        
        try:
            inputs = self.cls_tokenizer(
                text, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512,
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                logits = self.cls_model(**inputs).logits
                probs = torch.softmax(logits, dim=1)
            
            # Assuming index 1 is AI-generated
            if probs.shape[1] == 2:
                return probs[0][1].item()
            else:
                return probs[0][0].item()
        except Exception as e:
            print(f"Classifier error: {e}")
            return 0.5
    
    def stylometry(self, text):
        """Analyze writing style - AI text tends to be more uniform."""
        if not USE_STYLOMETRY:
            return 0.5
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sentences) < 2:
            return 0.5
        
        # Sentence length variance
        lengths = [len(s.split()) for s in sentences]
        variance = np.var(lengths)
        
        # Low variance suggests AI (uniform writing style)
        uniformity_score = 1 - min(variance / STYLOMETRY_VARIANCE_THRESHOLD, 1.0)
        
        # Word diversity
        words = text.lower().split()
        if len(words) == 0:
            word_diversity = 0.5
        else:
            unique_ratio = len(set(words)) / len(words)
            # AI often has lower diversity (more repetitive)
            word_diversity = 1 - unique_ratio
        
        # Punctuation patterns
        punct_count = len(re.findall(r'[,;:—]', text))
        word_count = len(words)
        punct_ratio = punct_count / word_count if word_count > 0 else 0
        # Normalize punctuation ratio (AI often has specific punctuation patterns)
        punct_score = min(punct_ratio / 0.1, 1.0)
        
        # Combined stylometry score
        style_score = (
            0.50 * uniformity_score +
            0.30 * word_diversity +
            0.20 * punct_score
        )
        
        return min(style_score, 1.0)
    
    def detect_ai_patterns(self, text):
        """Detect common AI writing patterns."""
        ai_indicators = 0
        total_indicators = 0
        
        # Check for overly formal transitions
        formal_transitions = [
            'furthermore', 'moreover', 'nevertheless', 'consequently',
            'in conclusion', 'to summarize', 'it is important to note'
        ]
        total_indicators += len(formal_transitions)
        for phrase in formal_transitions:
            if phrase in text.lower():
                ai_indicators += 1
        
        # Check for balanced sentence structure
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sentences) >= 3:
            lengths = [len(s.split()) for s in sentences]
            avg_length = np.mean(lengths)
            # AI often produces sentences of similar length
            similar_length = sum(1 for l in lengths if abs(l - avg_length) < 3)
            if similar_length / len(sentences) > 0.7:
                ai_indicators += 2
        total_indicators += 2
        
        # Check for hedging language (AI often hedges)
        hedges = ['may', 'might', 'could', 'possibly', 'perhaps', 'potentially']
        hedge_count = sum(1 for hedge in hedges if hedge in text.lower().split())
        if hedge_count >= 3:
            ai_indicators += 1
        total_indicators += 1
        
        return ai_indicators / total_indicators if total_indicators > 0 else 0.0
    
    def score(self, text):
        """Calculate comprehensive AI detection score."""
        if not text or len(text.strip()) < 50:
            return 0.0
        
        scores = {}
        weights = {}
        
        # Perplexity score
        if USE_PERPLEXITY:
            ppl = self.perplexity(text)
            # Convert perplexity to AI probability
            # Lower perplexity = more likely AI
            ppl_score = 1.0 - min(
                max((ppl - PERPLEXITY_AI_THRESHOLD) / (PERPLEXITY_HUMAN_THRESHOLD - PERPLEXITY_AI_THRESHOLD), 0.0),
                1.0
            )
            scores['perplexity'] = ppl_score
            weights['perplexity'] = 0.25
        
        # Classifier score
        if USE_CLASSIFIER:
            scores['classifier'] = self.classifier_prob(text)
            weights['classifier'] = 0.30
        
        # Stylometry score
        if USE_STYLOMETRY:
            scores['stylometry'] = self.stylometry(text)
            weights['stylometry'] = 0.20
        
        # Burstiness score
        if USE_BURSTINESS:
            scores['burstiness'] = self.burstiness(text)
            weights['burstiness'] = 0.15
        
        # Pattern detection
        scores['patterns'] = self.detect_ai_patterns(text)
        weights['patterns'] = 0.10
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight == 0:
            return 0.5
        
        normalized_weights = {k: v/total_weight for k, v in weights.items()}
        
        # Calculate weighted average
        final_score = sum(scores[k] * normalized_weights[k] for k in scores.keys())
        
        return min(max(final_score, 0.0), 1.0)
