$( document ).ready(function() {
    $('#mobile_button').on('click', function(evt){
        const attr = $('#mobile-menu').attr("hidden");
        if( typeof attr !== 'undefined' && attr !== false ){
            $('#mobile-menu').removeAttr("hidden");
        }else{
            $('#mobile-menu').attr("hidden","");
        }
    });
});