# Embedding Models
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
AI_CLASSIFIER_MODEL = "roberta-base-openai-detector"
AI_DETECTION_MODEL = "Hello-SimpleAI/chatgpt-detector-roberta"

# Thresholds for Plagiarism Detection
SEMANTIC_THRESHOLD = 0.80
LEXICAL_THRESHOLD = 0.85
HIGH_PLAGIARISM_THRESHOLD = 0.40
MEDIUM_PLAGIARISM_THRESHOLD = 0.25

# Thresholds for AI Detection
AI_HIGH_THRESHOLD = 0.60
AI_MEDIUM_THRESHOLD = 0.35
AI_LOW_THRESHOLD = 0.20

# Human Contribution Weights
HUMAN_REWRITE_WEIGHT = 0.40
HUMAN_NOVELTY_WEIGHT = 0.30
HUMAN_ETHICAL_WEIGHT = 0.30

# Originality Scoring
AI_PENALTY_FACTOR = 0.70

# Vector Store Settings
VECTOR_SEARCH_K = 5

# Report Settings
MIN_PARAGRAPH_LENGTH = 50
CITATION_BONUS_FACTOR = 0.4

# AI Detection Features
USE_PERPLEXITY = True
USE_BURSTINESS = True
USE_STYLOMETRY = True
USE_CLASSIFIER = True

# Perplexity Settings
PERPLEXITY_AI_THRESHOLD = 30.0  # Lower perplexity suggests AI
PERPLEXITY_HUMAN_THRESHOLD = 100.0

# Stylometry Settings
STYLOMETRY_VARIANCE_THRESHOLD = 50.0
