from django.core.urlresolvers import reverse
from django.http import HttpResponseNotAllowed, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from lightshowmaker.models import Show
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
    return render(request, 'index.html', {'shows': Show.objects.all(), 'current_show': Show.objects.get(id=show_id) if show_id else None})

@csrf_exempt
@return_json
def show(request, show_id=None):
    if request.method == 'POST':
        if show_id:
            show = Show.objects.get(id=show_id)
            show.name = request.POST['name']
            show.save()
        else:
            show = Show.objects.create(name=request.POST['name'])
    
        return {'redirect': reverse('show', args=(show.id,))}
    
    return index(request, show_id)

@csrf_except
def real_time(request, show_id):
    import zigbee
    import socket
    if request.method == 'POST':
        sock = socket.socket(socket.AF_XBEE, socket.SOCK_DGRAM, socket.XBS_PROT_TRANSPORT)
        show = Show.objects.get(id=show_id)
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
            
    