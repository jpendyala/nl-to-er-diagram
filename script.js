document.addEventListener('DOMContentLoaded', () => {
    const promptInput = document.getElementById('prompt-input');
    const generateBtn = document.getElementById('generate-btn');
    const errorDiv = document.getElementById('error');
    const resultContainer = document.getElementById('result-container');
    const mermaidDiagramDiv = document.getElementById('mermaid-diagram');
    const mermaidCodePre = document.getElementById('mermaid-code').querySelector('code');
    const loadingDiv = document.getElementById('loading');

    // --- Configuration ---
    // Change this if your backend runs on a different URL/port
    const apiUrl = 'http://127.0.0.1:8000/generate-er-diagram';
    // ---------------------

    generateBtn.addEventListener('click', async () => {
        const prompt = promptInput.value.trim();

        // Clear previous results and errors
        errorDiv.textContent = '';
        resultContainer.style.display = 'none';
        mermaidDiagramDiv.innerHTML = ''; // Clear previous diagram
        mermaidCodePre.textContent = '';
        loadingDiv.style.display = 'block'; // Show loading indicator
        generateBtn.disabled = true; // Disable button during request

        if (!prompt) {
            errorDiv.textContent = 'Please enter a database description.';
            loadingDiv.style.display = 'none';
            generateBtn.disabled = false;
            return;
        }

        try {
            console.log(`Sending prompt to ${apiUrl}: ${prompt.substring(0, 100)}...`);

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json', // Explicitly accept JSON
                },
                body: JSON.stringify({ prompt: prompt })
            });

            console.log(`Received response status: ${response.status}`);

            if (!response.ok) {
                let errorMsg = `Error: ${response.status} ${response.statusText}`;
                try {
                    // Try to parse error details from backend response body
                    const errorData = await response.json();
                    if (errorData.detail) {
                       errorMsg += ` - ${errorData.detail}`;
                    }
                } catch (e) {
                    // Could not parse JSON body or no 'detail' field
                    errorMsg += ` (Could not parse error details from response)`;
                }
                 throw new Error(errorMsg);
            }

            const data = await response.json();
            console.log("Received data:", data);

            if (data.mermaid_code) {
                // Display raw code
                mermaidCodePre.textContent = data.mermaid_code;

                try {
                    // Update the div with the Mermaid code for rendering
                    mermaidDiagramDiv.textContent = data.mermaid_code; // Add the raw code first
                    mermaidDiagramDiv.removeAttribute('data-processed'); // Important for re-rendering

                    // Reinitialize Mermaid.js to render the new diagram
                    mermaid.contentLoaded();
                    console.log("Mermaid rendering complete.");
                    resultContainer.style.display = 'block'; // Show results
                } catch (renderError) {
                    console.error("Mermaid rendering failed:", renderError);
                    errorDiv.textContent = `Failed to render the diagram: ${renderError.message || renderError}. Check console for details. Raw code is displayed below.`;
                    resultContainer.style.display = 'block'; // Still show raw code
                    mermaidDiagramDiv.innerHTML = '<p style="color:red;">Rendering failed.</p>'; // Clear diagram area
                }

                // Optional: Display any explanation from the backend
                if(data.explanation) {
                    const explanationP = document.createElement('p');
                    explanationP.style.fontStyle = 'italic';
                    explanationP.style.marginTop = '10px';
                    explanationP.textContent = `Note: ${data.explanation}`;
                    resultContainer.appendChild(explanationP); // Add it after the code/diagram
                }

            } else {
                 throw new Error('Received response does not contain mermaid_code.');
            }

        } catch (error) {
            console.error('Fetch or processing error:', error);
            errorDiv.textContent = `An error occurred: ${error.message}`;
        } finally {
             loadingDiv.style.display = 'none'; // Hide loading indicator
             generateBtn.disabled = false; // Re-enable button
        }
    });
});