
from flask import Flask, render_template, request, jsonify, send_file
import os
from datetime import datetime
import tempfile

from utils.ollama_client import OllamaClient
from services.prompt_enhancer import PromptEnhancer
from services.code_generator import CodeGenerator
from services.security_analyzer import SecurityAnalyzer
from services.code_analyzer import CodeAnalyzer
from services.report_generator import ReportGenerator
from database import db  

app = Flask(__name__)
app.secret_key = 'hello its me'

ollama_client = OllamaClient()
prompt_enhancer = PromptEnhancer(ollama_client)
code_generator = CodeGenerator(ollama_client)
security_analyzer = SecurityAnalyzer(ollama_client)
code_analyzer = CodeAnalyzer(code_generator, security_analyzer)
report_generator = ReportGenerator()

@app.before_request
def check_ollama():
    if request.endpoint and request.endpoint.startswith('api'):
        if not ollama_client.check_ollama_health():
            return jsonify({'error': 'Ollama service is not available. Please make sure Ollama is running on http://localhost:11434'}), 503

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enhance')
def enhance():
    return render_template('enhance.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/reports')
def reports_list():
    """Route to display all reports"""
    reports = db.get_all_reports()
    return render_template('reports.html', reports=reports)

@app.route('/api/enhance-and-analyze', methods=['POST'])
def enhance_and_analyze():
    try:
        data = request.get_json()
        user_prompt = data.get('prompt', '').strip()
        language = data.get('language', 'python').lower()  
        
        if not user_prompt:
            return jsonify({'error': 'Prompt cannot be empty'}), 400
        
        if len(user_prompt) > 7000:
            return jsonify({'error': 'Prompt too long. Please keep it under 7000 characters.'}), 400
        
        # Step 1: Enhance prompt with language
        print(f"Step 1: Enhancing prompt for {language}...")
        enhanced_prompt = prompt_enhancer.enhance_prompt(user_prompt, language)
        
        # Step 2: Generate code with language
        print(f"Step 2: Generating {language} code...")
        generated_response = code_generator.generate_code(enhanced_prompt, language=language)
        
        # Step 3: Analyze code with feedback loop, passing language
        print(f"Step 3: Analyzing {language} code security with feedback loop...")
        analysis_results = code_analyzer.analyze_with_feedback_loop(generated_response, language)
        
        # Store results
        results_data = {
            'user_prompt': user_prompt,
            'enhanced_prompt': enhanced_prompt,
            'generated_code': analysis_results['final_code'],
            'original_code': generated_response,
            'detected_language': analysis_results.get('detected_language', language.title()),
            'analysis_results': analysis_results['final_analysis'],
            'fix_attempts': analysis_results['fix_attempts_made'],
            'had_high_severity': analysis_results['had_high_severity'],
            'analysis_history': analysis_results.get('analysis_history', []),
            'final_security_score': analysis_results.get('final_security_score', 8.5),
            'final_severity_level': analysis_results.get('final_severity_level', 'MODERATE'),
            'vulnerability_summary': analysis_results.get('vulnerability_summary', {'high': 0, 'medium': 0, 'low': 0}),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(results_data)
        
    except Exception as e:
        print(f"Error in enhance-and-analyze: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    try:
        data = request.get_json()
        
        # Use report generator service
        result = report_generator.generate_html_report(data)
        
        if result['success']:
            return jsonify({
                'report_id': result['report_id'],
                'message': result['message']
            })
        else:
            return jsonify({'error': result['error']}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-report')
def download_report():
    try:
        report_id = request.args.get('report_id')
        if not report_id:
            return jsonify({'error': 'Report ID is required'}), 400
        
        report = report_generator.get_report(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Create a temporary file with HTML content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(report.get('html_content', ''))
            temp_filename = f.name
        
        return send_file(temp_filename, as_attachment=True, download_name=f'security_report_{report_id}.html')
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/view-report')
def view_report():
    try:
        report_id = request.args.get('report_id')
        if not report_id:
            return jsonify({'error': 'Report ID is required'}), 400
        
        report = report_generator.get_report(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Return the HTML content directly
        html_content = report.get('html_content', '')
        if not html_content:
            return jsonify({'error': 'Report HTML content not found'}), 404
        
        # Return as HTML response
        from flask import Response
        return Response(html_content, mimetype='text/html')
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete-report', methods=['DELETE'])
def delete_report():
    try:
        report_id = request.args.get('report_id')
        if not report_id:
            return jsonify({'error': 'Report ID is required'}), 400
        
        db.delete_report(report_id)
        return jsonify({'success': True, 'message': 'Report deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports')
def get_reports_list():
    """API endpoint to get list of reports"""
    try:
        limit = request.args.get('limit', 50, type=int)
        reports = db.get_all_reports(limit)
        return jsonify({'reports': reports})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    try:
        services_health = {
            'ollama': ollama_client.check_ollama_health(),
            'database': os.path.exists('reports.db')  # Check if database file exists
        }
        
        all_healthy = all(services_health.values())
        
        return jsonify({
            'status': 'healthy' if all_healthy else 'degraded',
            'services': services_health,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('utils', exist_ok=True)
    os.makedirs('services', exist_ok=True)
    
    print("AI Security Framework starting...")
    print("Checking Ollama connection...")
    
    if ollama_client.check_ollama_health():
        print("Ollama is running and healthy")
    else:
        print("Ollama is not available. ")
     
    
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
