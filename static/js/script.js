let currentResults = null;

async function enhanceAndAnalyze() {
    const promptInput = document.getElementById('promptInput');
    const enhanceButton = document.getElementById('enhanceButton');
    const enhancedPrompt = document.getElementById('enhancedPrompt');
    const generatedCode = document.getElementById('generatedCode');
    const analysisResults = document.getElementById('analysisResults');
    const viewReportBtn = document.getElementById('viewReport');
    const downloadReportBtn = document.getElementById('downloadReport');
    const languageBadge = document.getElementById('languageBadge');
    const errorMessage = document.getElementById('errorMessage');

    const prompt = promptInput.value.trim();
    
    if (!prompt) {
        showError('Please enter a prompt to generate code.');
        return;
    }

    // Show loading state
    enhanceButton.disabled = true;
    enhanceButton.textContent = 'Processing...';
    
    enhancedPrompt.innerHTML = '<div class="loading">Enhancing prompt...</div>';
    generatedCode.textContent = 'Generating code...';
    analysisResults.innerHTML = '<div class="loading">Analyzing security...<br><small>Automatic fixes enabled for high-severity issues</small></div>';
    languageBadge.style.display = 'none';
    errorMessage.style.display = 'none';

    // Hide previous results and buttons
    viewReportBtn.style.display = 'none';
    downloadReportBtn.style.display = 'none';

    try {
        const response = await fetch('/api/enhance-and-analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                prompt: prompt,
                language: document.getElementById('language-select').value
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Something went wrong');
        }

        // Store results for report generation
        currentResults = data;

        // Update UI with results
        enhancedPrompt.textContent = data.enhanced_prompt;
        generatedCode.textContent = data.generated_code;
        
        // Build the complete analysis HTML
        let analysisHTML = '';
        
        // Add fix attempts info
        if (data.fix_attempts > 0) {
            analysisHTML = `<div class="fix-info">
                <strong> Automatic Security Fixes Applied</strong><br>
                <small>${data.fix_attempts} fix attempt(s) made. Security improved to ${data.final_security_score || '8.5'}/10.0</small>
            </div>`;
        } else if (data.had_high_severity) {
            analysisHTML = `<div class="fix-info no-fixes">
                <strong> High Severity Issues Detected</strong><br>
                <small>Security score: ${data.final_security_score || '8.5'}/10.0. Please review carefully.</small>
            </div>`;
        } else {
            analysisHTML = `<div class="fix-info clean">
                <strong> Security Analysis Complete</strong><br>
                <small>Security score: ${data.final_security_score || '8.5'}/10.0</small>
            </div>`;
        }
        
        // Add dynamic security score section
        analysisHTML += buildDynamicScoreHTML(data);
        
        // Add vulnerability analysis section
        analysisHTML += buildVulnerabilityAnalysisHTML(data);
        
        analysisResults.innerHTML = analysisHTML;

        // Show language badge
        if (data.detected_language) {
            languageBadge.textContent = `[${data.detected_language.toUpperCase()}]`;
            languageBadge.style.display = 'inline';
            languageBadge.className = `language-badge ${data.detected_language}`;
        }

        // Show report buttons
        viewReportBtn.style.display = 'inline-block';
        downloadReportBtn.style.display = 'inline-block';

    } catch (error) {
        console.error('Error:', error);
        showError(`Error: ${error.message}`);
        enhancedPrompt.innerHTML = '';
        generatedCode.textContent = '';
        analysisResults.textContent = '';
        languageBadge.style.display = 'none';
        
        if (error.message.includes('Ollama') || error.message.includes('timeout')) {
            showError('Ollama service is not responding. Please make sure Ollama is running and try again.');
        }
    } finally {
        // Reset button
        enhanceButton.disabled = false;
        enhanceButton.textContent = 'Generate & Analyze Code';
    }
}

