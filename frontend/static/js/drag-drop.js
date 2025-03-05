/**
 * Enhanced Drag and Drop File Upload
 * Provides a modern, animated interface for file uploads
 */

class DragDropUpload {
  constructor(options = {}) {
    // Default options
    this.options = {
      dropzoneSelector: '#drop-area',
      fileInputSelector: '#file-input',
      fileDisplaySelector: '#file-name',
      progressSelector: '#upload-progress',
      maxFileSize: 10 * 1024 * 1024, // 10MB
      allowedTypes: ['text/plain', 'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
      ...options
    };
    
    // Elements
    this.dropzone = document.querySelector(this.options.dropzoneSelector);
    this.fileInput = document.querySelector(this.options.fileInputSelector);
    this.fileDisplay = document.querySelector(this.options.fileDisplaySelector);
    this.progressBar = document.querySelector(this.options.progressSelector);
    
    // Bind methods
    this.handleDragOver = this.handleDragOver.bind(this);
    this.handleDragLeave = this.handleDragLeave.bind(this);
    this.handleDrop = this.handleDrop.bind(this);
    this.handleFileSelect = this.handleFileSelect.bind(this);
    
    // Initialize
    if (this.dropzone && this.fileInput) {
      this.initialize();
    }
  }
  
  initialize() {
    // Add event listeners for drag and drop
    this.dropzone.addEventListener('dragover', this.handleDragOver);
    this.dropzone.addEventListener('dragleave', this.handleDragLeave);
    this.dropzone.addEventListener('drop', this.handleDrop);
    
    // Click on dropzone to trigger file input
    this.dropzone.addEventListener('click', () => {
      this.fileInput.click();
    });
    
    // File input change event
    this.fileInput.addEventListener('change', this.handleFileSelect);
    
    // Add animation classes
    this.dropzone.classList.add('glass-dropzone', 'scale-in');
  }
  
  handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    
    this.dropzone.classList.add('active');
    
    // Add pulsing animation
    if (!this.dropzone.classList.contains('pulse')) {
      this.dropzone.classList.add('pulse');
    }
  }
  
  handleDragLeave(e) {
    e.preventDefault();
    e.stopPropagation();
    
    this.dropzone.classList.remove('active', 'pulse');
  }
  
  handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    
    this.dropzone.classList.remove('active', 'pulse');
    
