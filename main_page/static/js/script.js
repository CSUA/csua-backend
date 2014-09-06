$(document).ready(function(){

    /* Navigation Bar */
    $('.navitemwithdropdown').hover(function() {
        $(this).find('.dropdown').show();
    }, function() {
        $(this).find('.dropdown').hide();
    });
    $('.dropdown').hover(function() {
        $(this).show();
    }, function() {
        $(this).hide();
    });
    $('.dropdownitem').hover(function() {
        $(this).css({'background-color': '#555'});
    }, function() {
        $(this).css({'background-color': '#333'});
    });

    /* Links */
    $('.blueheaderlink').hover(function() {
        $(this).css({'color': '#0075cb'});
    }, function() {
        $(this).css({'color': '#005fa3'});
    });
    $('.greyheaderlink').hover(function() {
        $(this).css('color', '#333');
    }, function() {
        $(this).css('color', 'grey');
    });

    /* Footer */
    $('.creditblue').hover(function() {
        $(this).css({'color': '#0075cb'});
    }, function() {
        $(this).css({'color': '#005fa3'});
    });
    $('.creditgrey').hover(function() {
        $(this).css({'color': 'black'});
    }, function() {
        $(this).css({'color': 'grey'});
    });

    /* Events */
    $('.event-name').hover(function() {
        $(this).css({'color': 'grey'});
    }, function() {
        $(this).css({'color': 'black'});
    });
    $('.tab').click(function() {
        $('.tab').css({'color': 'grey'});
        $(this).css({'color': 'white'});
    });
    $('#panels a').click(function(event) {
        var panel_id = $(this).attr('href');
        $('.panel').hide();
        event.preventDefault();
        $(panel_id).show();
    });

    /* Officers */
    $('.photoone').hover(function() {
        $(this).next().css({'z-index': '3'});
        $(this).next().fadeIn(400);
    }, function() {
    });
    $('.phototwo').hover(function() {
    }, function() {
        $(this).stop().fadeOut(400);
    });

});
