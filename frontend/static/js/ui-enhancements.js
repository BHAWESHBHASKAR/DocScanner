/**
 * Modern Professional UI Enhancements for Document Scanner
 * Adds animations, transitions, and interactive elements for a production-grade experience
 * @version 2.0
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize document comparison view if it exists
    initDocumentComparison();
    
    // Initialize match badges
    initMatchBadges();
    // Header scroll effect with smooth transition
    const header = document.querySelector('header.glass-nav');
    if (header) {
        const handleScroll = () => {
            const scrollPosition = window.scrollY;
            if (scrollPosition > 10) {
                header.classList.add('scrolled');
                // Add subtle shadow intensity based on scroll position (max at 100px scroll)
                const shadowIntensity = Math.min(scrollPosition / 100, 1);
                header.style.boxShadow = `0 10px 30px rgba(0, 0, 0, ${0.05 + (shadowIntensity * 0.1)})`;
            } else {
                header.classList.remove('scrolled');
                header.style.boxShadow = '';
            }
        };
        
        // Use passive event listener for better performance
        window.addEventListener('scroll', handleScroll, { passive: true });
        // Initial call to set correct state on page load
        handleScroll();
    }

    // Add active class to current nav link
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (href !== '/' && currentPath.startsWith(href))) {
            link.classList.add('active');
        }
    });

    // Enhanced card hover effects with subtle animations
    const cards = document.querySelectorAll('.card, .document-card, .glass-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
            this.style.boxShadow = 'var(--card-hover-shadow)';
            
            // Add subtle highlight to card border
            this.style.borderColor = 'rgba(var(--primary-color-rgb), 0.2)';
            
            // Animate child elements for a more interactive feel
            const cardTitle = this.querySelector('h2, h3, .card-title');
            if (cardTitle) {
                cardTitle.style.color = 'var(--primary-color)';
                cardTitle.style.transition = 'color 0.3s ease';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
            this.style.borderColor = '';
            
            // Reset child elements
            const cardTitle = this.querySelector('h2, h3, .card-title');
            if (cardTitle) {
                cardTitle.style.color = '';
            }
        });
    });

    // Enhanced button interactions with modern effects
    const buttons = document.querySelectorAll('.btn, .glass-btn');
    buttons.forEach(button => {
        // Add ripple effect container
        if (!button.querySelector('.ripple-effect')) {
            const rippleContainer = document.createElement('span');
            rippleContainer.classList.add('ripple-effect');
            button.appendChild(rippleContainer);
            button.style.position = 'relative';
            button.style.overflow = 'hidden';
        }
        
        button.addEventListener('mousedown', function(e) {
            this.style.transform = 'scale(0.98)';
            
            // Create ripple effect
            const rippleContainer = this.querySelector('.ripple-effect');
            const rect = button.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height) * 2;
            
            // Remove existing ripples
            rippleContainer.innerHTML = '';
            
            // Create new ripple
            const ripple = document.createElement('span');
            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${e.clientX - rect.left - (size/2)}px`;
            ripple.style.top = `${e.clientY - rect.top - (size/2)}px`;
            ripple.classList.add('ripple');
            rippleContainer.appendChild(ripple);
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = 'scale(1)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Add ripple effect styles if not already in document
    if (!document.getElementById('ripple-styles')) {
        const style = document.createElement('style');
        style.id = 'ripple-styles';
        style.textContent = `
            .ripple-effect {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                overflow: hidden;
                pointer-events: none;
            }
            .ripple {
                position: absolute;
                border-radius: 50%;
                background-color: rgba(255, 255, 255, 0.4);
                transform: scale(0);
                animation: ripple-animation 0.6s linear;
            }
            @keyframes ripple-animation {
                to {
                    transform: scale(1);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    // Form input focus effects
    const formInputs = document.querySelectorAll('input, textarea, select');
    formInputs.forEach(input => {
        const parent = input.parentElement;
        
        input.addEventListener('focus', function() {
            if (parent.classList.contains('form-group')) {
                parent.classList.add('focused');
            }
        });
        
        input.addEventListener('blur', function() {
            if (parent.classList.contains('form-group')) {
                parent.classList.remove('focused');
            }
        });
    });

    // File input enhancement
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'No file selected';
            const fileNameDisplay = document.getElementById('file-name');
            if (fileNameDisplay) {
                fileNameDisplay.textContent = fileName;
                fileNameDisplay.style.display = 'block';
            }
            
            // Enable scan button if file is selected
            const scanButton = document.getElementById('scan-button');
            if (scanButton && this.files.length > 0) {
                scanButton.disabled = false;
                scanButton.classList.add('ready');
            }
        });
    });

    // Animated counters for statistics
    const counters = document.querySelectorAll('.counter');
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 1500; // ms
        const step = Math.ceil(target / (duration / 16)); // 60fps
        
        let current = 0;
        const updateCounter = () => {
            current += step;
            if (current >= target) {
                counter.textContent = target.toLocaleString();
            } else {
                counter.textContent = current.toLocaleString();
                requestAnimationFrame(updateCounter);
            }
        };
        
        // Start animation when element is in viewport
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateCounter();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        observer.observe(counter);
    });
    
    // Initialize dropdown menus
    const dropdowns = document.querySelectorAll('.glass-dropdown');
    dropdowns.forEach(dropdown => {
        const dropdownContent = dropdown.querySelector('.glass-dropdown-content');
        if (dropdownContent) {
            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!dropdown.contains(e.target)) {
                    dropdownContent.style.display = 'none';
                    setTimeout(() => {
                        dropdownContent.style.display = '';
                    }, 10);
                }
            });
        }
    });
    
    // Social links hover effects
    const socialLinks = document.querySelectorAll('.social-link');
    socialLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
    
    // Initialize document comparison view if it exists
    initDocumentComparison();
    
    // Initialize match badges
    initMatchBadges();
});

/**
 * Initialize document comparison view with highlighting
 */
