/**
 * Interactive User Menu
 * Provides an animated, interactive dropdown menu for user actions
 */

class UserMenu {
  constructor() {
    this.menuToggle = document.getElementById('user-menu-toggle');
    this.menu = document.querySelector('.user-menu');
    this.isOpen = false;
    
    // Bind methods
    this.toggleMenu = this.toggleMenu.bind(this);
    this.handleClickOutside = this.handleClickOutside.bind(this);
    
    // Initialize
    if (this.menuToggle && this.menu) {
      this.initialize();
    }
  }
  
  initialize() {
    // Convert regular menu to glass menu
    this.menu.classList.add('glass-dropdown-content');
    
    // Add event listener to toggle button
    this.menuToggle.addEventListener('click', this.toggleMenu);
    
    // Add click outside listener
    document.addEventListener('click', this.handleClickOutside);
    
    // Add menu items with animations
    this.enhanceMenuItems();
  }
  
  enhanceMenuItems() {
    // Get all menu items
    const menuItems = this.menu.querySelectorAll('li');
    
    // Add animation classes with staggered delays
    menuItems.forEach((item, index) => {
      item.classList.add('menu-item', `stagger-${index + 1}`);
      
      // Add icon container if not present
      const link = item.querySelector('a');
      if (link) {
        // Extract existing icon if present
        const existingIcon = link.querySelector('i');
        let iconHTML = '';
        
        if (existingIcon) {
          // Use existing icon
          iconHTML = existingIcon.outerHTML;
          existingIcon.remove();
        }
        
        // Wrap content in spans for animation
        const textContent = link.textContent.trim();
        link.innerHTML = `
          <div class="menu-icon">${iconHTML}</div>
          <span class="menu-text">${textContent}</span>
        `;
      }
    });
    
    // Add additional menu items if they don't exist
    this.addAdditionalMenuItems();
  }
  
  addAdditionalMenuItems() {
    // Check if we need to add items
    const hasSettings = Array.from(this.menu.querySelectorAll('a')).some(
      link => link.textContent.includes('Settings')
    );
    
    if (!hasSettings) {
      // Create settings item
      const settingsItem = document.createElement('li');
      settingsItem.classList.add('menu-item', `stagger-${this.menu.querySelectorAll('li').length + 1}`);
      settingsItem.innerHTML = `
        <a href="#settings">
          <div class="menu-icon"><i class="fas fa-cog"></i></div>
          <span class="menu-text">Settings</span>
        </a>
      `;
      this.menu.appendChild(settingsItem);
      
      // Create help item
      const helpItem = document.createElement('li');
      helpItem.classList.add('menu-item', `stagger-${this.menu.querySelectorAll('li').length + 1}`);
      helpItem.innerHTML = `
        <a href="#help">
          <div class="menu-icon"><i class="fas fa-question-circle"></i></div>
          <span class="menu-text">Help</span>
        </a>
      `;
      this.menu.appendChild(helpItem);
    }
  }
  
  toggleMenu(e) {
    e.preventDefault();
    e.stopPropagation();
    
    this.isOpen = !this.isOpen;
    
    // Toggle active class on parent element
    const parent = this.menuToggle.parentElement;
    if (parent) {
      parent.classList.toggle('active', this.isOpen);
    }
    
    // Toggle menu visibility
    if (this.isOpen) {
      this.openMenu();
    } else {
      this.closeMenu();
    }
  }
  
  openMenu() {
    // Show menu
    this.menu.style.display = 'block';
    
    // Trigger animation
    setTimeout(() => {
      this.menu.classList.add('active');
      
      // Animate menu items
      const menuItems = this.menu.querySelectorAll('.menu-item');
      menuItems.forEach(item => {
        item.classList.add('animate-in');
      });
    }, 10);
    
    // Add active class to toggle button
    this.menuToggle.classList.add('active');
    
    // Add a subtle rotation to the icon
    const icon = this.menuToggle.querySelector('i');
    if (icon) {
      icon.style.transform = 'rotate(180deg)';
    }
  }
  
  closeMenu() {
    // Remove active class
    this.menu.classList.remove('active');
    
    // Remove animation from menu items
    const menuItems = this.menu.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
      item.classList.remove('animate-in');
    });
    
    // Hide menu after animation
    setTimeout(() => {
      this.menu.style.display = 'none';
    }, 300);
    
    // Remove active class from toggle button
    this.menuToggle.classList.remove('active');
    
    // Reset icon rotation
    const icon = this.menuToggle.querySelector('i');
    if (icon) {
      icon.style.transform = 'rotate(0deg)';
    }
  }
  
  handleClickOutside(e) {
    if (this.isOpen && !this.menu.contains(e.target) && !this.menuToggle.contains(e.target)) {
      this.isOpen = false;
      this.closeMenu();
      
      // Remove active class from parent
      const parent = this.menuToggle.parentElement;
      if (parent) {
        parent.classList.remove('active');
      }
    }
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.userMenu = new UserMenu();
  
  // Add CSS for menu animations
  const style = document.createElement('style');
  style.textContent = `
    .user-menu {
      min-width: 200px;
      right: 0;
      top: 100%;
      transition: all 0.3s ease;
      transform-origin: top right;
      transform: scale(0.9);
      opacity: 0;
      display: none;
    }
    
    .user-menu.active {
      transform: scale(1);
      opacity: 1;
    }
    
    .menu-item {
      opacity: 0;
      transform: translateY(10px);
      transition: all 0.3s ease;
    }
    
    .menu-item.animate-in {
      opacity: 1;
      transform: translateY(0);
    }
    
    .menu-item a {
      display: flex;
      align-items: center;
      padding: 12px 16px;
      color: var(--text-primary);
      transition: all 0.3s ease;
    }
    
    .menu-item a:hover {
      background: rgba(67, 97, 238, 0.1);
    }
    
    .menu-icon {
      margin-right: 12px;
      width: 20px;
      text-align: center;
      color: var(--primary-color);
    }
    
    #user-menu-toggle {
      display: flex;
      align-items: center;
    }
    
    #user-menu-toggle i {
      transition: transform 0.3s ease;
    }
    
    #user-menu-toggle.active {
      color: var(--primary-color);
    }
  `;
  document.head.appendChild(style);
});
