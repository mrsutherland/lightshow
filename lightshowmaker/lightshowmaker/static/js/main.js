$(function(){
    $('div#body').css('height', $(window).height() - $('div#body').position().top);
})

$('a#add-show').on('click', function(e){
    e.preventDefault();
    var showName = window.prompt('Name your new show:');
    if (showName == null) return;
    $.ajax({
        'url': '/show/',
        'type': 'POST',
        'data': {'name': showName},
        'dataType': 'json',
        'success': function(data, status, xhr){
            window.location=data.redirect;
        }
    });
});

$('div#body').on('click', function(e){
    if ($('#add-lights').hasClass('active')){
        $('div#body').append($('<div class="light"></div>').css({'top': e.pageY - $('div#body').position().top - 5, 'left': e.pageX - 5}))
    }
})
