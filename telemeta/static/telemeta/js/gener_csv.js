/**
 * Created by crem on 24/05/16.
 */


$(function () {
    
    if (filename != null) {
        window.onbeforeunload = function () {return "";}
    
        $(window).on('unload', function () {
            $.get(window.location.pathname+'?quit=1&file='+filename);
        });
    }
});