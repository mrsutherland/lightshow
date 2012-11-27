function change(color){
    $(this).data('red', Math.round(color.toRgb().r / 17))
    $(this).data('green', Math.round(color.toRgb().g / 17))
    $(this).data('blue', Math.round(color.toRgb().b / 17))
    $(this).css('background-color', color.toRgbString());
}

var spectrumData = {
    showInput: true,
    //showAlpha: true,
    showPalette: true,
    localStorageKey: 'lightshowmaker.colors',
    clickoutFiresChange: true,
    //showInitial: true,
    preferredFormat: 'hex',
    showButtons: false,
    beforeShow: function(){
        return $('body').hasClass('change-colors');
    },
    show: function(){
        $(this).spectrum('set', $(this).css('background-color'));
    },
    move: function(color){
        var red = Math.round(color.toRgb().r / 17)
        var green = Math.round(color.toRgb().g / 17)
        var blue =  Math.round(color.toRgb().b / 17)
        $(this).spectrum('set', 'rgb(' + red * 17 + ',' + green * 17 + ',' + blue * 17 + ')');
        change(color);
    },
    change: change,
}

$(function(){
    if ($('div#body').length) $('div#body').css('height', $(window).height() - $('div#body').position().top);
    
    $('div#slider').slider();

    $('.light').spectrum(spectrumData).off('click.spectrum')

    $(window).on('resize', function(){
        $('div#body').css('height', $(window).height() - $('div#body').position().top);
    })
    
    $('a#add-show').on('click', function(e){
        e.preventDefault();
        var showName = window.prompt('Name your new show (have you saved the current show?!):');
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
    
    $('a#rename-show').on('click', function(e){
        e.preventDefault();
        var showName = window.prompt('Rename your show:');
        if (showName == null) return;
        $.ajax({
            url: '/show/' + $('div#body').data('showId') + '/',
            type: 'POST',
            data: {'name': showName},
            dataType: 'json',
            success: function(data, status, xhr){
                $('.current-show-name').html(showName);
            }
        });
    });
    
    $('a#delete-show').on('click', function(e){
        e.preventDefault();
        var showName = window.confirm('Are you very sure you want to delete this whole show?  There is no going back.');
        if (showName != true) return;
        $.ajax({
            url: '/show/' + $('div#body').data('showId') + '/delete/',
            type: 'POST',
            success: function(data, status, xhr){
                window.location=data.redirect;
            }
        });
    });
    
    $('.btn-group').on('click', '.btn', function(){
        var cls = $(this).attr('id');
        $('body').removeClass('add-lights').removeClass('move-lights').removeClass('delete-lights').removeClass('change-colors').addClass(cls);
    })
    
    $('#show-numbers').on('click', function(e){
        if ($(this).hasClass('active')) $('body').removeClass('show-numbers');
        else $('body').addClass('show-numbers');
    })
    
    $('div#body').on('click', function(e){
        e.preventDefault()
        if (!$('body').hasClass('add-lights')) return;
        var nextNumber = $('div#body').data('nextNumber');
        $('div#body').data('nextNumber', nextNumber += 1);
        $('div#body').append($('<div class="light"><span>' + nextNumber +'</span></div>')
                .css({'top': e.pageY - $('div#body').position().top, 'left': e.pageX})
                .data({'red': 15, 'green': 15, 'blue': 15}))
                .spectrum(spectrumData).off('click.spectrum');
    })
    
    $('div#body').on('click', '.light', function(e){
        var $this = $(e.target).is('.light') ? $(e.target) : $(e.target).parents('.light');
        if ($('body').hasClass('delete-lights')){
            e.preventDefault();
            $this.remove();
        }
        else if ($('body').hasClass('change-colors')){
            $this.spectrum('toggle');
            e.stopPropagation(); // I don't know why but this is absolutely reqd
        }   
    })
    
    $('div#body').on('mousedown', '.light', function(down_event){
        if (!$('body').hasClass('move-lights')) return;
        down_event.preventDefault();
        
        var light = $(down_event.target);
        $('div#body').on('mousemove.lightshowmaker.move-light', function(move_event){
            move_event.preventDefault();
            light.css({'top': move_event.pageY - $('div#body').position().top, 'left': move_event.pageX})
        })
        $('div#body').on('mouseup', function(up_event){
            up_event.preventDefault();
            $('div#body').off('mousemove.lightshowmaker.move-light')
        })
    });
    
    
    function save(e, success){
        var $this = $(this).button('loading');
        e.preventDefault()
        var lights = [];
        for (var i=0; i < $('.light').length; i++){
            var light = $($('.light')[i]);
            console.log(light.data());
            lights.push({
                'number': parseInt(light.text()),
                'y': parseInt(light.css('top')),
                'x': parseInt(light.css('left')),
                'red': light.data('red'),
                'green': light.data('green'),
                'blue': light.data('blue')
            });
        };
        
        $.ajax({
            url: '/show/' + $('div#body').data('showId') + '/lights/',
            type: 'POST',
            data: {'data': JSON.stringify({'lights': lights})},
            success: function(data, status, xhr){
                $this.button('reset');
                if (success) success(e)
            }
        });
    }
    
    $('#save').on('click', save);
    
    $('#real-time').on('click', function(e){
        save(e, function(e){
           var $this = $(this).button('loading');
           $.ajax({
               url: '/show/' + $('div#body').data('showId') + '/real_time/',
               type: 'POST',
               success: function(data, status, xhr){
                   $this.button('reset');
               }
           })
       });
    });
});