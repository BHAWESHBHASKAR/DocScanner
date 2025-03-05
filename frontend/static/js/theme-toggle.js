/**
 * Theme Toggle Functionality
 * Handles dark/light theme switching with localStorage persistence
 */

class ThemeManager {
  constructor() {
    this.themeToggleBtn = document.getElementById('theme-toggle');
    this.body = document.body;
    this.THEME_KEY = 'docscanner-theme';
    this.DARK_THEME = 'dark';
    this.LIGHT_THEME = 'light';
    
    this.initialize();
  }
  
  initialize() {
    // Load saved theme
    this.loadSavedTheme();
    
    // Add event listener to theme toggle button
    if (this.themeToggleBtn) {
      this.themeToggleBtn.addEventListener('click', () => this.toggleTheme());
    }
    
    // Add event listener for OS theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
      if (!localStorage.getItem(this.THEME_KEY)) {
        this.setTheme(e.matches ? this.DARK_THEME : this.LIGHT_THEME, false);
      }
    });
  }
  
  loadSavedTheme() {
    const savedTheme = localStorage.getItem(this.THEME_KEY);
    
    // Always start with light theme
    this.setTheme(this.LIGHT_THEME);
    localStorage.setItem(this.THEME_KEY, this.LIGHT_THEME);
  }
  
  toggleTheme() {
    const newTheme = this.body.classList.contains(this.DARK_THEME) 
      ? this.LIGHT_THEME 
      : this.DARK_THEME;
    
    this.setTheme(newTheme);
    
    // Animate the toggle icon
    if (this.themeToggleBtn) {
      this.themeToggleBtn.classList.add('rotate-animation');
      setTimeout(() => {
        this.themeToggleBtn.classList.remove('rotate-animation');
      }, 500);
    }
  }
  
  setTheme(theme, saveToStorage = true) {
    // Remove both classes first
    this.body.classList.remove(this.DARK_THEME, this.LIGHT_THEME);
    
    // Add the appropriate class
    this.body.classList.add(theme);
    
    // Update toggle button icon if it exists
    if (this.themeToggleBtn) {
      const iconElement = this.themeToggleBtn.querySelector('i');
      if (iconElement) {
        iconElement.className = theme === this.DARK_THEME 
          ? 'fas fa-sun' 
          : 'fas fa-moon';
      }
    }
    
    // Save to localStorage if needed
    if (saveToStorage) {
      localStorage.setItem(this.THEME_KEY, theme);
    }
    
    // Dispatch custom event
    window.dispatchEvent(new CustomEvent('themechange', { detail: { theme } }));
  }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.themeManager = new ThemeManager();
});

// Add CSS animation for the toggle button
const style = document.createElement('style');
style.textContent = `
  @keyframes rotate-animation {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .rotate-animation {
    animation: rotate-animation 0.5s ease-in-out;
  }
`;
document.head.appendChild(style);
