$(document).ready(function() {
    // Destroy any existing Select2 instances first
    if ($.fn.select2) {
        $('select').select2('destroy');
        
        // Reinitialize with better configuration
        $('select').select2({
            width: 'resolve',
            dropdownAutoWidth: true,
            dropdownParent: $('body'),
            closeOnSelect: true
        });
        
        // Handle opening of select2 dropdowns
        $(document).on('select2:open', function() {
            setTimeout(function() {
                // Ensure dropdowns have proper height and position
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
    }
    
    // Precise sidebar navigation highlighting
    $('.sidebar-nav .nav-link').removeClass('active');
    
    // Get the current URL path
    const currentPath = window.location.pathname;
    
    // Check each link against the current path
    $('.sidebar-nav .nav-link').each(function() {
        const dataPath = $(this).attr('data-path');
        if (dataPath) {
            const patterns = dataPath.split('|');
            for (const pattern of patterns) {
                const regex = new RegExp(pattern);
                if (regex.test(currentPath)) {
                    $(this).addClass('active');
                    return;
                }
            }
        }
    });
});