    const files = e.dataTransfer.files;
    this.processFiles(files);
  }
  
  handleFileSelect(e) {
    const files = e.target.files;
    this.processFiles(files);
  }
  
  processFiles(files) {
    if (!files.length) return;
    
    const validFiles = [];
    const invalidFiles = [];
    
    // Validate files
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      // Check file type
      if (!this.options.allowedTypes.includes(file.type)) {
        invalidFiles.push({
          name: file.name,
          reason: 'Unsupported file type'
        });
        continue;
      }
      
      // Check file size
      if (file.size > this.options.maxFileSize) {
        invalidFiles.push({
          name: file.name,
          reason: 'File size exceeds limit'
        });
        continue;
      }
      
      validFiles.push(file);
    }
    
    // Handle valid files
    if (validFiles.length) {
      this.displayFiles(validFiles);
      
      // Simulate progress bar (in a real app, this would be tied to actual upload progress)
      if (this.progressBar) {
        this.simulateProgress();
      }
    }
    
    // Show errors for invalid files
    if (invalidFiles.length) {
      this.showErrors(invalidFiles);
    }
    
    // If no valid files were selected, clear the file input
    if (validFiles.length === 0) {
      this.fileInput.value = '';
    }
  }
  
  displayFiles(files) {
    if (!this.fileDisplay) return;
    
    const fileNames = files.map(file => file.name);
    
    // Create file chips
    const fileChipsHTML = fileNames.map(name => `
      <div class="file-chip slide-in-up">
        <i class="fas fa-file"></i>
        <span>${name}</span>
        <button type="button" class="remove-file" data-filename="${name}">&times;</button>
      </div>
    `).join('');
    
    this.fileDisplay.innerHTML = fileChipsHTML;
    this.fileDisplay.style.display = 'flex';
    
    // Add event listeners to remove buttons
    const removeButtons = this.fileDisplay.querySelectorAll('.remove-file');
    removeButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        const filename = e.target.dataset.filename;
        const chip = e.target.parentElement;
        
        // Add remove animation
        chip.classList.add('slide-out');
        
        // Remove chip after animation
        setTimeout(() => {
          chip.remove();
          
          // If no chips left, hide the display
          if (this.fileDisplay.children.length === 0) {
            this.fileDisplay.style.display = 'none';
            this.fileInput.value = '';
          }
        }, 300);
      });
    });
  }
  
  showErrors(invalidFiles) {
    // Create error notifications
    invalidFiles.forEach(file => {
      this.showNotification(`Error: ${file.name} - ${file.reason}`, 'danger');
    });
  }
  
  showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `glass-notification ${type} slide-in-up`;
    
    // Add content
    notification.innerHTML = `
      <div class="notification-content">
        <i class="fas ${this.getIconForType(type)}"></i>
        <span>${message}</span>
      </div>
      <button type="button" class="close-notification">&times;</button>
    `;
    
    // Add to page
    const notificationsContainer = document.querySelector('.notifications-container');
    if (notificationsContainer) {
      notificationsContainer.appendChild(notification);
    } else {
      // Create container if it doesn't exist
      const container = document.createElement('div');
      container.className = 'notifications-container';
      container.appendChild(notification);
      document.body.appendChild(container);
    }
    
    // Add close button functionality
    const closeButton = notification.querySelector('.close-notification');
    closeButton.addEventListener('click', () => {
      notification.classList.add('closing');
      setTimeout(() => {
        notification.remove();
      }, 300);
    });
    
    // Auto-close after 5 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.classList.add('closing');
        setTimeout(() => {
          notification.remove();
        }, 300);
      }
    }, 5000);
  }
  
  getIconForType(type) {
    switch (type) {
      case 'success': return 'fa-check-circle';
      case 'warning': return 'fa-exclamation-triangle';
      case 'danger': return 'fa-times-circle';
      case 'info':
      default: return 'fa-info-circle';
    }
  }
  
  simulateProgress() {
    // Reset progress
    const progressInner = this.progressBar.querySelector('.glass-progress-bar');
    if (!progressInner) return;
    
    progressInner.style.width = '0%';
    this.progressBar.style.display = 'block';
    
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 10;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
        
        // Show success message
        this.showNotification('Files ready for upload!', 'success');
        
        // Hide progress bar after a delay
        setTimeout(() => {
          this.progressBar.style.display = 'none';
        }, 1000);
      }
      
      progressInner.style.width = `${progress}%`;
    }, 200);
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.dragDropUpload = new DragDropUpload();
  
  // Add CSS for file chips and animations
  const style = document.createElement('style');
  style.textContent = `
    .file-chip {
      display: inline-flex;
      align-items: center;
      background: var(--surface-color);
      backdrop-filter: blur(var(--glass-blur));
      border-radius: 50px;
      padding: 8px 16px;
      margin: 5px;
      box-shadow: var(--shadow);
      transition: all 0.3s ease;
    }
    
    .file-chip i {
      margin-right: 8px;
      color: var(--primary-color);
    }
    
    .file-chip .remove-file {
      background: none;
      border: none;
      color: var(--text-secondary);
      cursor: pointer;
      margin-left: 8px;
      font-size: 16px;
      transition: color 0.3s ease;
    }
    
    .file-chip .remove-file:hover {
      color: var(--danger-color);
    }
    
    .file-chip.slide-out {
      transform: translateX(100px);
      opacity: 0;
    }
    
    .notifications-container {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 9999;
      width: 300px;
    }
    
    @keyframes pulse {
      0% { transform: scale(1); }
      50% { transform: scale(1.02); }
      100% { transform: scale(1); }
    }
    
    .pulse {
      animation: pulse 1s infinite;
    }
  `;
  document.head.appendChild(style);
});
