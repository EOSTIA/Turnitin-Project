# Quick Start Guide

## Academic Integrity Validation Engine

### 🚀 Quick Setup (5 minutes)

#### Step 1: Install Dependencies
```bash
cd turnitin_engine
pip install -r requirements.txt
```

#### Step 2: Setup GROBID (for PDF processing)
Download and run GROBID:
```bash
# Option 1: Docker (easiest)
docker pull lfoppiano/grobid:0.8.0
docker run --rm --init --ulimit core=0 -p 8070:8070 lfoppiano/grobid:0.8.0

# Option 2: Manual
git clone https://github.com/kermitt2/grobid.git
cd grobid
./gradlew run
```

Verify GROBID is running: Visit `http://localhost:8070` in your browser

#### Step 3: Test the Installation
```bash
python test_installation.py
```

### 📝 Quick Examples

#### Example 1: Analyze Text (No PDF needed)
```python
from detector import IntegrityDetector

# Initialize
detector = IntegrityDetector()
detector.build_corpus([])

# Analyze text
result = detector.analyze_text(
    text="Your text here...",
    citations=["Citation 1"]
)

print(f"Originality: {result['scores']['originality']:.1%}")
print(f"AI Detection: {result['scores']['ai_detection']:.1%}")
print(f"Status: {result['status']}")
```

#### Example 2: Analyze PDF
```bash
python main.py my_paper.pdf reference_papers/ output/
```

#### Example 3: Run Examples
```bash
python example_usage.py
```

### 📊 Understanding the Scores

**Originality Score** (Higher is better)
- 85-100%: Exceptional ✅
- 70-84%: Excellent ✅
- 55-69%: Good ⚠️
- Below 55%: Needs work ❌

**AI Detection Score** (Lower is better)
- 0-35%: Likely human ✅
- 35-60%: Some AI indicators ⚠️
- 60%+: Likely AI ❌

**Plagiarism Score** (Lower is better)
- 0-25%: Acceptable ✅
- 25-40%: Review needed ⚠️
- 40%+: Major issues ❌

### 🛠️ Troubleshooting

**"GROBID failed" error:**
- Ensure GROBID is running at http://localhost:8070
- Try: `curl http://localhost:8070/api/version`

**"Model not found" error:**
- First run downloads AI models (2-3GB)
- Requires internet connection
- Downloads to ~/.cache/huggingface/

**Slow processing:**
- First run is slower (model loading)
- Use GPU for faster processing
- Batch process multiple files

### 🎯 Next Steps

1. **Read the full README.md** for detailed documentation
2. **Run example_usage.py** to see all features
3. **Configure config.py** to customize thresholds
4. **Build your reference corpus** for plagiarism detection

### 📚 Key Files

- `main.py` - Process PDFs
- `detector.py` - Python API
- `example_usage.py` - Usage examples
- `config.py` - Configuration
- `README.md` - Full documentation

### 💡 Tips

1. **Build a good corpus**: More reference papers = better plagiarism detection
2. **Adjust thresholds**: Edit config.py for your use case
3. **Use batch processing**: Process multiple files together
4. **Check HTML reports**: Easier to read than JSON

### 🆘 Getting Help

1. Check the README.md
2. Run test_installation.py
3. Review example_usage.py
4. Verify GROBID is running
5. Check config.py settings

---

**Ready to start?**
```bash
python example_usage.py
```
