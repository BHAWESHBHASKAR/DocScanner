/**
 * Document Upload Form Handler
 * Ensures proper form submission and provides visual feedback
 */

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const scanButton = document.getElementById('scan-button');
    const fileInput = document.getElementById('file-input');
    
    if (uploadForm && scanButton && fileInput) {
        // Add click handler for scan button
        scanButton.addEventListener('click', function(e) {
            // Only prevent default if no file is selected
            if (fileInput.files.length === 0) {
                e.preventDefault();
                alert('Please select a file to scan');
                return;
            }
            
            // Add loading state to button
            scanButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            scanButton.disabled = true;
            
            // Allow form submission to proceed
            uploadForm.submit();
        });
        
        // Add change handler for file input to update UI
        fileInput.addEventListener('change', function() {
            if (fileInput.files.length > 0) {
                const fileName = fileInput.files[0].name;
                const fileNameDisplay = document.getElementById('file-name');
                
                if (fileNameDisplay) {
                    fileNameDisplay.textContent = fileName;
                    fileNameDisplay.style.display = 'block';
                }
                
                // Update scan button to show it's ready
                scanButton.innerHTML = 'Scan Document <i class="fas fa-arrow-right"></i>';
                scanButton.classList.add('ready');
            }
        });
        
        // Add form submit handler
        uploadForm.addEventListener('submit', function(e) {
            // Validate file is selected
            if (fileInput.files.length === 0) {
                e.preventDefault();
                alert('Please select a file to scan');
                return;
            }
            
            // Add loading state to button
            scanButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            scanButton.disabled = true;
        });
    }
    
    // Fix for mobile devices
    if (fileInput) {
        fileInput.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
});
