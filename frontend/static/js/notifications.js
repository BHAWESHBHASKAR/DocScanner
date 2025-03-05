/**
 * Animated Notifications System
 * Provides beautiful, animated notifications with glassmorphism styling
 */

class NotificationSystem {
  constructor() {
    this.container = null;
    this.notifications = [];
    this.initialize();
  }
  
  initialize() {
    // Create container if it doesn't exist
    this.container = document.querySelector('.notifications-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'notifications-container';
      document.body.appendChild(this.container);
    }
    
    // Listen for flash messages to convert them
    this.convertFlashMessages();
  }
  
  convertFlashMessages() {
    // Get all flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    
    // Convert each to a notification
    flashMessages.forEach((flash, index) => {
      // Get content and type
      const content = flash.textContent.trim();
      let type = 'info';
      
      if (flash.classList.contains('success')) {
        type = 'success';
      } else if (flash.classList.contains('error')) {
        type = 'danger';
      } else if (flash.classList.contains('warning')) {
        type = 'warning';
      }
      
      // Hide original flash
      flash.style.display = 'none';
      
      // Show as notification with delay
      setTimeout(() => {
        this.show(content, type);
      }, index * 200); // Stagger notifications
    });
  }
  
  /**
   * Show a notification
   * @param {string} message - The notification message
   * @param {string} type - Type of notification: 'success', 'info', 'warning', 'danger'
   * @param {number} duration - Duration in ms before auto-close (0 for no auto-close)
   * @param {boolean} dismissible - Whether the notification can be dismissed
   */
  show(message, type = 'info', duration = 5000, dismissible = true) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `glass-notification ${type} slide-in-up`;
    
    // Generate unique ID
    const id = `notification-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
    notification.id = id;
    
    // Add content
    notification.innerHTML = `
      <div class="notification-content">
        <div class="notification-icon">
          <i class="fas ${this.getIconForType(type)}"></i>
        </div>
        <div class="notification-message">${message}</div>
      </div>
      ${dismissible ? '<button type="button" class="close-notification">&times;</button>' : ''}
      ${duration > 0 ? '<div class="notification-progress"><div class="notification-progress-bar"></div></div>' : ''}
    `;
    
    // Add to container
    this.container.appendChild(notification);
    
    // Add to tracking array
    this.notifications.push({
      id,
      element: notification,
      timer: null
    });
    
    // Add close button functionality
    if (dismissible) {
      const closeButton = notification.querySelector('.close-notification');
      closeButton.addEventListener('click', () => {
        this.dismiss(id);
      });
    }
    
    // Add progress bar animation
    if (duration > 0) {
      const progressBar = notification.querySelector('.notification-progress-bar');
      if (progressBar) {
        // Start at full width
        progressBar.style.width = '100%';
        
        // Animate to 0 over the duration
        setTimeout(() => {
          progressBar.style.width = '0%';
          progressBar.style.transition = `width ${duration}ms linear`;
        }, 10);
      }
      
      // Set auto-dismiss timer
      const timer = setTimeout(() => {
        this.dismiss(id);
      }, duration);
      
      // Update timer in tracking array
      const notificationObj = this.notifications.find(n => n.id === id);
      if (notificationObj) {
        notificationObj.timer = timer;
      }
    }
    
    // Return ID for potential manual dismissal
    return id;
  }
  
  /**
   * Dismiss a notification
   * @param {string} id - ID of the notification to dismiss
   */
  dismiss(id) {
    // Find notification in tracking array
    const index = this.notifications.findIndex(n => n.id === id);
    if (index === -1) return;
    
    const notification = this.notifications[index];
    
    // Clear timer if exists
    if (notification.timer) {
      clearTimeout(notification.timer);
    }
    
    // Add closing animation
    notification.element.classList.add('closing');
    
    // Remove after animation
    setTimeout(() => {
      if (notification.element.parentNode) {
        notification.element.remove();
      }
      
      // Remove from tracking array
      this.notifications.splice(index, 1);
    }, 300);
  }
  
  /**
   * Dismiss all notifications
   */
  dismissAll() {
    // Clone array to avoid issues during iteration
    const notificationsToRemove = [...this.notifications];
    
    // Dismiss each notification
    notificationsToRemove.forEach(notification => {
      this.dismiss(notification.id);
    });
  }
  
  /**
   * Get icon class for notification type
   * @param {string} type - Notification type
   * @returns {string} - Font Awesome icon class
   */
  getIconForType(type) {
    switch (type) {
      case 'success': return 'fa-check-circle';
      case 'warning': return 'fa-exclamation-triangle';
      case 'danger': return 'fa-times-circle';
      case 'info':
      default: return 'fa-info-circle';
    }
  }
  
  /**
   * Shorthand for success notification
   */
  success(message, duration = 5000) {
    return this.show(message, 'success', duration);
  }
  
  /**
   * Shorthand for info notification
   */
  info(message, duration = 5000) {
    return this.show(message, 'info', duration);
  }
  
  /**
   * Shorthand for warning notification
   */
  warning(message, duration = 5000) {
    return this.show(message, 'warning', duration);
  }
  
  /**
   * Shorthand for danger/error notification
   */
  error(message, duration = 5000) {
    return this.show(message, 'danger', duration);
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.notifications = new NotificationSystem();
  
  // Add CSS for notifications
  const style = document.createElement('style');
  style.textContent = `
    .notifications-container {
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 9999;
      width: 300px;
      max-width: calc(100vw - 40px);
    }
    
    .glass-notification {
      position: relative;
      overflow: hidden;
      margin-bottom: 10px;
    }
    
    .notification-content {
      display: flex;
      align-items: center;
      padding: 16px;
    }
    
    .notification-icon {
      margin-right: 12px;
      font-size: 20px;
    }
    
    .notification-message {
      flex: 1;
    }
    
    .close-notification {
      background: none;
      border: none;
      color: var(--text-secondary);
      font-size: 18px;
      cursor: pointer;
      padding: 0 16px;
      transition: color 0.3s ease;
    }
    
    .close-notification:hover {
      color: var(--text-primary);
    }
    
    .notification-progress {
      position: absolute;
      bottom: 0;
      left: 0;
      width: 100%;
      height: 3px;
      background: rgba(255, 255, 255, 0.2);
    }
    
    .notification-progress-bar {
      height: 100%;
      width: 100%;
      background: rgba(255, 255, 255, 0.5);
    }
    
    .glass-notification.success .notification-icon {
      color: var(--success-color);
    }
    
    .glass-notification.warning .notification-icon {
      color: var(--warning-color);
    }
    
    .glass-notification.danger .notification-icon {
      color: var(--danger-color);
    }
    
    .glass-notification.info .notification-icon {
      color: var(--info-color);
    }
  `;
  document.head.appendChild(style);
});
