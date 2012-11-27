$(function(){
    if ($('div#body').length) $('div#body').css('height', $(window).height() - $('div#body').position().top);
})
$(window).on('resize', function(){
    $('div#body').css('height', $(window).height() - $('div#body').position().top);
})

$('a#add-show').on('click', function(e){
    e.preventDefault();
    var showName = window.prompt('Name your new show:');
    if (showName == null) return;
    $.ajax({
        url: '/show/',
        type: 'POST',
        data: {'name': showName},
        dataType: 'json',
        success: function(data, status, xhr){
            window.location=data.redirect;
        }
    });
});

$('#add-lights').on('click', function(e){
    if ($(this).hasClass('active')) $('div#body').removeClass('add-lights');
    else $('div#body').addClass('add-lights');
})
$('#show-numbers').on('click', function(e){
    if ($(this).hasClass('active')) $('div#body').removeClass('show-numbers');
    else $('div#body').addClass('show-numbers');
})

$('div#body').on('click', function(e){
    e.preventDefault()
    if (!$('div#body').hasClass('add-lights')) return
    var nextNumber = $('div#body').data('nextNumber')
    $('div#body').data('nextNumber', nextNumber += 1);
    $('div#body').append($('<div class="light"><span>' + nextNumber +'</span></div>').css({'top': e.pageY - $('div#body').position().top, 'left': e.pageX}))
})

$('div#body').on('click', '.light', function(e){
    if ($('div#body').hasClass('add-lights')) return;
    $(e.target).spectrum({
        color: $(e.target).css('background-color'), 
        showInput: true,
        //showAlpha: true,
        showPalette: true,
        //showSelectionPalette: true,
        localStorageKey: 'lightshowmaker.colors',
        clickoutFiresChange: true,
        showInitial: true,
        preferredFormat: 'hex',
        change: function(color){
            $(e.target).css('background-color', color.toHexString());
            console.log(color)
        }
    });
})

$('div#body').on('mousedown', '.light', function(down_event){
    //down_event.preventDefault();
    if ($('div#body').hasClass('add-lights')) return;
    
    var light = $(down_event.target);
    $('div#body').on('mousemove.lightshowmaker.move-light', function(move_event){
    //    move_event.preventDefault();
        light.css({'top': move_event.pageY - $('div#body').position().top, 'left': move_event.pageX})
    })
    $('div#body').on('mouseup', function(up_event){
    //    up_event.preventDefault();
        $('div#body').off('mousemove.lightshowmaker.move-light')
    })
});

$('#save').on('click', function(e){
    var $this = $(this).button('loading');
    e.preventDefault()
    var lights = [];
    for (var i=0; i < $('.light').length; i++){
        var light = $($('.light')[i]);
        var color = light.css('background-color').match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
        lights.push({
            'number': parseInt(light.text()),
            'y': parseInt(light.css('top')),
            'x': parseInt(light.css('left')),
            'red': parseInt(color[1]),
            'green': parseInt(color[2]),
            'blue': parseInt(color[3])
        });
    };
    console.log(lights)
    
    $.ajax({
        url: '/show/' + $('div#body').data('showId') + '/lights/',
        type: 'POST',
        data: {'data': JSON.stringify({'lights': lights})},
        success: function(data, status, xhr){
            $this.button('reset');
        }
    });
});