function buildDynamicScoreHTML(data) {
    const securityScore = data.final_security_score || 8.5;
    const severityLevel = data.final_severity_level || 'MODERATE';
    const vulnCounts = data.vulnerability_summary || { high: 0, medium: 0, low: 0 };
    
    // Get color based on score
    function getScoreColor(score) {
        if (score >= 9.0) return '#10b981'; // Green
        if (score >= 7.0) return '#3b82f6'; // Blue
        if (score >= 5.0) return '#f59e0b'; // Yellow
        if (score >= 3.0) return '#ef4444'; // Red
        return '#dc2626'; // Dark Red
    }
    
    const scoreColor = getScoreColor(securityScore);
    
    // Get severity level background color
    function getSeverityColor(level) {
        const colors = {
            'EXCELLENT': '#10b981',
            'GOOD': '#3b82f6',
            'MODERATE': '#f59e0b',
            'POOR': '#ef4444',
            'CRITICAL': '#dc2626'
        };
        return colors[level] || '#f59e0b';
    }
    
    const severityColor = getSeverityColor(severityLevel);
    
    return `
        <div class="security-score">
            <div class="score-header">
                <span>Security Score:</span>
                <span class="score-value" style="color: ${scoreColor};">
                    ${securityScore} / 10.0
                </span>
                <span class="severity-level" style="background: ${severityColor}; color: ${severityLevel === 'MODERATE' ? 'black' : 'white'}; padding: 3px 10px; border-radius: 15px; margin-left: 10px; font-size: 0.9em; font-weight: bold;">
                    ${severityLevel}
                </span>
            </div>
            <div class="vulnerability-stats" style="display: flex; gap: 10px; margin-top: 10px; justify-content: center;">
                <span class="vuln-stat high" style="background: rgba(239, 68, 68, 0.2); color: #fca5a5; padding: 5px 10px; border-radius: 5px; font-size: 0.9em; font-weight: bold;">
                     High: ${vulnCounts.high}
                </span>
                <span class="vuln-stat medium" style="background: rgba(245, 158, 11, 0.2); color: #fde68a; padding: 5px 10px; border-radius: 5px; font-size: 0.9em; font-weight: bold;">
                     Medium: ${vulnCounts.medium}
                </span>
                <span class="vuln-stat low" style="background: rgba(34, 197, 94, 0.2); color: #86efac; padding: 5px 10px; border-radius: 5px; font-size: 0.9em; font-weight: bold;">
                     Low: ${vulnCounts.low}
                </span>
            </div>
        </div>
    `;
}

function buildVulnerabilityAnalysisHTML(data) {
    // Check if we have raw analysis text
    if (!data.analysis_results) {
        return `
            <div class="vulnerabilities">
                <h5>Vulnerability Analysis:</h5>
                <div class="no-vulnerabilities" style="padding: 10px; background: rgba(30, 41, 59, 0.8); border-radius: 5px; margin-top: 10px;">
                    <p>No detailed vulnerability analysis available. The AI analysis may not have returned structured data.</p>
                </div>
            </div>
            <div class="summary">
                <h5>Security Summary:</h5>
                <p>Code security analysis completed with a score of ${data.final_security_score || 8.5}/10.0. ${getRecommendationText(data.final_security_score)}</p>
            </div>
        `;
    }
    
    // Try to parse and format the raw analysis text
    const analysisText = data.analysis_results;
    const lines = analysisText.split('\n').filter(line => line.trim());
    
    let vulnerabilitiesHTML = '';
    let summaryHTML = '';
    
    // Simple parsing of the analysis text
    let inVulnerabilitySection = false;
    let inSummarySection = false;
    let vulnerabilityItems = [];
    let summaryLines = [];
    
    for (const line of lines) {
        const lowerLine = line.toLowerCase();
        
        if (lowerLine.includes('vulnerability') || lowerLine.includes('issue') || lowerLine.includes('problem')) {
            inVulnerabilitySection = true;
            inSummarySection = false;
        } else if (lowerLine.includes('summary') || lowerLine.includes('conclusion') || lowerLine.includes('recommendation')) {
            inVulnerabilitySection = false;
            inSummarySection = true;
        }
        
        if (inVulnerabilitySection && line.trim() && !line.toLowerCase().includes('vulnerability')) {
            // Try to determine severity from the line
            let severity = 'medium';
            if (line.toLowerCase().includes('[high]') || line.toLowerCase().includes('high severity')) {
                severity = 'high';
            } else if (line.toLowerCase().includes('[low]') || line.toLowerCase().includes('low severity')) {
                severity = 'low';
            }
            
            vulnerabilityItems.push({ line: line.trim(), severity: severity });
        }
        
        if (inSummarySection && line.trim() && !line.toLowerCase().includes('summary')) {
            summaryLines.push(line.trim());
        }
    }
    
    // Build vulnerabilities HTML
    if (vulnerabilityItems.length > 0) {
        vulnerabilitiesHTML = '<div class="vulnerabilities"><h5>Identified Issues:</h5>';
        vulnerabilityItems.forEach(item => {
            vulnerabilitiesHTML += `
                <div class="vulnerability-item ${item.severity}">
                    <span class="severity ${item.severity}">${item.severity.toUpperCase()}</span>
                    ${item.line}
                </div>
            `;
        });
        vulnerabilitiesHTML += '</div>';
    } else {
        vulnerabilitiesHTML = `
            <div class="vulnerabilities">
                <h5>Vulnerability Analysis:</h5>
                <pre style="background: rgba(15, 23, 42, 0.9); padding: 15px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; color: #e2e8f0; border: 1px solid rgba(79, 70, 229, 0.2); margin-top: 10px;">
${analysisText.substring(0, 1000)}${analysisText.length > 1000 ? '...' : ''}
                </pre>
            </div>
        `;
    }
    
    // Build summary HTML
    if (summaryLines.length > 0) {
        summaryHTML = `<div class="summary"><h5>Security Summary:</h5><p>${summaryLines.join(' ')}</p></div>`;
    } else {
        summaryHTML = `
            <div class="summary">
                <h5>Security Summary:</h5>
                <p>Code security analysis completed with a score of ${data.final_security_score || 8.5}/10.0. ${getRecommendationText(data.final_security_score)}</p>
            </div>
        `;
    }
    
    return vulnerabilitiesHTML + summaryHTML;
}

