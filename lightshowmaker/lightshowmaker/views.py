from django.core.urlresolvers import reverse
from django.http import HttpResponseNotAllowed, HttpResponse
from django.shortcuts import render, redirect
from lightshowmaker.models import Show
import json
from django.views.decorators.csrf import csrf_exempt

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
