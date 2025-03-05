/**
 * Responsive Grid System
 * Provides dynamic, responsive grid layouts with animation support
 */

class ResponsiveGrid {
  constructor(options = {}) {
    // Default options
    this.options = {
      gridSelector: '.glass-grid',
      itemSelector: '.glass-card',
      gapSize: 24,
      minColumnWidth: 300,
      animateItems: true,
      ...options
    };
    
    // Initialize
    this.initialize();
  }
  
  initialize() {
    // Find all grid containers
    this.gridContainers = document.querySelectorAll(this.options.gridSelector);
    
    if (this.gridContainers.length) {
      // Initialize each grid
      this.gridContainers.forEach(grid => this.setupGrid(grid));
      
      // Add resize listener
      window.addEventListener('resize', this.debounce(() => {
        this.gridContainers.forEach(grid => this.updateGrid(grid));
      }, 200));
    }
  }
  
  setupGrid(grid) {
    // Set initial styles
    grid.style.display = 'grid';
    grid.style.gap = `${this.options.gapSize}px`;
    
    // Update grid template columns
    this.updateGrid(grid);
    
    // Add animation to items if enabled
    if (this.options.animateItems) {
      const items = grid.querySelectorAll(this.options.itemSelector);
      items.forEach((item, index) => {
        // Add animation classes
        item.classList.add('grid-item-animate');
        item.style.animationDelay = `${index * 0.1}s`;
        
        // Add intersection observer for scroll animation
        this.addScrollAnimation(item);
      });
    }
  }
  
  updateGrid(grid) {
    // Calculate number of columns based on container width
    const containerWidth = grid.clientWidth;
    const columnCount = Math.floor(containerWidth / this.options.minColumnWidth) || 1;
    
    // Update grid template columns
    grid.style.gridTemplateColumns = `repeat(${columnCount}, 1fr)`;
  }
  
  addScrollAnimation(item) {
    // Create intersection observer
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          // Add animation class when element enters viewport
          entry.target.classList.add('animate');
          // Stop observing after animation
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1 // Trigger when 10% of the item is visible
    });
    
    // Start observing
    observer.observe(item);
  }
  
  /**
   * Debounce function to limit function calls
   * @param {Function} func - Function to debounce
   * @param {number} wait - Wait time in milliseconds
   * @returns {Function} - Debounced function
   */
  debounce(func, wait) {
    let timeout;
    return function(...args) {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  }
  
  /**
   * Refresh all grids (useful after dynamic content changes)
   */
  refresh() {
    this.gridContainers.forEach(grid => this.updateGrid(grid));
  }
  
  /**
   * Add a new item to a grid with animation
   * @param {HTMLElement} grid - Grid container
   * @param {HTMLElement} item - Item to add
   */
  addItem(grid, item) {
    // Add animation class
    item.classList.add('grid-item-animate');
    
    // Initially hide item
    item.style.opacity = '0';
    
    // Add to grid
    grid.appendChild(item);
    
    // Trigger animation after a small delay
    setTimeout(() => {
      item.classList.add('animate');
      item.style.opacity = '1';
    }, 10);
    
    // Update grid layout
    this.updateGrid(grid);
  }
  
  /**
   * Remove an item from a grid with animation
   * @param {HTMLElement} item - Item to remove
   */
  removeItem(item) {
    // Add exit animation
    item.classList.add('exit');
    
    // Remove after animation
    setTimeout(() => {
      if (item.parentNode) {
        item.parentNode.removeChild(item);
        
        // Update grid layout
        const grid = item.closest(this.options.gridSelector);
        if (grid) {
          this.updateGrid(grid);
        }
      }
    }, 300);
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.responsiveGrid = new ResponsiveGrid();
  
  // Add CSS for grid animations
  const style = document.createElement('style');
  style.textContent = `
    .grid-item-animate {
      opacity: 0;
      transform: translateY(20px);
      transition: opacity 0.5s ease, transform 0.5s ease;
    }
    
    .grid-item-animate.animate {
      opacity: 1;
      transform: translateY(0);
    }
    
    .grid-item-animate.exit {
      opacity: 0;
      transform: scale(0.8);
      transition: opacity 0.3s ease, transform 0.3s ease;
    }
    
    /* Masonry-like grid for varying height items */
    .glass-masonry {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      grid-auto-rows: 10px;
      grid-gap: 24px;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
      .glass-grid, .glass-masonry {
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
      }
    }
    
    @media (max-width: 480px) {
      .glass-grid, .glass-masonry {
        grid-template-columns: 1fr;
      }
    }
  `;
  document.head.appendChild(style);
});
