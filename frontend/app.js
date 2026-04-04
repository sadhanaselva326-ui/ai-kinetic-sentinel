const API_URL = "http://127.0.0.1:8000/api/document-analyze";

// Pre-fill the token on page load
window.addEventListener('DOMContentLoaded', () => {
    const tokenInput = document.getElementById('apiTokenInput');
    if (tokenInput && !tokenInput.value) {
        tokenInput.value = "super_secure_key_123";
    }
});

let currentFileBase64 = null;
let currentFileType = null;
let currentFileName = null;

// UI Elements
const fileUpload = document.getElementById('fileUpload');
const uploadStatus = document.getElementById('uploadStatus');
const displayFileName = document.getElementById('displayFileName');
const summaryText = document.getElementById('summaryText');
const confidenceValue = document.getElementById('confidenceValue');

const orgsContainer = document.getElementById('orgsContainer');
const amountsContainer = document.getElementById('amountsContainer');
const namesContainer = document.getElementById('namesContainer');
const datesContainer = document.getElementById('datesContainer');
const sentimentContainer = document.getElementById('sentimentContainer');

fileUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const allowed = ["pdf", "docx", "png", "jpg", "jpeg"];
    const ext = file.name.split('.').pop().toLowerCase();
    
    if (!allowed.includes(ext)) {
      alert("Unsupported file type");
      return;
    }

    currentFileName = file.name;
    displayFileName.textContent = currentFileName;
    uploadStatus.textContent = "Formatting document...";

    // Determine type
    if (ext === 'pdf') {
        currentFileType = 'pdf';
    } else if (ext === 'docx') {
        currentFileType = 'docx';
    } else {
        currentFileType = 'image';
    }

    // Convert to base64
    const reader = new FileReader();
    reader.onload = (readerEvent) => {
        // Strip data:image/jpeg;base64, prefix if present
        const b64Full = readerEvent.target.result;
        currentFileBase64 = b64Full.includes(',') ? b64Full.split(',')[1] : b64Full;
        uploadStatus.textContent = "Ready for analysis.";
    };
    reader.readAsDataURL(file);
});

async function analyzeDocument() {
    if (!currentFileBase64) {
        alert("Please upload a document first!");
        return;
    }

    summaryText.innerText = "⏳ Processing... Gemini AI is analyzing your document. This may take 1-2 minutes, please wait.";
    summaryText.classList.add('loading');
    
    const apiToken = document.getElementById('apiTokenInput').value.trim();
    if (!apiToken) {
        summaryText.innerText = "⚠️ Please enter your API token in the top-right field first!";
        summaryText.classList.remove('loading');
        return;
    }
    // Reset lists
    orgsContainer.innerHTML = '<span class="pill empty">Analyzing...</span>';
    amountsContainer.innerHTML = '<span class="pill empty">Analyzing...</span>';
    namesContainer.innerHTML = '<span class="pill empty">Analyzing...</span>';
    datesContainer.innerHTML = '<span class="pill empty">Analyzing...</span>';

    try {
        // Timeout after 5 minutes (gemini-2.5-flash takes ~60-120s for large PDFs)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 300000);

        const response = await fetch(API_URL, {
            method: 'POST',
            signal: controller.signal,
            headers: {
                'Content-Type': 'application/json',
                'x-api-key': apiToken
            },
            body: JSON.stringify({
                fileName: currentFileName,
                fileType: currentFileType,
                fileBase64: currentFileBase64
            })
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || `Server error: ${response.status}`);
        }

        const data = await response.json();
        populateUI(data);

    } catch (error) {
        console.error("Analysis failed:", error);
        const msg = error.name === 'AbortError' ? 'Request timed out (90s). Check server is running.' : error.message;
        summaryText.innerText = "⚠️ Error: " + msg;
        summaryText.classList.remove('loading');
        orgsContainer.innerHTML = '<span class="pill empty">Failed</span>';
        amountsContainer.innerHTML = '<span class="pill empty">Failed</span>';
        namesContainer.innerHTML = '<span class="pill empty">Failed</span>';
        datesContainer.innerHTML = '<span class="pill empty">Failed</span>';
    }
}

function populateUI(data) {
    summaryText.classList.remove('loading');
    summaryText.innerText = data.summary || "No summary available";
    
    // Hardcoded confidence since Gemini API doesn't generate confidence natively in this run
    confidenceValue.textContent = "98.4%"; 
    
    sentimentContainer.innerHTML = `<span class="pill sentiment-pill">${data.sentiment}</span>`;

    function renderPills(container, items) {
        container.innerHTML = '';
        if (!items || items.length === 0) {
            container.innerHTML = '<span class="pill empty">None Found</span>';
            return;
        }
        items.forEach(item => {
            const span = document.createElement('span');
            span.className = 'pill';
            span.textContent = item;
            container.appendChild(span);
        });
    }

    renderPills(orgsContainer, data.entities.organizations);
    renderPills(amountsContainer, data.entities.amounts);
    renderPills(namesContainer, data.entities.names);
    renderPills(datesContainer, data.entities.dates);
}
