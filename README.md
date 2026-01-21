# AI-Powered Framework for Enhancing Open-Source Software Security through Prompt Optimization and Vulnerability Detection
is an open-source, proactive security framework that enhances source code safety in AI-generated code by integrating intelligent prompt engineering with automated vulnerability analysis. Unlike reactive security tools that scan code after generation, guides Large Language Models (LLMs) to produce secure code from the outset while preserving developer productivity.

Built with a modular Flask architecture and leveraging local AI processing via Ollama,  ensures complete data privacy by keeping all code and analysis within the user's environment—no data leaves your machine.
___ 

## Why This frameWork 
___
The increasing reliance on Large Language Models (LLMs) like GitHub Copilot for code generation introduces significant security risks, as these models often produce vulnerable code that threatens software integrity. Current reactive solutions only scan code after generation, leaving a critical security gap in the development lifecycle. While some approaches fine-tune models for security or use static analysis tools, they often lack real-time integration or compromise usability.

To address this, we developed a proactive AI-powered security framework that integrates prompt engineering with automated vulnerability analysis. By guiding LLMs toward secure code from the outset and implementing a closed-loop feedback system, our solution reduces vulnerabilities without sacrificing productivity.
## How It Works
___
operates through a closed-loop security pipeline:

1. Prompt Enhancement: Users submit natural language requests → F12's AI model enhances prompts with security context and constraints

2. Secure Code Generation: The enhanced prompt is processed by a separate LLM (DeepSeek V2) to generate initial code

3. Automated Analysis: Generated code is immediately scanned for vulnerabilities using integrated security tools

4. Iterative Refinement: If vulnerabilities are detected, the system regenerates code (up to 3 iterations) to fix issues

5. Security Scoring: Code receives a weighted security score (0-10) with detailed reports

The entire process is automated and requires minimal developer intervention.
___ 
![How It Works](https://github.com/user-attachments/assets/98817610-4b63-4349-9341-cab7aff3463c)


## Quick Start
___

### Prerequisites Installation:
1.	Install Python 3.8+ from python.org
2.	Install Ollama from ollama.ai
3.	Verify installation through command line validation

### Application Setup:

#### Method 1: Automated setup (recommended)
1. **Run setup :**
python setup.py
2. **Start the application:**
python app.py
3. **Open your browser:**
http://localhost:5000

#### Method 2: Manual setup
1. pip install -r requirements.txt
2. ollama pull deepseek-v2:16b
3. ollama pull deepseek-coder-v2:latest**
4. Start the application:
5. python app.py
3. Open your browser: http://localhost:5000

## Known Limitations
1. **Language Support:** Currently optimized for Python, Java, and C
2. **Model Consistency:** Occasional variability in AI responses
3. **Complex Code Bases:** Best suited for modular functions rather than entire systems

## preview
![preview](https://github.com/user-attachments/assets/63c3dc63-8ed8-4dfd-ab91-1e5ec73748de)


