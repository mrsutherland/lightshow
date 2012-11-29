function change(color, mute){
    var step = $('#slider').slider('value');
    var colors = $(this).data('colors')[step]
    colors.red = Math.round(color.toRgb().r / 17);
    colors.green = Math.round(color.toRgb().g / 17);
    colors.blue = Math.round(color.toRgb().b / 17);
    colors.alpha = Math.round(color.toRgb().a * 255);
    colors.color = 'rgba(' + colors.red * 17 + ',' + colors.green * 17 + ',' + colors.blue * 17 + ',' + colors.alpha / 255.0 + ')';
    $(this).css('background-color', colors.color);
    
    if ($('#live').hasClass('active') && !mute){
        $('#live').button('loading');
        $.ajax({
            url: '/show/' + $('div#body').data('showId') + '/real_time/',
            type: 'POST',
            data: {'data': JSON.stringify({'steps': 1, 'lights': [{'number': $(this).data('number'), 'colors': [colors]}]})},
            success: function(data, status, xhr){
                $('#live').button('reset');
            },
            error: function(data, status, xhr){
                window.alert('Error!');
                $('#live').button('reset');
            },
        })   
    };
}

var spectrumData = {
    showInput: true,
    showAlpha: true,
    showPalette: true,
    localStorageKey: 'lightshowmaker.colors',
    clickoutFiresChange: true,
    preferredFormat: 'hex',
    showButtons: false,
    beforeShow: function(){
        return $('body').hasClass('change-colors');
    },
    show: function(){
        $(this).spectrum('set', $(this).data('colors')[$('#slider').slider('option', 'value')].color);
    },
    move: function(color){
        var red = Math.round(color.toRgb().r / 17)
        var green = Math.round(color.toRgb().g / 17)
        var blue =  Math.round(color.toRgb().b / 17)
        var alpha = Math.round(color.toRgb().a * 255);
        $(this).spectrum('set', 'rgba(' + red * 17 + ',' + green * 17 + ',' + blue * 17 + ',' + alpha  / 255.0 + ')');
        change.apply(this, [color]);
    },
    change: change,
}

function play_step(){
    var value = $('#slider').slider('option', 'value')
    if (value == $('#slider').slider('option', 'steps') - 1) value = 0;
    else value += 1;
    $('#slider').slider('option', 'value', value);
}

