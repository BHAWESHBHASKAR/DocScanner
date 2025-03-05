// Main JavaScript file for Document Scanner application

// Theme Toggle Functionality
const toggleTheme = () => {
    const body = document.body;
    body.classList.toggle('dark');
    const theme = body.classList.contains('dark') ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
};

// Load theme from localStorage
const loadTheme = () => {
    const theme = localStorage.getItem('theme') || 'light';
    document.body.classList.toggle('dark', theme === 'dark');
};

// Initialize theme on page load
loadTheme();

// Add event listener for theme toggle button
const themeToggleButton = document.getElementById('theme-toggle');
if (themeToggleButton) {
    themeToggleButton.addEventListener('click', toggleTheme);
}

// Drag and Drop File Upload Functionality
const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const fileNameDisplay = document.getElementById('file-name');

if (dropArea) {
    dropArea.addEventListener('dragover', (event) => {
        event.preventDefault();
        dropArea.classList.add('active');
    });

    dropArea.addEventListener('dragleave', () => {
        dropArea.classList.remove('active');
    });

    dropArea.addEventListener('drop', (event) => {
        event.preventDefault();
        dropArea.classList.remove('active');
        const files = event.dataTransfer.files;
        handleFiles(files);
    });

    dropArea.addEventListener('click', () => {
        fileInput.click();
    });
}

fileInput.addEventListener('change', (event) => {
    const files = event.target.files;
    handleFiles(files);
});

function handleFiles(files) {
    const supportedTypes = ['text/plain', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const fileNames = [];

    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (supportedTypes.includes(file.type)) {
            fileNames.push(file.name);
        } else {
            alert('Error: Unsupported file type. Please select a PDF, DOC, DOCX, or TXT file.');
            fileInput.value = ''; // Clear the file input
            return;
        }
    }

    fileNameDisplay.textContent = fileNames.join(', ');
    fileNameDisplay.style.display = 'block';
}

document.addEventListener('DOMContentLoaded', function() {
    // Flash message close button functionality
    const closeButtons = document.querySelectorAll('.flash-message .close-btn');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const flashMessage = this.parentElement;
            flashMessage.classList.add('fade-out');
            setTimeout(() => {
                flashMessage.style.display = 'none';
            }, 500);
        });
    });

    // Auto-hide flash messages after 5 seconds
    setTimeout(() => {
        document.querySelectorAll('.flash-message').forEach(message => {
            message.classList.add('fade-out');
            setTimeout(() => {
                message.style.display = 'none';
            }, 500);
        });
    }, 5000);

    // Profile tabs functionality
    const tabButtons = document.querySelectorAll('.tab-btn');
    if (tabButtons.length > 0) {
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tabName = this.getAttribute('data-tab');
                // Remove active class from all buttons and contents
                document.querySelectorAll('.tab-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                // Add active class to current button and content
                this.classList.add('active');
                document.getElementById(`${tabName}-tab`).classList.add('active');
            });
        });
    }

    // Admin dashboard charts
    setupCharts();
});

// Function to setup charts on admin dashboard
function setupCharts() {
    const scanActivityChart = document.getElementById('scan-activity-chart');
    if (scanActivityChart) {
        const scanActivityData = JSON.parse(scanActivityChart.getAttribute('data-chart'));
        renderChart(scanActivityChart, scanActivityData, 'Scan Activity (Last 7 Days)');
    }

    const userRegistrationChart = document.getElementById('user-registration-chart');
    if (userRegistrationChart) {
        const userRegistrationData = JSON.parse(userRegistrationChart.getAttribute('data-chart'));
        renderChart(userRegistrationChart, userRegistrationData, 'User Registrations (Last 30 Days)');
    }

    const creditUsageChart = document.getElementById('credit-usage-chart');
    if (creditUsageChart) {
        const creditUsageData = JSON.parse(creditUsageChart.getAttribute('data-chart'));
        renderChart(creditUsageChart, creditUsageData, 'Credit Usage (Last 30 Days)');
    }
}

// Simple chart rendering function using canvas
function renderChart(canvas, data, title) {
    if (!canvas || !canvas.getContext) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw title
    ctx.font = '16px Arial';
    ctx.fillStyle = '#343a40';
    ctx.textAlign = 'center';
    ctx.fillText(title, width / 2, 20);
    
    // Find max value for scaling
    const maxValue = Math.max(...data.map(item => item.count)) || 1;
    
    // Draw bars
    const barWidth = (width - 40) / data.length;
    const barMaxHeight = height - 60;
    
    data.forEach((item, index) => {
        const barHeight = (item.count / maxValue) * barMaxHeight;
        const x = 20 + (index * barWidth);
        const y = height - 30 - barHeight;
        
        // Draw bar
        ctx.fillStyle = '#4a6fa5';
        ctx.fillRect(x, y, barWidth - 5, barHeight);
        
        // Draw date label
        ctx.font = '10px Arial';
        ctx.fillStyle = '#6c757d';
        ctx.textAlign = 'center';
        ctx.fillText(item.date.slice(-5), x + (barWidth - 5) / 2, height - 10);
        
        // Draw value
        ctx.font = '12px Arial';
        ctx.fillStyle = '#343a40';
        ctx.textAlign = 'center';
        ctx.fillText(item.count, x + (barWidth - 5) / 2, y - 5);
    });
}

// Document similarity visualization
function visualizeSimilarity(elementId, similarityScore) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const canvas = document.createElement('canvas');
    canvas.width = 200;
    canvas.height = 20;
    element.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    
    // Draw background
    ctx.fillStyle = '#e9ecef';
    ctx.fillRect(0, 0, 200, 20);
    
    // Draw similarity bar
    let color = '#dc3545'; // red for low similarity
    if (similarityScore >= 0.7) {
        color = '#28a745'; // green for high similarity
    } else if (similarityScore >= 0.5) {
        color = '#ffc107'; // yellow for medium similarity
    }
    
    ctx.fillStyle = color;
    ctx.fillRect(0, 0, 200 * similarityScore, 20);
    
    // Add percentage text
    const percentText = document.createElement('span');
    percentText.textContent = `${Math.round(similarityScore * 100)}%`;
    percentText.style.marginLeft = '10px';
    percentText.style.fontWeight = 'bold';
    percentText.style.color = color;
    element.appendChild(percentText);
}
