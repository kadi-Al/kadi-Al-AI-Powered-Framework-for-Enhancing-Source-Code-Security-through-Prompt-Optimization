from datetime import datetime
from database import db

class ReportGenerator:
    def __init__(self):
        pass
    
    def generate_html_report(self, data):
        try:
            # Generate HTML content
            html_content = self._render_html_template(data)
            
            # Add HTML content to data
            data['html_content'] = html_content
            
            # Save to database
            report_id = db.save_report(data)
            
            return {
                'success': True,
                'report_id': report_id,
                'message': f'Report generated successfully (ID: {report_id})'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate report: {str(e)}'
            }
    
    def _render_html_template(self, data):
        """Render HTML template from data"""
        timestamp = data.get('timestamp', datetime.now().isoformat())
        formatted_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
        
        # Get security score from data
        security_score = data.get('final_security_score', 8.5)
        severity_level = data.get('final_severity_level', 'MODERATE')
        
        # Get color based on score
        score_color = self._get_score_color(security_score)
        
        # Get vulnerability counts
        vuln_counts = data.get('vulnerability_summary', {'high': 0, 'medium': 0, 'low': 0})
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Security Analysis Report - AI-Powered Security Framework</title>
            <!-- Link to the main CSS file -->
            <link rel="stylesheet" href="/static/css/style.css">
            <!-- Embedded report-specific styles -->
            <style>
                /* Score colors */
                .score-value.excellent {{ color: #10b981; }}
                .score-value.good {{ color: #3b82f6; }}
                .score-value.moderate {{ color: #f59e0b; }}
                .score-value.poor {{ color: #ef4444; }}
                .score-value.critical {{ color: #dc2626; }}
                
                .severity-level {{
                    display: inline-block;
                    padding: 3px 10px;
                    border-radius: 15px;
                    font-size: 0.9em;
                    font-weight: bold;
                    margin-left: 10px;
                }}
                .severity-level.excellent {{ background: #10b981; color: white; }}
                .severity-level.good {{ background: #3b82f6; color: white; }}
                .severity-level.moderate {{ background: #f59e0b; color: black; }}
                .severity-level.poor {{ background: #ef4444; color: white; }}
                .severity-level.critical {{ background: #dc2626; color: white; }}
                
                .vulnerability-stats {{
                    display: flex;
                    gap: 10px;
                    margin-top: 10px;
                    justify-content: center;
                }}
                .vuln-stat {{
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-size: 0.9em;
                    font-weight: bold;
                }}
                .vuln-stat.high {{ background: rgba(239, 68, 68, 0.2); color: #fca5a5; }}
                .vuln-stat.medium {{ background: rgba(245, 158, 11, 0.2); color: #fde68a; }}
                .vuln-stat.low {{ background: rgba(34, 197, 94, 0.2); color: #86efac; }}
                
                /* Report specific styles */

                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 0 20px;
                }}

                header {{
                    background: #502db9; 
                    color: white;
                    padding: 2rem 0;
                    text-align: center;
                    margin-bottom: 2rem;
                    border-radius: 0 0 1rem 1rem;
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
                }}

                header h1 {{
                    font-size: 3rem;
                    margin-bottom: 0.5rem;
                    font-weight: 800;
                    background: linear-gradient(to right, #a5b4fc, #c4b5fd);
                    -webkit-background-clip: text;
                    background-clip: text;
                    -webkit-text-fill-color: transparent;
                    color: transparent;
                }}

                header .sub-header {{
                    font-size: 1rem; 
                    font-weight: 400; 
                    color: rgba(226, 232, 240, 0.8); 
                    margin-top: 0.5rem;
                }}

                .report-container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                
                .report-header {{
                    background: #502db9;
                    color: white;
                    padding: 2rem 0;
                    text-align: center;
                    margin-bottom: 2rem;
                    border-radius: 0 0 1rem 1rem;
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
                }}
                
                .report-header h1 {{
                    font-size: 3rem;
                    margin-bottom: 0.5rem;
                    font-weight: 800;
                    background: linear-gradient(to right, #a5b4fc, #c4b5fd);
                    -webkit-background-clip: text;
                    background-clip: text;
                    -webkit-text-fill-color: transparent;
                    color: transparent;
                }}
                
                .report-header h2 {{
                    font-size: 1.8rem;
                    margin-bottom: 1rem;
                    color: #e2e8f0;
                }}
                
                .report-main {{
                    background: rgba(30, 41, 59, 0.7);
                    padding: 2rem;
                    border-radius: 1rem;
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(79, 70, 229, 0.3);
                    margin-bottom: 2rem;
                }}
                
                .report-section {{
                    background: rgba(30, 41, 59, 0.8);
                    border: 1px solid rgba(79, 70, 229, 0.3);
                    border-radius: 0.75rem;
                    padding: 1.5rem;
                    margin-bottom: 1.5rem;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
                }}
                
                .report-section h3 {{
                    margin-bottom: 1rem;
                    color: #a5b4fc;
                    border-bottom: 1px solid rgba(79, 70, 229, 0.3);
                    padding-bottom: 0.5rem;
                }}
                
                .code-block {{
                    background: rgba(15, 23, 42, 0.9);
                    padding: 1rem;
                    border-radius: 0.5rem;
                    overflow-x: auto;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9rem;
                    line-height: 1.4;
                    color: #e2e8f0;
                    border: 1px solid rgba(79, 70, 229, 0.2);
                    margin-top: 0.5rem;
                }}
                
                .analysis-text {{
                    background: rgba(15, 23, 42, 0.9);
                    padding: 1rem;
                    border-radius: 0.5rem;
                    color: #e2e8f0;
                    line-height: 1.6;
                    border: 1px solid rgba(79, 70, 229, 0.2);
                    margin-top: 0.5rem;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }}
                
                .report-footer {{
                    text-align: center;
                    padding: 2rem 0;
                    margin-top: 2rem;
                    background: rgba(15, 23, 42, 0.8);
                    color: #94a3b8;
                    border-radius: 1rem 1rem 0 0;
                }}
                
                .report-metadata {{
                    color: #cbd5e1;
                    font-size: 0.9rem;
                    margin-top: 0.5rem;
                }}
                
                .language-badge.report {{
                    display: inline-block;
                    padding: 2px 8px;
                    background: #4f46e5;
                    color: white;
                    border-radius: 0.25rem;
                    font-size: 0.8em;
                    margin-left: 0.5rem;
                }}
                
                .language-badge.report.c {{ background: #3b82f6; }}
                .language-badge.report.python {{ background: #f59e0b; }}
                .language-badge.report.java {{ background: #ef4444; }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                <h1>AI-Powered Security Framework</h1>
                    <p class="sub-header">Security Analysis Report</p>
                    <div class="report-metadata">
                        Generated on: {formatted_time}
                    </div>
                    {f'<div class="report-metadata">Language: <span class="language-badge report {data.get("detected_language", "python").lower()}">{data.get("detected_language", "Unknown").upper()}</span></div>' if data.get('detected_language') else ''}
                </header>
                </div>

                <div class="report-main">
                    <!-- Security Status Information -->
                    {self._get_security_status_html(data)}

                    <div class="report-section">
                        <h3>Original Prompt</h3>
                        <div class="analysis-text">
                            {data.get('user_prompt', '')}
                        </div>
                    </div>

                    <div class="report-section">
                        <h3>Enhanced Prompt</h3>
                        <div class="analysis-text">
                            {data.get('enhanced_prompt', '')}
                        </div>
                    </div>

                    <div class="report-section">
                        <h3>Generated Code</h3>
                        <div class="code-block">
                            <pre>{data.get('generated_code', '')}</pre>
                        </div>
                    </div>

                    <div class="report-section">
                        <h3>Security Analysis & Recommendations</h3>
                        <div class="analysis-text">
                            <div class="security-score">
                                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                                    <span style="font-weight: bold; margin-right: 0.5rem;">Security Score:</span>
                                    <span class="score-value {severity_level.lower()}" style="color: {score_color}; font-weight: bold; font-size: 1.2rem;">
                                        {security_score} / 10.0
                                    </span>
                                    <span class="severity-level {severity_level.lower()}">{severity_level}</span>
                                </div>
                                <div class="vulnerability-stats">
                                    <span class="vuln-stat high">High: {vuln_counts['high']}</span>
                                    <span class="vuln-stat medium">Medium: {vuln_counts['medium']}</span>
                                    <span class="vuln-stat low">Low: {vuln_counts['low']}</span>
                                </div>
                            </div>
                            <div style="margin-top: 1.5rem;">
                                {data.get('analysis_results', 'No analysis results available')}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="report-footer">
                    <p>&copy; 2025 AI-Powered Security Framework | Created by Kady Alsaif, Shatha Alharbi, Shahad Alqahtani</p>
                    <p>Report ID: {data.get('timestamp', timestamp)}</p>
                    <p>Analysis attempts: {data.get('fix_attempts', 0)}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _get_score_color(self, score):
        """Get color based on security score"""
        if score >= 9.0:
            return "#10b981"  # Green
        elif score >= 7.0:
            return "#3b82f6"  # Blue
        elif score >= 5.0:
            return "#f59e0b"  # Yellow
        elif score >= 3.0:
            return "#ef4444"  # Red
        else:
            return "#dc2626"  # Dark Red
    
    def _get_security_status_html(self, data):
        """Generate security status HTML based on analysis results"""
        fix_attempts = data.get('fix_attempts', 0)
        had_high_severity = data.get('had_high_severity', False)
        security_score = data.get('final_security_score', 0)
        
        if fix_attempts > 0:
            return f'''
            <div class="report-section" style="background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.5);">
                <h3>Automatic Security Fixes Applied</h3>
                <p>{fix_attempts} fix attempt(s) were made to improve security score.</p>
                <p>Security score: <strong>{security_score}/10.0</strong></p>
            </div>
            '''
        elif had_high_severity:
            return f'''
            <div class="report-section" style="background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.5);">
                <h3>High Severity Issues Detected</h3>
                <p>Automatic fixes were attempted but high severity issues remain.</p>
                <p>Security score: <strong>{security_score}/10.0</strong> - Please review carefully.</p>
            </div>
            '''
        else:
            score_color = self._get_score_color(security_score)
            return f'''
            <div class="report-section" style="background: rgba(34, 197, 94, 0.1); border-color: rgba(34, 197, 94, 0.5);">
                <h3>Security Analysis Complete</h3>
                <p>Security score: <strong style="color: {score_color}">{security_score}/10.0</strong></p>
                <p>The code has been analyzed and meets security standards.</p>
            </div>
            '''
    
    def get_report(self, report_id):
        """Get report from database"""
        return db.get_report(report_id)
    
    def get_all_reports(self, limit=50):
        """Get all reports from database"""
        return db.get_all_reports(limit)
    
    def get_report_html(self, report_id):
        """Get HTML content for a report"""
        report = db.get_report(report_id)
        return report.get('html_content') if report else None