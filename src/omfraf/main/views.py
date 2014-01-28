import json as simplejson
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from omfraf.main import settings
from util import generate_fragments, load_fragments


def index(request):
  return render(request, 'index.html')

@csrf_exempt
def generate(request):
  if request.method != 'POST':
    raise Http404

  params = request.POST.dict()
  if 'csrfmiddlewaretoken' in params:
    params.pop('csrfmiddlewaretoken')

  ack = generate_fragments(params)
  ack.update({'version': settings.VERSION})
  return HttpResponse(
    simplejson.dumps(ack, indent=2, default=(lambda o: o.__dict__)),
    mimetype="application/json"
  )

@csrf_exempt
def load(request):
  if request.method != 'POST':
    raise Http404

  params = request.POST.dict()
  if 'csrfmiddlewaretoken' in params:
    params.pop('csrfmiddlewaretoken')

  fragments = load_fragments(params)
  fragments.update({'version': settings.VERSION})
  return HttpResponse(
    simplejson.dumps(fragments, indent=2, default=(lambda o: o.__dict__)),
    mimetype="application/json"
  )
