import json
from datetime import datetime
import statistics

def generate_report(results, metadata=None):
    """
    Generate a comprehensive validation report.
    
    Args:
        results: List of paragraph-level analysis results
        metadata: Optional metadata about the document
    
    Returns:
        Comprehensive report dictionary
    """
    if not results:
        return {
            "error": "No results to generate report",
            "timestamp": datetime.now().isoformat()
        }
    
    # Calculate overall statistics
    plagiarism_scores = [r["plagiarism"] for r in results]
    ai_scores = [r["ai_usage"] for r in results]
    human_scores = [r["human_contribution"] for r in results]
    originality_scores = [r["originality"] for r in results]
    
    # Overall scores
    overall_plagiarism = statistics.mean(plagiarism_scores)
    overall_ai = statistics.mean(ai_scores)
    overall_human = statistics.mean(human_scores)
    overall_originality = statistics.mean(originality_scores)
    
    # Distribution analysis
    def categorize_score(score, thresholds={'high': 0.6, 'medium': 0.3}):
        if score > thresholds['high']:
            return 'high'
        elif score > thresholds['medium']:
            return 'medium'
        else:
            return 'low'
    
    plagiarism_distribution = {
        'high': sum(1 for s in plagiarism_scores if s > 0.4),
        'medium': sum(1 for s in plagiarism_scores if 0.25 < s <= 0.4),
        'low': sum(1 for s in plagiarism_scores if s <= 0.25)
    }
    
    ai_distribution = {
        'high': sum(1 for s in ai_scores if s > 0.6),
        'medium': sum(1 for s in ai_scores if 0.35 < s <= 0.6),
        'low': sum(1 for s in ai_scores if s <= 0.35)
    }
    
    # Section-wise analysis
    sections_summary = {}
    for result in results:
        section = result["section"]
        if section not in sections_summary:
            sections_summary[section] = {
                'paragraphs': [],
                'avg_plagiarism': 0,
                'avg_ai': 0,
                'avg_originality': 0,
                'avg_human': 0,
                'flagged_count': 0
            }
        
        sections_summary[section]['paragraphs'].append(result)
        
        # Check if flagged
        if result['plagiarism'] > 0.4 or result['ai_usage'] > 0.6:
            sections_summary[section]['flagged_count'] += 1
    
    # Calculate section averages
    for section, data in sections_summary.items():
        paras = data['paragraphs']
        data['avg_plagiarism'] = round(statistics.mean([p['plagiarism'] for p in paras]), 3)
        data['avg_ai'] = round(statistics.mean([p['ai_usage'] for p in paras]), 3)
        data['avg_originality'] = round(statistics.mean([p['originality'] for p in paras]), 3)
        data['avg_human'] = round(statistics.mean([p['human_contribution'] for p in paras]), 3)
        data['paragraph_count'] = len(paras)
    
    # Identify problematic sections
    flagged_sections = [
        {
            'section': section,
            'reason': [],
            'severity': 'LOW'
        }
        for section, data in sections_summary.items()
        if data['avg_plagiarism'] > 0.3 or data['avg_ai'] > 0.5
    ]
    
    for item in flagged_sections:
        section = item['section']
        data = sections_summary[section]
        if data['avg_plagiarism'] > 0.6:
            item['reason'].append(f"High plagiarism ({data['avg_plagiarism']:.1%})")
            item['severity'] = 'CRITICAL'
        elif data['avg_plagiarism'] > 0.4:
            item['reason'].append(f"Elevated plagiarism ({data['avg_plagiarism']:.1%})")
            item['severity'] = 'HIGH'
        elif data['avg_plagiarism'] > 0.3:
            item['reason'].append(f"Moderate plagiarism ({data['avg_plagiarism']:.1%})")
            if item['severity'] not in ['CRITICAL', 'HIGH']:
                item['severity'] = 'MEDIUM'
        
        if data['avg_ai'] > 0.7:
            item['reason'].append(f"Very high AI probability ({data['avg_ai']:.1%})")
            item['severity'] = 'CRITICAL'
        elif data['avg_ai'] > 0.6:
            item['reason'].append(f"High AI probability ({data['avg_ai']:.1%})")
            if item['severity'] != 'CRITICAL':
                item['severity'] = 'HIGH'
        elif data['avg_ai'] > 0.5:
            item['reason'].append(f"Moderate AI probability ({data['avg_ai']:.1%})")
            if item['severity'] not in ['CRITICAL', 'HIGH']:
                item['severity'] = 'MEDIUM'
    
    # Overall assessment
    def get_integrity_grade(plag, ai, human):
        if plag > 0.6 or ai > 0.7:
            return 'F - Fails academic integrity standards'
        elif plag > 0.4 or ai > 0.6:
            return 'D - Major revisions required'
        elif plag > 0.3 or ai > 0.5:
            return 'C - Significant improvements needed'
        elif plag > 0.2 or ai > 0.4 or human < 0.6:
            return 'B - Good with minor revisions'
        else:
            return 'A - Excellent originality and integrity'
    
    integrity_grade = get_integrity_grade(overall_plagiarism, overall_ai, overall_human)
    
    # Generate recommendations
    recommendations = []
    if overall_plagiarism > 0.4:
        recommendations.append("Review and revise sections with high plagiarism scores")
        recommendations.append("Add proper citations for all referenced material")
        recommendations.append("Ensure all paraphrasing is substantive and original")
    
    if overall_ai > 0.6:
        recommendations.append("Add more personal insights and original analysis")
        recommendations.append("Include specific examples from your own research")
        recommendations.append("Vary writing style to be more natural and human-like")
    
    if overall_human < 0.5:
        recommendations.append("Increase human contribution through critical analysis")
        recommendations.append("Add unique perspectives and interpretations")
        recommendations.append("Include more citations to support original arguments")
    
    if not recommendations:
        recommendations.append("Content demonstrates strong originality")
        recommendations.append("Continue maintaining high academic integrity standards")
    
    # Build comprehensive report
    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "document_info": metadata or {},
            "total_paragraphs": len(results),
            "total_sections": len(sections_summary)
        },
        "executive_summary": {
            "integrity_grade": integrity_grade,
            "overall_originality_score": round(overall_originality, 3),
            "overall_plagiarism_score": round(overall_plagiarism, 3),
            "overall_ai_detection_score": round(overall_ai, 3),
            "overall_human_contribution_score": round(overall_human, 3),
            "status": "PASS" if overall_plagiarism < 0.3 and overall_ai < 0.5 else "NEEDS REVIEW"
        },
        "detailed_statistics": {
            "plagiarism": {
                "mean": round(overall_plagiarism, 3),
                "median": round(statistics.median(plagiarism_scores), 3),
                "std_dev": round(statistics.stdev(plagiarism_scores) if len(plagiarism_scores) > 1 else 0, 3),
                "min": round(min(plagiarism_scores), 3),
                "max": round(max(plagiarism_scores), 3),
                "distribution": plagiarism_distribution
            },
            "ai_detection": {
                "mean": round(overall_ai, 3),
                "median": round(statistics.median(ai_scores), 3),
                "std_dev": round(statistics.stdev(ai_scores) if len(ai_scores) > 1 else 0, 3),
                "min": round(min(ai_scores), 3),
                "max": round(max(ai_scores), 3),
                "distribution": ai_distribution
            },
            "human_contribution": {
                "mean": round(overall_human, 3),
                "median": round(statistics.median(human_scores), 3),
                "std_dev": round(statistics.stdev(human_scores) if len(human_scores) > 1 else 0, 3),
                "min": round(min(human_scores), 3),
                "max": round(max(human_scores), 3)
            },
            "originality": {
                "mean": round(overall_originality, 3),
                "median": round(statistics.median(originality_scores), 3),
                "std_dev": round(statistics.stdev(originality_scores) if len(originality_scores) > 1 else 0, 3),
                "min": round(min(originality_scores), 3),
                "max": round(max(originality_scores), 3)
            }
        },
        "section_analysis": sections_summary,
        "flagged_sections": sorted(flagged_sections, key=lambda x: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].index(x['severity']), reverse=True),
        "recommendations": recommendations,
        "detailed_results": results
    }
    
    return report

