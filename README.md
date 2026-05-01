# Academic Integrity Validation Engine

A comprehensive Plagiarism & AI-Usage Validation Engine that validates "human-in-the-loop" contribution, identifies potential AI-generated text patterns, and provides section-wise originality scores with actionable refinement suggestions.

## Features

### 🔍 **Multi-Layered Plagiarism Detection**
- **Semantic Similarity**: Uses state-of-the-art sentence transformers to detect meaning-level similarities
- **Lexical Analysis**: Identifies exact text matches and paraphrasing
- **N-gram Overlap**: Detects phrase-level copying
- **Verbatim Detection**: Catches long-sequence direct copying
- **Citation-Aware**: Reduces plagiarism scores for properly cited content

### 🤖 **Advanced AI Detection**
- **Perplexity Analysis**: Measures text predictability (AI-generated text has lower perplexity)
- **Classifier-Based**: Uses fine-tuned transformer models for AI detection
- **Stylometry**: Analyzes writing style uniformity and patterns
- **Burstiness**: Detects variation in sentence structure
- **Pattern Recognition**: Identifies common AI writing patterns and phrases

### 👤 **Human Contribution Scoring**
- Validates authentic "human-in-the-loop" contribution
- Considers novelty, originality, and ethical writing
- Accounts for citation depth and research quality
- Provides qualitative assessments

### 📊 **Comprehensive Reporting**
- Section-wise originality scores
- Detailed statistics with mean, median, and standard deviation
- Flagged sections with severity levels (Critical, High, Medium, Low)
- Both JSON and HTML report formats
- Executive summary with integrity grades (A-F)

### 💡 **Actionable Refinement Suggestions**
- Specific, categorized suggestions for improvement
- Prioritized by severity level
- Addresses plagiarism, AI usage, citations, and human contribution
- Overall assessment for each section

## Installation

```bash
# Clone the repository

# Install dependencies
pip install -r requirements.txt

# Install and run GROBID (required for PDF parsing)
# Download from: https://github.com/kermitt2/grobid
# Run: ./gradlew run
```

## Prerequisites

### GROBID Setup
GROBID is required for parsing academic PDFs. 

1. Download GROBID:
   ```bash
   git clone https://github.com/kermitt2/grobid.git
   cd grobid
   ```

2. Build and run:
   ```bash
   ./gradlew run
   ```

3. Verify it's running at `http://localhost:8070`

## Usage

### Command Line

#### Analyze a Single Paper
```bash
python main.py paper.pdf corpus_directory/ output_directory/
```

#### Analyze Multiple Papers
```bash
python main.py --dir papers_directory/ corpus_directory/ output_directory/
```

### Python API

#### Basic Usage
```python
from main import process_paper

# Analyze a paper
report = process_paper(
    pdf_path="research_paper.pdf",
    corpus_dir="reference_papers/",
    output_dir="analysis_results/"
)

# Access results
print(f"Originality: {report['executive_summary']['overall_originality_score']:.1%}")
print(f"Grade: {report['executive_summary']['integrity_grade']}")
```

#### Advanced Usage with Detector API
```python
from detector import IntegrityDetector

# Initialize detector
detector = IntegrityDetector()

# Build reference corpus
corpus_texts = [
    "This is a reference document...",
    "Another reference text...",
]
detector.build_corpus(corpus_texts)

# Analyze text
result = detector.analyze_text(
    text="Your text to analyze...",
    citations=["Citation 1", "Citation 2"]
)

print(f"Plagiarism: {result['scores']['plagiarism']:.1%}")
print(f"AI Detection: {result['scores']['ai_detection']:.1%}")
print(f"Status: {result['status']}")

# Get suggestions
for suggestion in result['refinement_suggestions']['suggestions']:
    print(f"- [{suggestion['severity']}] {suggestion['issue']}")
```

#### Batch Analysis
```python
from detector import IntegrityDetector

detector = IntegrityDetector()
detector.build_corpus(corpus_texts)

# Analyze multiple texts
texts = [
    "First paragraph...",
    "Second paragraph...",
    "Third paragraph..."
]

results = detector.batch_analyze(texts)

for idx, result in enumerate(results):
    print(f"Paragraph {idx + 1}: {result['status']}")
```

#### Text Comparison
```python
from detector import IntegrityDetector

detector = IntegrityDetector()

# Compare two texts
similarity = detector.compare_texts(
    text1="Original text...",
    text2="Potentially similar text..."
)

print(f"Similarity: {similarity['overall_similarity']:.1%}")
print(f"Assessment: {similarity['assessment']}")
```

## Output Reports