$(function(){
    if ($('div#body').length) $('div#body').css('height', $(window).height() - $('div#body').position().top);
    
    var stepCount = $('div#body').data('stepCount');
    $('div#slider').slider({
        animate: 'fast',
        min: 0,
        max: stepCount - 1,
        steps: stepCount,
        create: function(event, ui){
            $(this).find('a').html('0');
        },
        slide: function(event, ui){
            $(this).find('a').html(ui.value);
        },
        change: function(event, ui){ // On slider change, either manual or by code
            $(this).find('a').html(ui.value);
            
            var lights = [];
            for (var i=0; i<$('.light').length; i++){
                var light = $($('.light')[i]);
                light.css('background-color', light.data('colors')[ui.value].color);
                var current = light.data('colors')[ui.value];
                var previous = light.data('colors')[$(this).data('previousValue')];
                if ($('#live').hasClass('active') && (current.red != previous.red || current.green != previous.green || current.blue != previous.blue || current.brightness != previous.brightness)){ // only push changes
                    lights.push({'colors': [light.data('colors')[ui.value]], 'number': light.data('number')});
                }
            };
            
            if ($('#live').hasClass('active') && lights.length > 0){
                $('#live').button('loading');
                $.ajax({
                    url: '/show/' + $('div#body').data('showId') + '/real_time/',
                    type: 'POST',
                    data: {'data': JSON.stringify({'steps': 1, 'lights': lights})},
                    success: function(data, status, xhr){
                        $('#live').button('reset');
                    },
                    error: function(data, status, xhr){
                        window.alert('Error!');
                        $('#live').button('reset');
                    },

                })
            };
            $(this).data('previousValue', ui.value);
        }
    });
    
    $('.light').spectrum(spectrumData).off('click.spectrum') // set up light chooser
 
    $(window).on('resize', function(){ // set up window resizing
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
            },
            error: function(data, status, xhr){
                window.alert('Error!');
            },
        });
    });
    
    $('a#change-steps').on('click', function(e){
        e.preventDefault();
        var stepCount = window.prompt('New step count (extra steps will be deleted!):', $('#slider').slider('option', 'steps'));
        if (stepCount == null) return;
        stepCount = parseInt(stepCount);
        $('#slider').slider('option', 'max', stepCount - 1);
        $('#slider').slider('option', 'steps', stepCount);
        
        for (var i=0; i<$('.light').length; i++){
            var light = $($('.light')[i]);
            var colors = light.data('colors')
            if (colors.length > stepCount) {
                light.data('colors', colors.slice(0, stepCount))
                if ($('#slider').slider('option', 'value') > stepCount - 1)
                    $('#slider').slider('option', 'value', stepCount-1); // Move slider to new end
            }
            else if (colors.length < stepCount){
                var lastColor = colors.slice(-1)[0];
                var addLength = stepCount - colors.length;
                for (var j=0; j < addLength; j++){
                    colors.push($.extend({}, lastColor));
                }
            }
        }
              
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
            },
            error: function(data, status, xhr){
                window.alert('Error!');
            },

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
            },
            error: function(data, status, xhr){
                window.alert('Error!');
            },

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
    
    // Add lights
    $('div#body').on('click', function(e){
        e.preventDefault()
        if (!$('body').hasClass('add-lights')) return;
        
        for (var nextNumber = 0; nextNumber<10000; nextNumber++){ // There will never be more than 60something lights
            if ($('.light[data-number="' + nextNumber + '"]').length == 0) break; //TODO: STRAND: this will need some extra logic
        }
                
        var colors = [];
        for (var i=0; i<$('#slider').slider('option', 'steps'); i++) {
            colors.push({'red': 15, 'green': 15, 'blue': 15, 'alpha': 255, 'color': 'rgba(255,255,255,1.0)'});
        }
        
        $('div#body').append($('<div class="light" data-number="' + nextNumber + '"><span>' + nextNumber +'</span></div>')
                .css({'top': e.pageY - $('div#body').position().top, 'left': e.pageX})
                .data({'colors': colors, 'number': nextNumber})
                .spectrum(spectrumData).off('click.spectrum'));
        
        if ($('#live').hasClass('active')){
            $('#live').button('loading');
            $.ajax({
                url: '/show/' + $('div#body').data('showId') + '/real_time/',
                type: 'POST',
                data: {'data': JSON.stringify({'steps': 1, 'lights': [{'number': nextNumber, 'colors': [colors[0]]}]})},
                success: function(data, status, xhr){
                    $('#live').button('reset');
                },
                error: function(data, status, xhr){
                    window.alert('Error!');
                    $('#live').button('reset');
                },

            })   
        };
    })
    
    // Delete lights / Change colors
    $('div#body').on('click', '.light', function(e){
        var $this = $(e.target).is('.light') ? $(e.target) : $(e.target).parents('.light');
        if ($('body').hasClass('delete-lights')){
            e.preventDefault();
            $this.remove();
        }
        else if ($('body').hasClass('change-colors')){
            $this.spectrum('toggle');
            e.stopPropagation(); // I don't know why but this is absolutely needed
        }   
    })
    
    // Move Lights
    $('div#body').on('mousedown', '.light', function(down_event){
        if (!$('body').hasClass('move-lights')) return;
        down_event.preventDefault();
        
        var light = $(down_event.target).is('.light') ? $(down_event.target) : $(down_event.target).parents('.light');
        
        $('div#body').on('mousemove.lightshowmaker.move-light', function(move_event){
            move_event.preventDefault();
            light.css({'top': move_event.pageY - $('div#body').position().top, 'left': move_event.pageX})
        })
        $('div#body').on('mouseup', function(up_event){
            up_event.preventDefault();
            $('div#body').off('mousemove.lightshowmaker.move-light')
        })
    });
    
    // Rewind/FF
    $('#rewind').on('click', function(e){
        var current = $('#slider').slider('option', 'value');
        if (current == 0) var next = $('#slider').slider('option', 'steps') - 1;
        else var next = current - 1;
        $('#slider').slider('option', 'value', next);
    });
    
    $('#fast-forward').on('click', function(e){
        var current = $('#slider').slider('option', 'value');
        if (current == $('#slider').slider('option', 'steps') - 1) var next = 0;
        else var next = current + 1;
        $('#slider').slider('option', 'value', next);
    });
    
    // Play
    $('#play').on('click', function(e){
        if ($(this).hasClass('playing')){
            $(this).button('reset').removeClass('playing');
            window.clearInterval($(this).data('intervalId'));
        }
        else {
            $(this).button('playing').addClass('playing');
            $(this).data('intervalId', window.setInterval(play_step, 500));
        }
    });
    

    function assemble_data(start, end){
        var lights = [];
        for (var i=0; i < $('.light').length; i++){
            var light = $($('.light')[i]);
            lights.push({
                'number': light.data('number'),
                'y': parseInt(light.css('top')),
                'x': parseInt(light.css('left')),
                'colors': light.data('colors').slice(start, end),
            });
        };
        
        return {'data': JSON.stringify({'lights': lights, 'steps': end - start})};
    }
    
    $('#save').on('click', function(e){
        var $this = $(this).button('loading');
        e.preventDefault()
        $.ajax({
            url: '/show/' + $('div#body').data('showId') + '/lights/',
            type: 'POST',
            data: assemble_data(0, $('#slider').slider('option', 'steps')),
            success: function(data, status, xhr){
                $this.button('reset');
            },
            error: function(data, status, xhr){
                window.alert('Error!');
                $this.button('reset');
            },

        });
    });
    
    function make_it_spin(e, start, end){
        var $this = $(this).button('loading');
        e.preventDefault()
        $.ajax({
            url: '/show/' + $('div#body').data('showId') + '/real_time/',
            type: 'POST',
            data: assemble_data(start, end),
            success: function(data, status, xhr){
                $this.button('reset');
            },
            error: function(data, status, xhr){
                window.alert('Error!');
                $this.button('reset');
            },

        })
     };

    $('#make-it-spin').on('click', function(e){
        make_it_spin(e, 0, $('#slider').slider('option', 'steps'));
    });
    $('#live').on('click', function(e){
        if (!$('#live').hasClass('active')) make_it_spin(e, $('#slider').slider('option', 'value'), $('#slider').slider('option', 'value') + 1); // deal with open end range
    });
    
});