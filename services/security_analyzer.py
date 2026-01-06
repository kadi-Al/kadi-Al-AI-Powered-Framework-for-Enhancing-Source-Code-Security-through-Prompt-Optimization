from utils.ollama_client import OllamaClient
from utils.code_utils import CodeUtils

class SecurityAnalyzer:
    def __init__(self, ollama_client):
        self.ollama_client = ollama_client
        self.code_utils = CodeUtils()
    
    def analyze_code_security(self, code, language):
        # Determine the language (use provided language or detect)
        if language:
            target_language = language.lower()
        else:
            target_language = self.code_utils.detect_language(code)
        
        system_prompt = f"""You are a cybersecurity expert specializing in {target_language.upper()} code security analysis. 
        Analyze the provided {target_language.upper()} code for security vulnerabilities and provide:
        
        1. Security vulnerabilities found (with severity: High/Medium/Low)
        2. Specific fixes for each vulnerability
        3. Optimization suggestions for {target_language.upper()}
        4. Best practices recommendations for {target_language.upper()}
        5. A brief explanation of the features in the code
        6. What security threats you tried to prevent and how
        
        IMPORTANT: The code is in {target_language.upper()}. Analyze it as {target_language.upper()} code.
        
        Be very clear about severity levels. Use labels like [HIGH], [MEDIUM], [LOW] for each vulnerability.
        
        IMPORTANT: At the end of your analysis, include a summary section with this exact format:
        VULNERABILITY_SUMMARY:
        - HIGH: [count]
        - MEDIUM: [count]
        - LOW: [count]
        
        SECURITY_SCORE: [score between 0.0 and 10.0]
        """
        
        if len(code) > 7000:
            analysis_code = code[:2500] + f"\n// ... (code truncated, analyzing first {len(code[:2500])} characters)\n" + code[-2500:]
        else:
            analysis_code = code
        
        analysis_prompt = f"""
        Perform comprehensive security analysis on this {target_language.upper()} code:

        ```{target_language}
        {analysis_code}
        ```

        Focus on:
        1. Language-specific vulnerabilities for {target_language.upper()}
        2. Input validation issues
        3. Memory safety concerns (if applicable to {target_language.upper()})
        4. Authentication and authorization flaws
        5. Error handling and information leakage
        6. Code injection possibilities
        7. Cryptographic weaknesses
        8. Configuration and deployment issues

        Provide specific, actionable recommendations for fixing issues in {target_language.upper()}.
        """
        
        print(f"Analyzing {target_language.upper()} code security...")
        ai_response = self.ollama_client.generate_response("deepseek-v2:16b", analysis_prompt, system_prompt)
        
        # Extract vulnerability counts from AI response
        vulnerability_counts = self._extract_vulnerability_counts(ai_response)
        
        # Extract security score from AI response
        security_score = self._extract_security_score(ai_response, vulnerability_counts)
        
        return {
            'raw_analysis': ai_response,
            'vulnerability_counts': vulnerability_counts,
            'security_score': security_score,
            'vulnerabilities_detected': sum(vulnerability_counts.values()) > 0,
            'language_analyzed': target_language
        }
    
    def _extract_vulnerability_counts(self, analysis_text):
        """Extract vulnerability counts from AI analysis text"""
        if not analysis_text:
            return {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        
        analysis_lower = analysis_text.lower()
        
        # Try to extract from VULNERABILITY_SUMMARY section
        import re
        
        # Look for summary section
        summary_pattern = r'vulnerability_summary:.*?- high:\s*(\d+).*?- medium:\s*(\d+).*?- low:\s*(\d+)'
        summary_match = re.search(summary_pattern, analysis_lower, re.DOTALL | re.IGNORECASE)
        
        if summary_match:
            return {
                'HIGH': int(summary_match.group(1)),
                'MEDIUM': int(summary_match.group(2)),
                'LOW': int(summary_match.group(3))
            }
        
        # Look for alternative summary format
        alt_pattern = r'high:\s*(\d+).*?medium:\s*(\d+).*?low:\s*(\d+)'
        alt_match = re.search(alt_pattern, analysis_lower, re.DOTALL | re.IGNORECASE)
        
        if alt_match:
            return {
                'HIGH': int(alt_match.group(1)),
                'MEDIUM': int(alt_match.group(2)),
                'LOW': int(alt_match.group(3))
            }
        
        # Fallback: Count occurrences of severity markers
        high_patterns = [
            r'\[high\]', r'high severity', r'severity:\s*high', 
            r'critical vulnerability', r'critical severity', r'high risk'
        ]
        
        medium_patterns = [
            r'\[medium\]', r'medium severity', r'severity:\s*medium',
            r'moderate severity', r'moderate risk', r'medium risk'
        ]
        
        low_patterns = [
            r'\[low\]', r'low severity', r'severity:\s*low',
            r'minor severity', r'low risk', r'informational'
        ]
        
        high_count = 0
        for pattern in high_patterns:
            high_count += len(re.findall(pattern, analysis_lower, re.IGNORECASE))
        
        medium_count = 0
        for pattern in medium_patterns:
            medium_count += len(re.findall(pattern, analysis_lower, re.IGNORECASE))
        
        low_count = 0
        for pattern in low_patterns:
            low_count += len(re.findall(pattern, analysis_lower, re.IGNORECASE))
        
        # Also count bullet points with severity
        high_count += len(re.findall(r'-.*?high.*?(vulnerability|issue|problem|risk)', analysis_lower, re.IGNORECASE))
        medium_count += len(re.findall(r'-.*?medium.*?(vulnerability|issue|problem|risk)', analysis_lower, re.IGNORECASE))
        low_count += len(re.findall(r'-.*?low.*?(vulnerability|issue|problem|risk)', analysis_lower, re.IGNORECASE))
        
        return {
            'HIGH': min(high_count, 10),  # Cap at reasonable number
            'MEDIUM': min(medium_count, 15),
            'LOW': min(low_count, 20)
        }
    
    def _extract_security_score(self, analysis_text, vulnerability_counts):
        """Extract security score from AI response or calculate based on vulnerabilities"""
        if not analysis_text:
            return self._calculate_security_score(vulnerability_counts)
        
        # Try to extract score from analysis text
        import re
        
        score_pattern = r'security_score:\s*(\d+\.?\d*)'
        score_match = re.search(score_pattern, analysis_text, re.IGNORECASE)
        
        if score_match:
            try:
                score = float(score_match.group(1))
                # Ensure score is between 0 and 10
                return max(0.0, min(10.0, score))
            except:
                pass
        
        # Calculate score based on vulnerabilities
        return self._calculate_security_score(vulnerability_counts)
    
 
 