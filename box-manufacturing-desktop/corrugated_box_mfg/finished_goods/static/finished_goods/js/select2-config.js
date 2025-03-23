$(document).ready(function() {
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