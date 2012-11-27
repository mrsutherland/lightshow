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
        context['next_number'] = context['lights'].aggregate(Max('number')).values()[0] + 1
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
def lights(request, show_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    show = get_object_or_404(Show, id=show_id)
    
    data = json.loads(request.POST['data'])
    lights = data['lights']
    
    Lightbulb.objects.filter(strand__show = show).all().delete()
    for light in lights:
        red = round(light['red'] / 16.0)
        green = round(light['green'] / 16.0)
        blue = round(light['blue'] / 16.0)
        
        bulb = Lightbulb.objects.create(strand=show.strands.all()[0], number = light['number'], x=light['x'], y=light['y'])
        BulbColor.objects.create(lightbulb=bulb, red=red, green=green, blue=blue, frame=1, brightness=511)
    return HttpResponse()

@csrf_exempt
def real_time(request, show_id):
    import zigbee
    import socket
    if request.method == 'POST':
        sock = socket.socket(socket.AF_XBEE, socket.SOCK_DGRAM, socket.XBS_PROT_TRANSPORT)
        sock.bind(('', 0x15, 0, 0))
        show = get_object_or_404(Show, id=show_id)
        for strand in show.strands:
            leds = []
            for lightbulb in strand.lightbulbs.order('number'):
                color = lightbulb.colors[0]
                # color order - blue, green, red, extra data
                extra = 0
                leds.append(struct.pack('<BBBB', lightbulb.number, 
                                        color.brightness, 
                                        ((color.blue & 0xF) << 4) + (color.green & 0xF), 
                                        ((color.red & 0xF) << 4) + (extra & 0xF)))
            for led in leds:
                sock.sendto(led, ('[00:13:A2:00:40:5E:0F:39]!'.lower(), 0x15, 0x1ed5, 0x11ed))
                time.sleep(0.01)
        sock.close()

    else:
        return HttpResponseNotAllowed(['POST'])
