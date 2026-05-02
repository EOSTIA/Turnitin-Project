"""
Simple script to test plagiarism detection on a research paper.
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from ingest import parse_pdf
from embedding import Embedder
from vector_store import VectorStore
from plagiarism import PlagiarismEngine
from ai_detection import AIDetector
from human_score import HumanContribution
from originality import OriginalityScorer
from refinement import refinement_suggestions
from report import generate_report, save_report, generate_html_report

def test_paper(pdf_path):
    """
    Test a single research paper for plagiarism and AI detection.
    
    Args:
        pdf_path: Path to the PDF file
    """
    print(f"\n{'='*80}")
    print(f"Academic Integrity Validation Engine - Test")
    print(f"{'='*80}\n")
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: PDF file not found at {pdf_path}")
        return
    
    try:
        # Step 1: Parse the PDF
        print(f"[1/7] 📄 Parsing PDF: {os.path.basename(pdf_path)}")
        paragraphs = parse_pdf(pdf_path)
        print(f"      ✓ Extracted {len(paragraphs)} paragraphs")
        
        # Step 2: Initialize components
        print(f"\n[2/7] 🔧 Initializing detection engines...")
        embedder = Embedder()
        plagiarism_engine = PlagiarismEngine()
        ai_detector = AIDetector()
        human_scorer = HumanContribution()
        originality_scorer = OriginalityScorer()
        print(f"      ✓ All engines initialized")
        
        # Step 3: Create embeddings
        print(f"\n[3/7] 🧠 Creating text embeddings...")
        texts = [p["text"] for p in paragraphs]
        embeddings = embedder.encode(texts)
        print(f"      ✓ Created {len(embeddings)} embeddings")
        
        # Step 4: Build vector store (using the paper itself as reference)
        print(f"\n[4/7] 📊 Building reference corpus...")
        store = VectorStore(dim=len(embeddings[0]))
        # store.add(embeddings, texts)
        print(f"      ✓ Added {len(texts)} items to vector store")
        
        # Step 5: Analyze each paragraph
        print(f"\n[5/7] 🔍 Analyzing paragraphs...")
        results = []
        
        for i, (para, emb) in enumerate(zip(paragraphs, embeddings), 1):
            print(f"      Analyzing paragraph {i}/{len(paragraphs)}...", end="\r")
            
            # Get scores
            plagiarism = plagiarism_engine.score(para, emb, store)
            ai_score = ai_detector.score(para["text"])
            citations = para.get("citations", [])
            human_score = human_scorer.score(plagiarism, ai_score, citations)
            originality = originality_scorer.score(plagiarism, ai_score)
            
            # Get refinement suggestions
            suggestions = refinement_suggestions(
                plagiarism, ai_score, human_score, len(citations)
            )
            
            results.append({
                "section": para.get("section", "Unknown"),
                "paragraph_id": para.get("paragraph_id", f"p{i}"),
                "text": para["text"][:200] + "..." if len(para["text"]) > 200 else para["text"],
                "plagiarism": plagiarism,
                "ai_usage": ai_score,
                "human_contribution": human_score,
                "originality": originality,
                "citations_count": len(citations),
                "refinement": suggestions
            })
        
        print(f"      ✓ Analyzed {len(results)} paragraphs" + " " * 30)
        
        # Step 6: Generate report
        print(f"\n[6/7] 📝 Generating comprehensive report...")
        report = generate_report(results, metadata={
            "filename": os.path.basename(pdf_path),
            "filepath": pdf_path,
            "total_paragraphs": len(paragraphs)
        })
        
        # Step 7: Save reports
        print(f"\n[7/7] 💾 Saving reports...")
        output_dir = "test_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save JSON report
        json_path = os.path.join(output_dir, "validation_report.json")
        save_report(report, json_path)
        print(f"      ✓ JSON report saved: {json_path}")
        
        # Save HTML report
        html_path = os.path.join(output_dir, "validation_report.html")
        generate_html_report(report, html_path)
        print(f"      ✓ HTML report saved: {html_path}")
        
        # Display summary
        print(f"\n{'='*80}")
        print(f"VALIDATION SUMMARY")
        print(f"{'='*80}\n")
        
        print(f"📊 Overall Scores:")
        summary = report["executive_summary"]
        print(f"   • Plagiarism:         {summary['overall_plagiarism_score']:.1%}")
        print(f"   • AI Usage:           {summary['overall_ai_detection_score']:.1%}")
        print(f"   • Human Contribution: {summary['overall_human_contribution_score']:.1%}")
        print(f"   • Originality:        {summary['overall_originality_score']:.1%}")
        
        print(f"\n🎓 Academic Integrity Grade: {summary['integrity_grade']}")
        
        print(f"\n📈 Flagged Sections: {len(report['flagged_sections'])}")
        if report['flagged_sections']:
            print(f"\n   High Priority Issues:")
            for section in report['flagged_sections'][:3]:
                reason_text = ", ".join(section.get('reason', [])) or "No details"
                print(f"   • {section['section']} - {section['severity']} - {reason_text}")
        
        print(f"\n✅ Reports saved to: {os.path.abspath(output_dir)}")
        print(f"\n{'='*80}\n")
        
        return report
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    # Test with your PDF
    pdf_path = r"6016798.pdf"
    
    print("Starting plagiarism detection test...")
    print(f"Target PDF: {pdf_path}\n")
    
    result = test_paper(pdf_path)
    
    if result:
        print("✅ Test completed successfully!")
        print("Check the 'test_output' folder for detailed reports.")
    else:
        print("❌ Test failed. Please check the error messages above.")