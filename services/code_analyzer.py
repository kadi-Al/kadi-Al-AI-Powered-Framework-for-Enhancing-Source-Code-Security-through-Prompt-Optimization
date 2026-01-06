from utils.code_utils import CodeUtils
from services.code_generator import CodeGenerator
from services.security_analyzer import SecurityAnalyzer

class CodeAnalyzer:
    def __init__(self, code_generator, security_analyzer):
        self.code_generator = code_generator
        self.security_analyzer = security_analyzer
        self.code_utils = CodeUtils()
    
    def analyze_with_feedback_loop(self, code, language, max_fix_attempts=3):
        """Pass the original language explicitly"""
        current_code = code
        fix_attempts = 0
        all_analyses = []
        best_score = 0.0
        best_code = code
        
        print(f"Starting security analysis for {language.upper()} code...")
        
        for attempt in range(max_fix_attempts + 1):
            print(f"Analysis attempt {attempt + 1}/{max_fix_attempts + 1}")
            
            # Use the passed language parameter 
            analysis_results = self.security_analyzer.analyze_code_security(current_code, language)
            security_score = analysis_results.get('security_score', 0.0)
            has_high_severity = self.code_utils.has_high_severity_vulnerabilities(analysis_results['raw_analysis'])
            
            # Track best score and code
            if security_score > best_score:
                best_score = security_score
                best_code = current_code
            
            all_analyses.append({
                'attempt': attempt,
                'code': current_code,
                'analysis': analysis_results['raw_analysis'],
                'has_high_severity': has_high_severity,
                'vulnerability_counts': analysis_results['vulnerability_counts'],
                'security_score': security_score,
                'severity_level': self.security_analyzer.get_severity_level(security_score),
                'language': language  # Track language explicitly for any mistakes
            })
            
            print(f"Analysis {attempt + 1}: Score = {security_score}, High severity = {has_high_severity}, Language = {language}")
            
            # Check if we should attempt to fix and haven't reached max attempts
            if has_high_severity and attempt < max_fix_attempts:
                fix_attempts += 1
                print(f"High severity vulnerabilities found. Attempting fix #{fix_attempts} for {language} code...")
                
                vulnerability_summary = self.code_utils.extract_vulnerability_summary(analysis_results['raw_analysis'])
                
                try:
                    # Pass the language explicitly to generate_code
                    fixed_code = self.code_generator.generate_code(
                        current_code, 
                        vulnerability_summary,
                        language=language  # Pass language parameter
                    )
                    
                    if fixed_code and fixed_code.strip() and fixed_code != current_code:
                        current_code = fixed_code
                        print(f"Fix attempt #{fix_attempts} completed for {language}. Code updated.")
                    else:
                        print(f"Fix attempt resulted in no changes for {language}. Stopping fix attempts.")
                        break
                        
                except Exception as e:
                    print(f"Error during fix attempt for {language}: {e}")
                    break
            else:
                break
        
        # Use the best scoring code as final code
        final_code = best_code if best_score > 0 else current_code
        
        final_result = {
            'final_analysis': all_analyses[-1]['analysis'],
            'final_code': final_code,
            'original_code': code,
            'fix_attempts_made': fix_attempts,
            'analysis_history': all_analyses,
            'had_high_severity': any(analysis['has_high_severity'] for analysis in all_analyses),
            'final_security_score': best_score,
            'final_severity_level': self.security_analyzer.get_severity_level(best_score),
            'vulnerability_summary': {
                'high': all_analyses[-1]['vulnerability_counts']['HIGH'],
                'medium': all_analyses[-1]['vulnerability_counts']['MEDIUM'],
                'low': all_analyses[-1]['vulnerability_counts']['LOW']
            },
            'detected_language': language  
        }
        # for testing only
        #print(f"Security analysis completed for {language}. Final score: {best_score}/10.0, Fix attempts: {fix_attempts}")
        
        return final_result