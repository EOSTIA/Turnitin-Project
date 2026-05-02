"""
Example Usage of the Academic Integrity Validation Engine
Demonstrates various ways to use the plagiarism and AI detection system.
"""

from detector import IntegrityDetector, StreamingDetector
from main import process_paper
import json


def example_1_simple_text_analysis():
    """Example 1: Analyze a simple text without corpus."""
    print("\n" + "="*80)
    print("Example 1: Simple Text Analysis")
    print("="*80 + "\n")
    
    # Initialize detector
    detector = IntegrityDetector()
    
    # Build empty corpus (optional - for demo purposes)
    detector.build_corpus([])
    
    # Text to analyze
    text = """
    Machine learning has revolutionized the field of artificial intelligence.
    Deep neural networks, particularly convolutional neural networks, have 
    achieved remarkable results in computer vision tasks. These networks can
    automatically learn hierarchical features from raw data, eliminating the
    need for manual feature engineering.
    """
    
    # Analyze
    result = detector.analyze_text(text, citations=["LeCun et al., 2015"])
    
    # Print results
    print("Scores:")
    for metric, score in result['scores'].items():
        print(f"  {metric}: {score:.1%}")
    
    print(f"\nStatus: {result['status']}")
    print(f"\nAssessments:")
    for key, value in result['assessments'].items():
        print(f"  {key}: {value}")
    
    print(f"\nOverall Assessment:")
    print(f"  {result['refinement_suggestions']['overall_assessment']}")
    

def example_2_with_corpus():
    """Example 2: Analyze text with reference corpus."""
    print("\n" + "="*80)
    print("Example 2: Analysis with Reference Corpus")
    print("="*80 + "\n")
    
    # Initialize detector
    detector = IntegrityDetector()
    
    # Build reference corpus
    corpus = [
        "Machine learning algorithms can learn patterns from data without explicit programming.",
        "Deep learning uses multiple layers to progressively extract higher-level features.",
        "Neural networks are inspired by biological neural networks in the brain.",
        "Supervised learning requires labeled training data to learn from examples.",
        "Unsupervised learning finds hidden patterns in unlabeled data."
    ]
    
    detector.build_corpus(corpus)
    
    # Text that partially copies from corpus
    text = """
    Machine learning algorithms can learn patterns from data without explicit 
    programming. This capability has led to breakthrough applications in various
    domains. The technology continues to evolve with new architectures and 
    training methods.
    """
    
    # Analyze
    result = detector.analyze_text(text, citations=[])
    
    # Print results
    print("Scores:")
    for metric, score in result['scores'].items():
        print(f"  {metric}: {score:.1%}")
    
    print(f"\nFlags:")
    for flag, value in result['flags'].items():
        if value:
            print(f"  ⚠️  {flag}: {value}")
    
    print(f"\nRefinement Suggestions:")
    priority = result['refinement_suggestions']['priority']
    print(f"  Priority Level: {priority}")
    
    for suggestion in result['refinement_suggestions']['suggestions']:
        print(f"\n  Category: {suggestion['category']}")
        print(f"  Severity: {suggestion['severity']}")
        print(f"  Issue: {suggestion['issue']}")
        print(f"  Actions:")
        for action in suggestion['actions'][:2]:  # Show first 2 actions
            print(f"    - {action}")


def example_3_batch_analysis():
    """Example 3: Batch analysis of multiple texts."""
    print("\n" + "="*80)
    print("Example 3: Batch Analysis")
    print("="*80 + "\n")
    
    # Initialize detector
    detector = IntegrityDetector()
    detector.build_corpus([])
    
    # Multiple texts to analyze
    texts = [
        "The quick brown fox jumps over the lazy dog. This is a test sentence.",
        "Artificial intelligence has transformed modern technology in unprecedented ways.",
        "Climate change poses significant challenges to global ecosystems and human societies."
    ]
    
    # Batch analyze
    results = detector.batch_analyze(texts)
    
    # Print results
    for idx, result in enumerate(results, 1):
        print(f"\nText {idx}:")
        print(f"  Originality: {result['scores']['originality']:.1%}")
        print(f"  AI Detection: {result['scores']['ai_detection']:.1%}")
        print(f"  Status: {result['status']}")


