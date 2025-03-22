document.addEventListener('DOMContentLoaded', function() {
    // Get current path
    const currentPath = window.location.pathname;
    
    // Remove active class from all navigation links
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Clear any other active links that might have been set by other scripts
    document.querySelectorAll('.sidebar .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Find the right link to highlight based on data-path attribute
    let foundActive = false;
    
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
        const dataPath = link.getAttribute('data-path');
        if (dataPath) {
            const patterns = dataPath.split('|');
            for (const pattern of patterns) {
                try {
                    const regex = new RegExp(pattern);
                    if (regex.test(currentPath)) {
                        link.classList.add('active');
                        console.log('Highlighting:', link.textContent.trim(), 'for path:', currentPath);
                        foundActive = true;
                        break;
                    }
                } catch (e) {
                    console.error('Invalid regex pattern:', pattern, e);
                }
            }
        }
    });
    
    // If no match found and we're at the index page, default to first item
    if (!foundActive && (currentPath === '/finished-goods/' || currentPath === '/finished-goods')) {
        const firstLink = document.querySelector('.sidebar-nav .nav-link');
        if (firstLink) {
            firstLink.classList.add('active');
            console.log('Default highlight for index page:', firstLink.textContent.trim());
        }
    }
});