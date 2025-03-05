/**
 * Modern Icon System
 * Provides animated, interactive icons with consistent styling
 */

class IconSystem {
  constructor() {
    this.icons = {};
    this.initialize();
  }
  
  initialize() {
    // Register icon animations
    this.registerIconAnimations();
    
    // Initialize interactive icons
    this.initializeInteractiveIcons();
    
    // Add icon styles
    this.addIconStyles();
  }
  
  registerIconAnimations() {
    // Define animations for different icons
    this.icons = {
      'fa-file-search': {
        animation: 'pulse',
        duration: '2s',
        trigger: 'hover'
      },
      'fa-file-upload': {
        animation: 'bounce',
        duration: '1s',
        trigger: 'hover'
      },
      'fa-user': {
        animation: 'wobble',
        duration: '1s',
        trigger: 'hover'
      },
      'fa-chart-line': {
        animation: 'slideUp',
        duration: '1s',
        trigger: 'hover'
      },
      'fa-user-circle': {
        animation: 'pulse',
        duration: '1s',
        trigger: 'hover'
      },
      'fa-adjust': {
        animation: 'rotate',
        duration: '1s',
        trigger: 'hover'
      },
      'fa-sign-in-alt': {
        animation: 'slideRight',
        duration: '1s',
        trigger: 'hover'
      },
      'fa-user-plus': {
        animation: 'pop',
        duration: '0.5s',
        trigger: 'hover'
      },
      'fa-home': {
        animation: 'bounce',
        duration: '1s',
        trigger: 'hover'
      }
    };
  }
  
  initializeInteractiveIcons() {
    // Find all Font Awesome icons
    const icons = document.querySelectorAll('.fas, .fab, .far, .fal, .fad');
    
    icons.forEach(icon => {
      // Get icon class (fa-xxx)
      const iconClass = Array.from(icon.classList).find(cls => cls.startsWith('fa-'));
      if (!iconClass) return;
      
      // Add animation class if defined
      const animation = this.icons[iconClass];
      if (animation) {
        // Add animation trigger
        if (animation.trigger === 'hover') {
          icon.addEventListener('mouseenter', () => {
            icon.classList.add(`icon-animation-${animation.animation}`);
          });
          
          icon.addEventListener('animationend', () => {
            icon.classList.remove(`icon-animation-${animation.animation}`);
          });
        } else if (animation.trigger === 'load') {
          icon.classList.add(`icon-animation-${animation.animation}`);
        }
        
        // Add animation duration if specified
        if (animation.duration) {
          icon.style.animationDuration = animation.duration;
        }
      }
      
      // Add interactive class
      icon.classList.add('interactive-icon');
    });
  }
  
  addIconStyles() {
    // Create style element
    const style = document.createElement('style');
    
    // Define animation keyframes and classes
    style.textContent = `
      /* Icon Base Styles */
      .interactive-icon {
        display: inline-block;
        transition: transform 0.3s ease, color 0.3s ease;
      }
      
      /* Icon Animations */
      @keyframes icon-pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
      }
      
      @keyframes icon-bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
      }
      
      @keyframes icon-wobble {
        0% { transform: rotate(0deg); }
        25% { transform: rotate(-10deg); }
        50% { transform: rotate(0deg); }
        75% { transform: rotate(10deg); }
        100% { transform: rotate(0deg); }
      }
      
      @keyframes icon-slideUp {
        0% { transform: translateY(10px); opacity: 0; }
        100% { transform: translateY(0); opacity: 1; }
      }
      
      @keyframes icon-rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      @keyframes icon-slideRight {
        0% { transform: translateX(-10px); opacity: 0; }
        100% { transform: translateX(0); opacity: 1; }
      }
      
      @keyframes icon-pop {
        0% { transform: scale(0.8); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
      }
      
      /* Animation Classes */
      .icon-animation-pulse {
        animation: icon-pulse 1s ease;
      }
      
      .icon-animation-bounce {
        animation: icon-bounce 1s ease;
      }
      
      .icon-animation-wobble {
        animation: icon-wobble 1s ease;
      }
      
      .icon-animation-slideUp {
        animation: icon-slideUp 1s ease;
      }
      
      .icon-animation-rotate {
        animation: icon-rotate 1s linear;
      }
      
      .icon-animation-slideRight {
        animation: icon-slideRight 1s ease;
      }
      
      .icon-animation-pop {
        animation: icon-pop 0.5s ease;
      }
      
      /* Icon Hover Effects */
      .nav-links a:hover .fas,
      .nav-links a:hover .fab,
      .nav-links a:hover .far,
      .nav-links a:hover .fal,
      .nav-links a:hover .fad {
        color: var(--primary-color);
      }
      
      /* Icon Sizes */
      .icon-sm {
        font-size: 0.875rem;
      }
      
      .icon-lg {
        font-size: 1.5rem;
      }
      
      .icon-xl {
        font-size: 2rem;
      }
      
      /* Icon Colors */
      .icon-primary { color: var(--primary-color); }
      .icon-secondary { color: var(--secondary-color); }
      .icon-accent { color: var(--accent-color); }
      .icon-success { color: var(--success-color); }
      .icon-warning { color: var(--warning-color); }
      .icon-danger { color: var(--danger-color); }
      .icon-info { color: var(--info-color); }
    `;
    
    // Add style to document
    document.head.appendChild(style);
  }
  
  /**
   * Add a custom animation to an icon
   * @param {string} iconClass - Font Awesome icon class (e.g., 'fa-file-search')
   * @param {string} animation - Animation name
   * @param {string} duration - Animation duration (e.g., '1s')
   * @param {string} trigger - Animation trigger ('hover', 'load', 'click')
   */
  addIconAnimation(iconClass, animation, duration = '1s', trigger = 'hover') {
    // Add to icons object
    this.icons[iconClass] = {
      animation,
      duration,
      trigger
    };
    
    // Re-initialize interactive icons
    this.initializeInteractiveIcons();
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.iconSystem = new IconSystem();
});
