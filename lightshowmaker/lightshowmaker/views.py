from django.core.urlresolvers import reverse
from django.db.models.aggregates import Max
from django.http import HttpResponseNotAllowed, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from lightshowmaker.models import Show, Lightbulb, Strand, BulbColor
import json
import struct
import time

def return_json(func):

    def _return_json(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, HttpResponse):
            return result
        return HttpResponse(json.dumps(result), content_type='application/json')

    return _return_json

def index(request, show_id=None):
    context = {'shows': Show.objects.all()}
    if show_id:
        show = context['current_show'] = Show.objects.get(id=show_id)
        context['lights'] = Lightbulb.objects.filter(strand__show = show)
    return render(request, 'index.html', context)

@csrf_exempt
@return_json
def show(request, show_id=None):
    if request.method == 'POST':
        if show_id:
            show = get_object_or_404(Show, id=show_id)
            show.name = request.POST['name']
            show.save()
        else:
            show = Show.objects.create(name=request.POST['name'])
            strand = Strand.objects.create(show=show, name='Main', eui64='')
    
        return {'redirect': reverse('show', args=(show.id,))}
    
    return index(request, show_id)

@csrf_exempt
@return_json
def delete_show(request, show_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    show = get_object_or_404(Show, id=show_id)
    show.delete()
    return {'redirect': reverse('index')}

@csrf_exempt
def lights(request, show_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    show = get_object_or_404(Show, id=show_id)
    
    data = json.loads(request.POST['data'])
    
    show.steps = data['steps']
    show.save()
    
    Lightbulb.objects.filter(strand__show = show).all().delete()
    BulbColor.objects.filter(lightbulb__strand__show = show).all().delete()
    
    for light in data['lights']:        
        lightbulb = Lightbulb.objects.create(strand=show.strands.all()[0], number = light['number'], x=light['x'], y=light['y'])
        assert show.steps == len(light['colors']), 'show.steps: %s, number of colors: %s' % (show.steps, len(light['colors']))
        for step, color in enumerate(light['colors']):
            BulbColor.objects.create(lightbulb = lightbulb, step = step, red = color['red'], green=color['green'], blue=color['blue'], brightness=color['alpha'])
            
    return HttpResponse()

@csrf_exempt
def real_time(request, show_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    show = get_object_or_404(Show, id=show_id)
    data = json.loads(request.POST['data'])
    
    #initialize ZigBee side
    import zigbee_leds
    zigbee_leds.initialize()

    for step in xrange(data['steps']):
        leds = []
        for light in data['lights']:
            color = light['colors'][step]
            # color order - blue, green, red, extra data
            extra = 0
            leds.append(struct.pack('<BBBB', light['number'], 
                                    color['alpha'] & 0xFF, 
                                    ((color['blue'] & 0xF) << 4) + (color['green'] & 0xF), 
                                    ((color['red'] & 0xF) << 4) + (extra & 0xF)))
    
        for i in xrange(0, len(leds), 20):
            zigbee_leds.send_leds(''.join(leds[i:i+20]), '[00:13:A2:00:40:5E:0F:39]!'.lower())
            
        if step < data['steps'] - 1:
            time.sleep(1)

    return HttpResponse()
