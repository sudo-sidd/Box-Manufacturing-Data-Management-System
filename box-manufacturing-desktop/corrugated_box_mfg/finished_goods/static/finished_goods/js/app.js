$(document).ready(function() {
    /************************************
     * PART 1: Navigation Highlighting
     ************************************/
    console.log('Navigation and dropdown script running');
    
    const currentPath = window.location.pathname;
    console.log('Current path:', currentPath);
    
    // Remove active class from all navigation links
    $('.sidebar-nav .nav-link, .sidebar .nav-link').removeClass('active');
    
    // Find the right link to highlight based on data-path attribute
    let highlightFound = false;
    
    $('.sidebar-nav .nav-link').each(function() {
        const link = $(this);
        const dataPath = link.attr('data-path');
        if (!dataPath) return;
        
        const patterns = dataPath.split('|');
        for (const pattern of patterns) {
            try {
                const regex = new RegExp(pattern);
                if (regex.test(currentPath)) {
                    link.addClass('active');
                    console.log('✓ Highlighting:', link.text().trim());
                    highlightFound = true;
                    break;
                }
            } catch (e) {
                console.error('Invalid regex pattern:', pattern, e);
            }
        }
    });
    
    // Default to first item for index page if no match found
    if (!highlightFound && (currentPath === '/finished-goods/' || currentPath === '/finished-goods')) {
        $('.sidebar-nav .nav-link').first().addClass('active');
    }
    
    /************************************
     * PART 2: Select2 Configuration
     ************************************/
    // Initialize Select2 elements
    $('select:not(.no-select2)').select2({
        width: 'resolve',
        dropdownAutoWidth: true,
        dropdownParent: $('body'),
        closeOnSelect: true
    });
    
    // Fix dropdown positioning
    $(document).on('select2:open', function() {
        setTimeout(function() {
            const dropdown = $('.select2-container--open .select2-dropdown');
            dropdown.css({
                'z-index': 99999,
                'max-height': 'none',
                'overflow': 'visible'
            });
            
            $('.select2-results__options').css({
                'max-height': '350px',
                'overflow-y': 'auto'
            });
        }, 0);
    });
});