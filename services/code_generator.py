from utils.ollama_client import OllamaClient
from utils.code_utils import CodeUtils

class CodeGenerator:
    def __init__(self, ollama_client):
        self.ollama_client = ollama_client
        self.code_utils = CodeUtils()
    
    def generate_code(self, enhanced_prompt, security_context=None, language=None):
        # If language is provided, use it; otherwise detect from prompt
        if language:
            target_language = language.lower()
        else:
            # Try to detect language from enhanced_prompt
            target_language = self.code_utils.detect_language(enhanced_prompt)
        
        # Generate system prompt based on whether we're fixing code or generating new code
        if security_context:
            system_prompt = f"""You are a security-focused code expert specializing in {target_language.upper()}. 
            Rewrite the provided code to fix ALL security vulnerabilities while maintaining the original functionality.

            SECURITY ISSUES TO ADDRESS:
            {security_context}

            REQUIREMENTS:
            - Fix all security vulnerabilities mentioned above
            - Maintain the original code's functionality
            - Keep the code in {target_language.upper()}
            - Include proper input validation for {target_language.upper()}
            - Add error handling without information leakage
            - Use secure coding practices specific to {target_language.upper()}
            - Return ONLY the fixed code without any explanations
            - Use proper {target_language.upper()} code formatting
            - Include necessary imports and dependencies
            - Generate complete, compilable code
            """
            
            code_prompt = f"""Rewrite the following {target_language.upper()} code to fix security vulnerabilities:

            SECURITY ISSUES TO ADDRESS:
            {security_context}

            REQUIREMENTS:
            - Fix all security vulnerabilities mentioned above
            - Maintain the original code's functionality and keep it as {target_language.upper()} code
            - Include proper input validation
            - Add error handling without information leakage
            - Use secure coding practices
            - Return ONLY the fixed code without any explanations
            - Generate the whole updated code in {target_language.upper()}

            Original code to fix:
            ```{target_language}
            {enhanced_prompt}
            ```
            """
        else:
            # Initial code generation
            system_prompt = f"""You are a security professional and code expert. 
            Generate secure, efficient, and well-documented code in {target_language.upper()} based on the user's request. 
            Include proper error handling and security measures specific to {target_language.upper()}. 
            
            IMPORTANT: The code MUST be in {target_language.upper()}. Do not change the programming language.
            
            Return only the code without additional explanations. Use code blocks with {target_language} specification.
            """
            
            # Add language hint to the prompt
            code_prompt = f"""Generate {target_language.upper()} code for: {enhanced_prompt}
            
            Requirements:
            - Code must be in {target_language.upper()}
            - Include proper error handling
            - Use secure coding practices
            - Add comments for important sections
            - Make sure it's compilable/runnable
            """
        
        if len(code_prompt) > 5000:
            code_prompt = code_prompt[:5000] + "..."
        
        print(f"Generating code in {target_language.upper()}...")
        response = self.ollama_client.generate_response("deepseek-coder-v2:latest", code_prompt, system_prompt)
        
        # Extract code from response
        extracted_code = self.code_utils.extract_code(response)
        
        # Add language-specific headers if missing
        extracted_code = self._ensure_language_header(extracted_code, target_language)
        
        return extracted_code
    
    def _ensure_language_header(self, code, language):
        """Add language-specific headers if missing to ensure code stays in the right language"""
        if not code or not language:
            return code
        
        code_lower = code.lower()
        language = language.lower()
        
        # For C code, ensure #include is present
        if language == 'c' and '#include' not in code_lower:
            header = "// C code - Generated with security enhancements\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n\n"
            return header + code
        
        # For Java code, ensure class definition is present
        elif language == 'java' and 'public class' not in code_lower:
            # Try to extract a class name from the first line or use default
            lines = code.strip().split('\n')
            class_name = "SecureCode"
            for line in lines[:5]:
                if 'class' in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.lower() == 'class' and i + 1 < len(parts):
                            class_name = parts[i + 1].split('{')[0].strip()
                            break
            header = f"// Java code - Generated with security enhancements\npublic class {class_name} {{\n    "
            # Indent all existing code
            indented_code = code.replace('\n', '\n    ')
            return header + indented_code + "\n}"
        
        # For Python code, ensure it starts with a comment
        elif language == 'python' and not code_lower.startswith('#') and not code_lower.startswith('"""'):
            header = "# Python code - Generated with security enhancements\n\n"
            return header + code
        
        return code