function initDocumentComparison() {
    const comparisonContainer = document.querySelector('.comparison-container');
    if (!comparisonContainer) return;
    
    // Highlight differences between documents
    const sourceContent = document.querySelector('.source-document .comparison-content');
    const matchContent = document.querySelector('.matched-document .comparison-content');
    
    if (sourceContent && matchContent) {
        // This is a simplified diff highlighting for demonstration
        // In a real implementation, you would use a proper diff algorithm
        const sourceText = sourceContent.textContent;
        const matchText = matchContent.textContent;
        
        // Split into words and compare
        const sourceWords = sourceText.split(/\s+/);
        const matchWords = matchText.split(/\s+/);
        
        let sourceHtml = '';
        let matchHtml = '';
        
        // Simple word-by-word comparison (this is just for UI demonstration)
        sourceWords.forEach((word, index) => {
            if (index < matchWords.length) {
                if (word === matchWords[index]) {
                    sourceHtml += `<span class="match-highlight">${word}</span> `;
                    matchHtml += `<span class="match-highlight">${matchWords[index]}</span> `;
                } else {
                    sourceHtml += `<span class="diff-highlight">${word}</span> `;
                    matchHtml += `<span class="diff-highlight">${matchWords[index]}</span> `;
                }
            } else {
                sourceHtml += `<span class="diff-highlight">${word}</span> `;
            }
        });
        
        // Add any remaining words in the match document
        if (matchWords.length > sourceWords.length) {
            for (let i = sourceWords.length; i < matchWords.length; i++) {
                matchHtml += `<span class="diff-highlight">${matchWords[i]}</span> `;
            }
        }
        
        sourceContent.innerHTML = sourceHtml;
        matchContent.innerHTML = matchHtml;
    }
}

/**
 * Initialize match badges with appropriate colors based on similarity score
 */
function initMatchBadges() {
    const matchBadges = document.querySelectorAll('.match-badge');
    matchBadges.forEach(badge => {
        const score = parseFloat(badge.getAttribute('data-score') || '0');
        
        // Remove any existing classes
        badge.classList.remove('exact', 'high', 'medium', 'low');
        
        // Add appropriate class based on score
        if (score === 100) {
            badge.classList.add('exact');
            badge.innerHTML = `<i class="fas fa-check-circle"></i> Exact Match`;
        } else if (score >= 80) {
            badge.classList.add('high');
            badge.innerHTML = `<i class="fas fa-star"></i> High Match (${score}%)`;
        } else if (score >= 50) {
            badge.classList.add('medium');
            badge.innerHTML = `<i class="fas fa-star-half-alt"></i> Medium Match (${score}%)`;
        } else {
            badge.classList.add('low');
            badge.innerHTML = `<i class="fas fa-exclamation-circle"></i> Low Match (${score}%)`;
        }
    });
}
