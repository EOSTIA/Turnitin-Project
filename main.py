from ingest import parse_pdf
from embedding import Embedder
from vector_store import VectorStore
from plagiarism import PlagiarismEngine
from ai_detection import AIDetector
from human_score import HumanContribution
from originality import OriginalityScorer
from refinement import refinement_suggestions
from report import generate_report, save_report, generate_html_report
import json
import os
from datetime import datetime
import sys

def process_paper(pdf_path, corpus_dir=None, output_dir="output"):
    """
    Process a research paper for plagiarism and AI detection.
    
    Args:
        pdf_path: Path to the PDF to analyze
        corpus_dir: Directory containing reference corpus PDFs (optional)
        output_dir: Directory to save output reports
    
    Returns:
        Comprehensive validation report
    """
    print(f"\n{'='*80}")
    print(f"Academic Integrity Validation Engine")
    print(f"{'='*80}\n")
    
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"[1/7] Loading paper: {pdf_path}")
        # Load paper draft
        paper = parse_pdf(pdf_path)
        print(f"      ✓ Loaded {len(paper)} paragraphs\n")
        
        # Load reference corpus
        corpus = []
        if corpus_dir and os.path.exists(corpus_dir):
            print(f"[2/7] Loading reference corpus from: {corpus_dir}")
            corpus_files = [os.path.join(corpus_dir, f) for f in os.listdir(corpus_dir) if f.endswith('.pdf')]
            
            for idx, doc_path in enumerate(corpus_files, 1):
                try:
                    print(f"      Loading corpus document {idx}/{len(corpus_files)}: {os.path.basename(doc_path)}")
                    corpus.extend(parse_pdf(doc_path))
                except Exception as e:
                    print(f"      ⚠ Warning: Failed to load {os.path.basename(doc_path)}: {e}")
            
            print(f"      ✓ Loaded {len(corpus)} paragraphs from corpus\n")
        else:
            print(f"[2/7] No corpus directory provided or found, using empty corpus\n")
        
        corpus_texts = [c["text"] for c in corpus] if corpus else []
        
        # Initialize components
        print(f"[3/7] Initializing AI models and embedders")
        embedder = Embedder()
        plag_engine = PlagiarismEngine()
        ai_detector = AIDetector()
        human = HumanContribution()
        orig = OriginalityScorer()
        print(f"      ✓ Models initialized\n")
        
        # Build vector store
        print(f"[4/7] Building vector store")
        if corpus_texts:
            corpus_embeddings = embedder.encode(corpus_texts)
            store = VectorStore(dim=len(corpus_embeddings[0]))
            store.add(corpus_embeddings, corpus_texts)
            print(f"      ✓ Vector store built with {len(corpus_texts)} documents\n")
        else:
            # Create empty store with default dimension
            print(f"      ⚠ Creating empty vector store (no corpus)\n")
            default_embedding = embedder.encode(["test"])[0]
            store = VectorStore(dim=len(default_embedding))
        
        # Analyze each paragraph
        print(f"[5/7] Analyzing paragraphs")
        results = []
        
        for idx, para in enumerate(paper, 1):
            print(f"      Analyzing paragraph {idx}/{len(paper)}: {para['section']}", end="\r")
            
            # Encode paragraph
            emb = embedder.encode([para["text"]])[0]
            
            # Calculate scores
            plagiarism = plag_engine.score(para, emb, store) if corpus_texts else 0.0
            ai_score = ai_detector.score(para["text"])
            human_score = human.score(plagiarism, ai_score, para["citations"])
            originality = orig.score(plagiarism, ai_score)
            
            # Get refinement suggestions
            suggestions = refinement_suggestions(
                plagiarism, 
                ai_score, 
                human_contribution=human_score,
                citations=len(para["citations"])
            )
            
            results.append({
                "section": para["section"],
                "paragraph": para["paragraph_id"],
                "text_preview": para["text"][:200] + "..." if len(para["text"]) > 200 else para["text"],
                "plagiarism": round(plagiarism, 3),
                "ai_usage": round(ai_score, 3),
                "human_contribution": round(human_score, 3),
                "originality": round(originality, 3),
                "citations_count": len(para["citations"]),
                "refinement_suggestions": suggestions
            })
        
        print(f"\n      ✓ Completed analysis of {len(paper)} paragraphs\n")
        
        # Generate report
        print(f"[6/7] Generating validation report")
        metadata = {
            "source_file": os.path.basename(pdf_path),
            "corpus_files": len(corpus_texts) if corpus_texts else 0,
            "analysis_date": datetime.now().isoformat()
        }
        
        report = generate_report(results, metadata=metadata)
        print(f"      ✓ Report generated\n")
        
        # Save reports
        print(f"[7/7] Saving reports to: {output_dir}")
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # Save JSON report
        json_path = os.path.join(output_dir, f"{base_name}_report.json")
        save_report(report, json_path)
        print(f"      ✓ JSON report saved: {json_path}")
        
        # Save HTML report
        html_path = os.path.join(output_dir, f"{base_name}_report.html")
        generate_html_report(report, html_path)
        print(f"      ✓ HTML report saved: {html_path}")
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"Analysis Complete!")
        print(f"{'='*80}")
        print(f"\nIntegrity Grade: {report['executive_summary']['integrity_grade']}")
        print(f"Originality Score: {report['executive_summary']['overall_originality_score']:.1%}")
        print(f"Plagiarism Score: {report['executive_summary']['overall_plagiarism_score']:.1%}")
        print(f"AI Detection Score: {report['executive_summary']['overall_ai_detection_score']:.1%}")
        print(f"Human Contribution: {report['executive_summary']['overall_human_contribution_score']:.1%}")
        print(f"\nStatus: {report['executive_summary']['status']}")
        
        if report['flagged_sections']:
            print(f"\n⚠ Flagged Sections: {len(report['flagged_sections'])}")
            for item in report['flagged_sections'][:3]:  # Show top 3
                print(f"   - {item['section']}: {', '.join(item['reason'])}")
        
        print(f"\n{'='*80}\n")
        
        return report
        
    except Exception as e:
        print(f"\n✗ Error processing paper: {e}")
        import traceback
        traceback.print_exc()
        return None

