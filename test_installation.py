"""
Test Installation Script
Verifies that the Academic Integrity Validation Engine is properly installed.
"""

import sys
import importlib


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    required_modules = [
        'torch',
        'transformers',
        'sentence_transformers',
        'faiss',
        'numpy',
        'lxml',
        'requests'
    ]
    
    missing = []
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module} - MISSING")
            missing.append(module)
    
    if missing:
        print(f"\n❌ Missing modules: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("\n✅ All required modules installed!")
    return True


def test_custom_modules():
    """Test that custom modules are working."""
    print("\nTesting custom modules...")
    
    try:
        from embedding import Embedder
        print("  ✓ embedding.py")
        
        from vector_store import VectorStore
        print("  ✓ vector_store.py")
        
        from plagiarism import PlagiarismEngine
        print("  ✓ plagiarism.py")
        
        from ai_detection import AIDetector
        print("  ✓ ai_detection.py")
        
        from human_score import HumanContribution
        print("  ✓ human_score.py")
        
        from originality import OriginalityScorer
        print("  ✓ originality.py")
        
        from refinement import refinement_suggestions
        print("  ✓ refinement.py")
        
        from report import generate_report
        print("  ✓ report.py")
        
        from detector import IntegrityDetector
        print("  ✓ detector.py")
        
        print("\n✅ All custom modules loaded successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error loading custom modules: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_embedder():
    """Test the embedding functionality."""
    print("\nTesting embedder...")
    
    try:
        from embedding import Embedder
        
        embedder = Embedder()
        print("  ✓ Embedder initialized")
        
        # Test encoding
        test_texts = ["This is a test sentence.", "Another test sentence."]
        embeddings = embedder.encode(test_texts)
        
        print(f"  ✓ Encoded {len(test_texts)} texts")
        print(f"  ✓ Embedding dimension: {len(embeddings[0])}")
        
        print("\n✅ Embedder working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Embedder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_detector():
    """Test AI detection functionality."""
    print("\nTesting AI detector...")
    
    try:
        from ai_detection import AIDetector
        
        print("  ⏳ Initializing AI detector (this may take a moment)...")
        detector = AIDetector()
        print("  ✓ AI detector initialized")
        
        # Test detection
        test_text = "Machine learning is a subset of artificial intelligence."
        score = detector.score(test_text)
        
        print(f"  ✓ AI detection score: {score:.3f}")
        
        print("\n✅ AI detector working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ AI detector test failed: {e}")
        print("  Note: First run downloads models (~2-3GB)")
        import traceback
        traceback.print_exc()
        return False


def test_vector_store():
    """Test vector store functionality."""
    print("\nTesting vector store...")
    
    try:
        from vector_store import VectorStore
        import numpy as np
        
        # Create store
        dim = 384  # Common embedding dimension
        store = VectorStore(dim)
        print(f"  ✓ Vector store created (dim={dim})")
        
        # Add vectors
        embeddings = np.random.rand(5, dim).astype('float32')
        texts = [f"Text {i}" for i in range(5)]
        store.add(embeddings, texts)
        
        print(f"  ✓ Added {store.get_size()} vectors")
        
        # Search
        query = np.random.rand(dim).astype('float32')
        results = store.search(query, k=3)
        
        print(f"  ✓ Search returned {len(results)} results")
        
        print("\n✅ Vector store working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Vector store test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_plagiarism_engine():
    """Test plagiarism detection."""
    print("\nTesting plagiarism engine...")
    
    try:
        from plagiarism import PlagiarismEngine
        
        engine = PlagiarismEngine()
        print("  ✓ Plagiarism engine initialized")
        
        # Test lexical similarity
        text1 = "The quick brown fox jumps over the lazy dog"
        text2 = "The quick brown fox jumps over the lazy dog"
        sim = engine.lexical_similarity(text1, text2)
        
        print(f"  ✓ Lexical similarity: {sim:.3f}")
        
        # Test n-gram overlap
        ngram_sim = engine.ngram_overlap(text1, text2, n=3)
        print(f"  ✓ N-gram overlap: {ngram_sim:.3f}")
        
        print("\n✅ Plagiarism engine working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Plagiarism engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integrity_detector():
    """Test the integrated detector."""
    print("\nTesting integrity detector...")
    
    try:
        from detector import IntegrityDetector
        
        print("  ⏳ Initializing detector (this may take a moment)...")
        detector = IntegrityDetector()
        print("  ✓ Detector initialized")
        
        # Build corpus
        corpus = ["This is a reference text.", "Another reference document."]
        detector.build_corpus(corpus)
        print(f"  ✓ Corpus built with {len(corpus)} documents")
        
        # Analyze text
        test_text = "Machine learning has revolutionized artificial intelligence."
        result = detector.analyze_text(test_text, citations=["Smith 2020"])
        
        print(f"  ✓ Analysis completed")
        print(f"    - Originality: {result['scores']['originality']:.3f}")
        print(f"    - AI detection: {result['scores']['ai_detection']:.3f}")
        print(f"    - Plagiarism: {result['scores']['plagiarism']:.3f}")
        print(f"    - Status: {result['status']}")
        
        print("\n✅ Integrity detector working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Integrity detector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_grobid():
    """Test GROBID server connectivity."""
    print("\nTesting GROBID server...")
    
    try:
        import requests
        
        grobid_url = "http://localhost:8070/api/version"
        
        print(f"  ⏳ Checking GROBID at {grobid_url}...")
        response = requests.get(grobid_url, timeout=5)
        
        if response.status_code == 200:
            version = response.text
            print(f"  ✓ GROBID is running (version: {version.strip()})")
            print("\n✅ GROBID server is accessible!")
            return True
        else:
            print(f"  ⚠️  GROBID returned status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("  ❌ GROBID is NOT running")
        print("\n⚠️  GROBID is required for PDF processing")
        print("  Start GROBID with:")
        print("    docker run -p 8070:8070 lfoppiano/grobid:0.8.0")
        print("  or visit: https://github.com/kermitt2/grobid")
        return False
        
    except Exception as e:
        print(f"  ❌ Error checking GROBID: {e}")
        return False


def run_all_tests():
    """Run all tests."""
    print("="*80)
    print("Academic Integrity Validation Engine - Installation Test")
    print("="*80)
    
    tests = [
        ("Required Modules", test_imports),
        ("Custom Modules", test_custom_modules),
        ("Embedder", test_embedder),
        ("Vector Store", test_vector_store),
        ("Plagiarism Engine", test_plagiarism_engine),
        ("AI Detector", test_ai_detector),
        ("Integrity Detector", test_integrity_detector),
        ("GROBID Server", test_grobid),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Installation successful!")
        print("\nNext steps:")
        print("  1. Read QUICKSTART.md for quick start guide")
        print("  2. Run: python example_usage.py")
        print("  3. Read README.md for full documentation")
    elif passed == total - 1 and not results[-1][1]:  # Only GROBID failed
        print("\n⚠️  Installation mostly successful!")
        print("  Note: GROBID is only needed for PDF processing")
        print("  You can still use the text analysis features")
        print("\nNext steps:")
        print("  1. For PDF support, install GROBID (see QUICKSTART.md)")
        print("  2. Run: python example_usage.py")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("  Try: pip install -r requirements.txt")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    run_all_tests()