def save_report(report, filename="validation_report.json"):
    """Save report to JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return filename

def generate_html_report(report, filename="validation_report.html"):
    """Generate an HTML version of the report for easier reading."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Academic Integrity Validation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            .score {{ font-size: 24px; font-weight: bold; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .grade-a {{ background: #2ecc71; color: white; }}
            .grade-b {{ background: #3498db; color: white; }}
            .grade-c {{ background: #f39c12; color: white; }}
            .grade-d {{ background: #e67e22; color: white; }}
            .grade-f {{ background: #e74c3c; color: white; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
            .stat-card {{ background: #ecf0f1; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db; }}
            .stat-label {{ font-size: 12px; color: #7f8c8d; text-transform: uppercase; }}
            .stat-value {{ font-size: 28px; font-weight: bold; color: #2c3e50; }}
            .severity-critical {{ color: #e74c3c; font-weight: bold; }}
            .severity-high {{ color: #e67e22; font-weight: bold; }}
            .severity-medium {{ color: #f39c12; font-weight: bold; }}
            .severity-low {{ color: #95a5a6; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #34495e; color: white; }}
            tr:hover {{ background: #f5f5f5; }}
            .recommendations {{ background: #e8f5e9; padding: 20px; border-radius: 5px; border-left: 4px solid #4caf50; }}
            .recommendations li {{ margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Academic Integrity Validation Report</h1>
            <p><strong>Generated:</strong> {report['metadata']['generated_at']}</p>
            <p><strong>Total Paragraphs Analyzed:</strong> {report['metadata']['total_paragraphs']}</p>
            
            <div class="score grade-{report['executive_summary']['integrity_grade'][0].lower()}">
                Integrity Grade: {report['executive_summary']['integrity_grade']}
            </div>
            
            <h2>Executive Summary</h2>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-label">Originality Score</div>
                    <div class="stat-value">{report['executive_summary']['overall_originality_score']:.1%}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Human Contribution</div>
                    <div class="stat-value">{report['executive_summary']['overall_human_contribution_score']:.1%}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Plagiarism Score</div>
                    <div class="stat-value">{report['executive_summary']['overall_plagiarism_score']:.1%}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">AI Detection Score</div>
                    <div class="stat-value">{report['executive_summary']['overall_ai_detection_score']:.1%}</div>
                </div>
            </div>
            
            <h2>Recommendations</h2>
            <div class="recommendations">
                <ul>
                    {''.join(f'<li>{rec}</li>' for rec in report['recommendations'])}
                </ul>
            </div>
            
            <h2>Flagged Sections</h2>
            <table>
                <tr>
                    <th>Section</th>
                    <th>Severity</th>
                    <th>Issues</th>
                </tr>
                {''.join(f'''<tr>
                    <td>{item['section']}</td>
                    <td class="severity-{item['severity'].lower()}">{item['severity']}</td>
                    <td>{'<br>'.join(item['reason'])}</td>
                </tr>''' for item in report['flagged_sections'])}
            </table>
        </div>
    </body>
    </html>
    """
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    return filename