def process_directory(input_dir, corpus_dir=None, output_dir="output"):
    """
    Process all PDF files in a directory.
    
    Args:
        input_dir: Directory containing PDFs to analyze
        corpus_dir: Directory containing reference corpus PDFs
        output_dir: Directory to save output reports
    """
    pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
    
    print(f"\nFound {len(pdf_files)} PDF files to process\n")
    
    for idx, pdf_file in enumerate(pdf_files, 1):
        print(f"\nProcessing file {idx}/{len(pdf_files)}: {pdf_file}")
        pdf_path = os.path.join(input_dir, pdf_file)
        process_paper(pdf_path, corpus_dir, output_dir)

if __name__ == '__main__':
    # Command-line interface
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  Single file: python main.py <pdf_path> [corpus_dir] [output_dir]")
        print("  Directory:   python main.py --dir <input_dir> [corpus_dir] [output_dir]")
        print("\nExamples:")
        print("  python main.py paper.pdf corpus/ output/")
        print("  python main.py --dir papers/ corpus/ output/")
        print()
        
        # Create example files for demonstration
        print("Creating example files for testing...")
        
        os.makedirs("example_corpus", exist_ok=True)
        os.makedirs("example_output", exist_ok=True)
        
        # Note: This creates dummy files - real usage requires actual PDFs
        if not os.path.exists("example_draft.pdf"):
            with open("example_draft.pdf", "w") as f:
                f.write("Example PDF content (replace with real PDF)")
        
        if not os.path.exists("example_corpus/corpus1.pdf"):
            with open("example_corpus/corpus1.pdf", "w") as f:
                f.write("Example corpus PDF (replace with real PDF)")
        
        print("\nNote: Example files created are placeholders.")
        print("Replace them with actual PDF files and run GROBID server at http://localhost:8070")
        print("\nTo install and run GROBID:")
        print("  1. Download from: https://github.com/kermitt2/grobid")
        print("  2. Run: ./gradlew run")
        print()
        
    else:
        if sys.argv[1] == "--dir":
            input_dir = sys.argv[2] if len(sys.argv) > 2 else "papers"
            corpus_dir = sys.argv[3] if len(sys.argv) > 3 else None
            output_dir = sys.argv[4] if len(sys.argv) > 4 else "output"
            process_directory(input_dir, corpus_dir, output_dir)
        else:
            pdf_path = sys.argv[1]
            corpus_dir = sys.argv[2] if len(sys.argv) > 2 else None
            output_dir = sys.argv[3] if len(sys.argv) > 3 else "output"
            process_paper(pdf_path, corpus_dir, output_dir)