def example_4_text_comparison():
    """Example 4: Compare two texts for similarity."""
    print("\n" + "="*80)
    print("Example 4: Text Comparison")
    print("="*80 + "\n")
    
    # Initialize detector
    detector = IntegrityDetector()
    
    # Original text
    text1 = """
    Neural networks are computational models inspired by the human brain.
    They consist of interconnected nodes organized in layers that process
    information through weighted connections.
    """
    
    # Similar text (paraphrased)
    text2 = """
    Artificial neural networks are computing systems modeled after biological brains.
    These systems comprise connected processing units arranged in hierarchical layers
    that transform data via adjustable link strengths.
    """
    
    # Different text
    text3 = """
    The weather today is sunny with a high of 75 degrees.
    It's a perfect day for outdoor activities.
    """
    
    # Compare texts
    similarity1 = detector.compare_texts(text1, text2)
    similarity2 = detector.compare_texts(text1, text3)
    
    print("Similarity between original and paraphrased:")
    for metric, value in similarity1.items():
        print(f"  {metric}: {value}")
    
    print("\nSimilarity between original and unrelated:")
    for metric, value in similarity2.items():
        print(f"  {metric}: {value}")


def example_5_streaming_analysis():
    """Example 5: Streaming analysis with callbacks."""
    print("\n" + "="*80)
    print("Example 5: Streaming Analysis")
    print("="*80 + "\n")
    
    # Define callback function
    def on_update(result):
        chunk_idx = result.get('chunk_index', 0)
        ai_score = result['scores']['ai_detection']
        status = result['status']
        print(f"  Chunk {chunk_idx + 1}: AI={ai_score:.1%}, Status={status}")
    
    # Initialize streaming detector
    detector = StreamingDetector(update_callback=on_update)
    detector.build_corpus([])
    
    # Text chunks (simulating streaming input)
    chunks = [
        "This is the first paragraph of the document.",
        "The second paragraph discusses a different topic.",
        "Finally, the third paragraph provides conclusions."
    ]
    
    # Stream analyze
    print("Analyzing chunks:")
    results = detector.stream_analyze(chunks)
    
    # Get trends
    print("\nTrends:")
    trends = detector.get_trends()
    for key, value in trends.items():
        print(f"  {key}: {value}")


def example_6_full_pdf_analysis():
    """Example 6: Full PDF analysis (requires GROBID and actual PDF file)."""
    print("\n" + "="*80)
    print("Example 6: Full PDF Analysis")
    print("="*80 + "\n")
    
    # Note: This requires:
    # 1. GROBID server running at http://localhost:8070
    # 2. Actual PDF files
    
    pdf_path = "example_paper.pdf"  # Replace with actual PDF
    corpus_dir = "reference_papers"  # Replace with actual corpus directory
    output_dir = "analysis_output"
    
    print(f"To run full PDF analysis:")
    print(f"  1. Ensure GROBID is running at http://localhost:8070")
    print(f"  2. Place PDF at: {pdf_path}")
    print(f"  3. Place reference PDFs in: {corpus_dir}/")
    print(f"  4. Run: python main.py {pdf_path} {corpus_dir} {output_dir}")
    
    # Uncomment to run (if you have the setup):
    # report = process_paper(pdf_path, corpus_dir, output_dir)
    # print(f"\nReport saved to: {output_dir}/")


def example_7_custom_refinement():
    """Example 7: Get detailed refinement suggestions."""
    print("\n" + "="*80)
    print("Example 7: Detailed Refinement Suggestions")
    print("="*80 + "\n")
    
    # Initialize detector
    detector = IntegrityDetector()
    detector.build_corpus([])
    
    # Text with potential issues
    text = """
    Furthermore, it is important to note that machine learning algorithms can be 
    utilized to process data. Moreover, these algorithms may potentially provide 
    accurate results. Nevertheless, it is crucial to understand that proper 
    validation is necessary.
    """
    
    # Analyze
    result = detector.analyze_text(text, citations=[])
    
    # Print detailed suggestions
    suggestions = result['refinement_suggestions']
    
    print(f"Priority Level: {suggestions['priority']}")
    print(f"\nOverall Assessment:\n  {suggestions['overall_assessment']}")
    
    print(f"\nDetailed Suggestions:")
    for suggestion in suggestions['suggestions']:
        print(f"\n  [{suggestion['severity']}] {suggestion['category']}")
        print(f"  Issue: {suggestion['issue']}")
        print(f"  Recommended Actions:")
        for action in suggestion['actions']:
            print(f"    • {action}")


def run_all_examples():
    """Run all examples."""
    examples = [
        example_1_simple_text_analysis,
        example_2_with_corpus,
        example_3_batch_analysis,
        example_4_text_comparison,
        example_5_streaming_analysis,
        example_6_full_pdf_analysis,
        example_7_custom_refinement
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("All Examples Completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    # Run all examples
    run_all_examples()
    
    # Or run individual examples:
    # example_1_simple_text_analysis()
    # example_2_with_corpus()
    # example_4_text_comparison()