### JSON Report Structure
```json
{
  "metadata": {
    "generated_at": "2026-02-07T...",
    "total_paragraphs": 25,
    "total_sections": 5
  },
  "executive_summary": {
    "integrity_grade": "A - Excellent originality and integrity",
    "overall_originality_score": 0.856,
    "overall_plagiarism_score": 0.123,
    "overall_ai_detection_score": 0.234,
    "overall_human_contribution_score": 0.789,
    "status": "PASS"
  },
  "detailed_statistics": {
    "plagiarism": {
      "mean": 0.123,
      "median": 0.115,
      "std_dev": 0.045,
      "distribution": {
        "high": 0,
        "medium": 2,
        "low": 23
      }
    }
  },
  "flagged_sections": [
    {
      "section": "Introduction",
      "severity": "MEDIUM",
      "reason": ["Moderate plagiarism (32%)"]
    }
  ],
  "recommendations": [
    "Content demonstrates strong originality",
    "Continue maintaining high academic integrity standards"
  ]
}
```

### HTML Report
An interactive HTML report is generated with:
- Color-coded integrity grades
- Statistical charts
- Detailed section analysis
- Expandable recommendations

## Scoring System

### Originality Score (0-1, higher is better)
- **0.85-1.0**: Exceptional - Highly original work
- **0.70-0.84**: Excellent - Strong originality
- **0.55-0.69**: Good - Adequate originality
- **0.40-0.54**: Fair - Some concerns
- **0.25-0.39**: Poor - Significant issues
- **0.0-0.24**: Very Poor - Severe concerns

### Plagiarism Score (0-1, lower is better)
- **0.0-0.25**: Low - Acceptable
- **0.25-0.40**: Medium - Review recommended
- **0.40-0.70**: High - Revisions required
- **0.70-1.0**: Critical - Major revisions required

### AI Detection Score (0-1, lower is better)
- **0.0-0.35**: Low - Likely human-written
- **0.35-0.60**: Medium - Some AI indicators
- **0.60-0.70**: High - Likely AI-assisted
- **0.70-1.0**: Critical - Very likely AI-generated

### Human Contribution Score (0-1, higher is better)
- **0.80-1.0**: Excellent - High human contribution
- **0.65-0.79**: Good - Substantial contribution
- **0.50-0.64**: Moderate - Adequate contribution
- **0.35-0.49**: Low - Limited contribution
- **0.0-0.34**: Very Low - Minimal contribution

## Configuration

Edit `config.py` to customize:

```python
# Embedding model
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

# Detection thresholds
HIGH_PLAGIARISM_THRESHOLD = 0.40
AI_HIGH_THRESHOLD = 0.60

# Scoring weights
HUMAN_REWRITE_WEIGHT = 0.40
HUMAN_NOVELTY_WEIGHT = 0.30
HUMAN_ETHICAL_WEIGHT = 0.30

# Feature toggles
USE_PERPLEXITY = True
USE_BURSTINESS = True
USE_STYLOMETRY = True
USE_CLASSIFIER = True
```

## Architecture

```
turnitin_engine/
├── main.py                 # Main processing pipeline
├── detector.py             # Unified detector API
├── config.py               # Configuration settings
├── ingest.py               # PDF parsing with GROBID
├── embedding.py            # Text embedding
├── vector_store.py         # Vector similarity search
├── plagiarism.py           # Plagiarism detection
├── ai_detection.py         # AI-generated text detection
├── human_score.py          # Human contribution scoring
├── originality.py          # Originality scoring
├── refinement.py           # Refinement suggestions
└── report.py               # Report generation
```

## How It Works

1. **PDF Parsing**: GROBID extracts structured text from PDFs, preserving sections and citations
2. **Embedding**: Text is converted to semantic vectors using sentence transformers
3. **Plagiarism Detection**: Multi-layered approach combining semantic, lexical, and n-gram analysis
4. **AI Detection**: Multiple techniques (perplexity, classifier, stylometry, burstiness)
5. **Score Calculation**: Comprehensive scoring for plagiarism, AI usage, human contribution, and originality
6. **Report Generation**: Detailed reports with statistics, flagged sections, and actionable suggestions

## Best Practices

1. **Build a Quality Corpus**: Include relevant papers in your reference corpus for accurate plagiarism detection
2. **Regular Updates**: Update AI detection models as new models emerge
3. **Threshold Tuning**: Adjust thresholds based on your specific use case
4. **Citation Awareness**: Ensure citations are properly parsed for accurate scoring
5. **Iterative Analysis**: Use refinement suggestions to improve content iteratively

## Performance Tips

- **GPU Acceleration**: Use CUDA-enabled PyTorch for faster AI detection
- **Batch Processing**: Process multiple papers together for efficiency
- **Corpus Optimization**: Keep corpus focused and relevant
- **Caching**: Results are cached where appropriate to avoid redundant computation

## Limitations

- Requires GROBID server for PDF parsing
- AI detection accuracy depends on training data
- Works best with English academic text
- Requires sufficient reference corpus for plagiarism detection

## Citation

If you use this tool in academic work, please cite appropriately.

## License

See LICENSE file for details.

## Support

For issues and questions:
- Check the documentation
- Review configuration settings
- Ensure GROBID is running
- Verify all dependencies are installed

## Acknowledgments

Built using:
- Sentence Transformers for embeddings
- Transformers for AI detection
- FAISS for vector search
- GROBID for PDF parsing