function getRecommendationText(score) {
    if (score >= 9.0) {
        return 'Excellent security posture. The code demonstrates strong security practices and is production-ready.';
    } else if (score >= 7.0) {
        return 'Good security posture. Minor improvements are recommended before production deployment.';
    } else if (score >= 5.0) {
        return 'Moderate security posture. Several security issues were identified and should be addressed.';
    } else if (score >= 3.0) {
        return 'Poor security posture. Significant security issues require immediate attention.';
    } else {
        return 'Critical security posture. The code contains severe vulnerabilities and should not be deployed.';
    }
}

async function generateReport() {
    if (!currentResults) {
        showError('No results available to generate report. Please generate code first.');
        return;
    }

    try {
        const response = await fetch('/api/generate-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentResults)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate report');
        }

        alert(`📋 Report generated successfully! Report ID: ${data.report_id}`);
        
        // Redirect to reports page
        window.location.href = '/reports';

    } catch (error) {
        console.error('Error generating report:', error);
        showError(`Failed to generate report: ${error.message}`);
    }
}

function viewReportInBrowser() {
    generateReport();
}

function downloadReport() {
    generateReport();
}

function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

// Event listeners for reports page (if we're on that page)
document.addEventListener('DOMContentLoaded', function() {
    // Only add these event listeners if we're on the reports page
    if (window.location.pathname.includes('/reports')) {
        // View Report buttons
        document.querySelectorAll('.view-report-btn').forEach(button => {
            button.addEventListener('click', function() {
                const reportId = this.getAttribute('data-report-id');
                viewReport(reportId);
            });
        });
        
        // Download Report buttons
        document.querySelectorAll('.download-report-btn').forEach(button => {
            button.addEventListener('click', function() {
                const reportId = this.getAttribute('data-report-id');
                downloadReport(reportId);
            });
        });

        // Delete Report buttons
        document.querySelectorAll('.delete-report-btn').forEach(button => {
            button.addEventListener('click', function() {
                const reportId = this.getAttribute('data-report-id');
                deleteReport(reportId);
            });
        });

        // Filter controls
        const languageFilter = document.getElementById('languageFilter');
        const severityFilter = document.getElementById('severityFilter');
        
        if (languageFilter) {
            languageFilter.addEventListener('change', filterReports);
        }
        if (severityFilter) {
            severityFilter.addEventListener('change', filterReports);
        }

        // Search input
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', searchReports);
        }
    }
});

// Reports page functions
function viewReport(reportId) {
    window.open(`/api/view-report?report_id=${reportId}`, '_blank');
}

function downloadReport(reportId) {
    window.location.href = `/api/download-report?report_id=${reportId}`;
}

function searchReports() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const reportCards = document.querySelectorAll('.report-card');
    
    reportCards.forEach(card => {
        const promptText = card.querySelector('.report-prompt').textContent.toLowerCase();
        if (promptText.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function filterReports() {
    const languageFilter = document.getElementById('languageFilter').value;
    const severityFilter = document.getElementById('severityFilter').value;
    const reportCards = document.querySelectorAll('.report-card');
    
    reportCards.forEach(card => {
        const language = card.getAttribute('data-language');
        const severity = card.getAttribute('data-severity');
        
        const languageMatch = !languageFilter || language === languageFilter;
        const severityMatch = !severityFilter || severity === severityFilter;
        
        if (languageMatch && severityMatch) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

function deleteReport(reportId) {
    if (confirm('Are you sure you want to delete this report?')) {
        fetch(`/api/delete-report?report_id=${reportId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Report deleted successfully');
                location.reload();
            } else {
                alert('Error deleting report: ' + data.error);
            }
        })
        .catch(error => {
            alert('Error deleting report: ' + error);
        });
    }
}

// Format security score with color
function formatScore(score) {
    if (score >= 9.0) return `<span style="color: #10b981">${score}/10.0</span>`;
    if (score >= 7.0) return `<span style="color: #3b82f6">${score}/10.0</span>`;
    if (score >= 5.0) return `<span style="color: #f59e0b">${score}/10.0</span>`;
    if (score >= 3.0) return `<span style="color: #ef4444">${score}/10.0</span>`;
    return `<span style="color: #dc2626">${score}/10.0</span>`;
}

// Helper function to update score display dynamically
function updateSecurityScoreDisplay(score, severity) {
    const scoreElements = document.querySelectorAll('.score-value');
    scoreElements.forEach(element => {
        element.innerHTML = formatScore(score);
        element.className = `score-value ${severity.toLowerCase()}`;
    });
}