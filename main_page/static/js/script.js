$(document).ready(function(){

    /* Events */
    $('.tab').hover(function() {
        $('.tab').removeClass('tabhover');
        $(this).addClass('tabhover');
    });
    $('.tab').click(function() {
        $('.tab').removeClass('tabcurrent');
        $(this).addClass('tabcurrent');
    });
    $('#panels a').click(function(event) {
        var panel_id = $(this).attr('href');
        $('.panel').hide();
        event.preventDefault();
        $(panel_id).show();
    });

});
