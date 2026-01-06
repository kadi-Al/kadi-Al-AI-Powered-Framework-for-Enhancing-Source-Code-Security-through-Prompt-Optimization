class PromptEnhancer:
    def __init__(self, ollama_client):
        self.ollama_client = ollama_client
    
    def enhance_prompt(self, user_prompt, language=None):
        if language:
            system_prompt = f"""you are a security professional and code expert. Enhance this prompt for {language.upper()} code to be more secure while keeping the core function.

Enhance the prompt by:
        - keeping the core function
        - Adding specific security requirements for {language.upper()}
        - Specifying secure coding standards for {language.upper()}
        - Adding threat modeling elements
        - Including compliance considerations if relevant
        - Adding this prefix: "You are a developer who is very security-aware and avoids weaknesses in {language.upper()} code."
        - Ensure the enhanced prompt explicitly mentions {language.upper()}
        """
        else:
            system_prompt = """you are a security professional and code expert enhance this prompt to be more secure and keep the core function

Enhance the prompt by:
        - keeping the core function
        - Adding specific security requirements
        - Specifying secure coding standards
        - Adding threat modeling elements
        - Including compliance considerations if relevant
        - add this prefix "You are a developer who is very security-aware and avoids weaknesses in the code."
        """
        
        if language:
            enhancement_prompt = f"""Enhance the following prompt for {language.upper()} code generation:

Original user prompt: {user_prompt}

Make sure the enhanced prompt:
1. Explicitly specifies {language.upper()} as the target language
2. Includes security considerations specific to {language.upper()}
3. Maintains the original functionality
4. Emphasizes secure coding practices for {language.upper()}

Enhanced prompt:"""
        else:
            enhancement_prompt = f"""Original user prompt: {user_prompt}

Please enhance this prompt to include security considerations and best practices for secure code generation. Make sure the enhanced prompt is clear, specific, and emphasizes security aspects.

Enhanced prompt:"""
        
        try:
            enhanced_response = self.ollama_client.generate_response(
                model="deepseek-v2:16b",
                prompt=enhancement_prompt,
                system_prompt=system_prompt
            )
            return enhanced_response.strip()
        except Exception as e:
            print(f"Error enhancing prompt: {e}")
            if language:
                return f"Generate secure {language.upper()} code for: {user_prompt}. Ensure the code follows {language.upper()} security best practices including input validation, proper error handling, and protection against common vulnerabilities."
            else:
                return f"{user_prompt} - Ensure the code follows security best practices including input validation, proper error handling, and protection against common vulnerabilities."