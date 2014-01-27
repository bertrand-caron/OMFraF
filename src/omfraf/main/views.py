import json as simplejson
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from omfraf.main import settings
from util import get_charges, generate_fragments

@csrf_exempt
def index(request):
  if request.method != 'POST':
    raise Http404

  params = request.POST.dict()
  if 'csrfmiddlewaretoken' in params:
    params.pop('csrfmiddlewaretoken')

  charges = get_charges(params)
  charges.update({'version': settings.VERSION})
  return HttpResponse(
    simplejson.dumps(charges, indent=2, default=(lambda o: o.__dict__)),
    mimetype="application/json"
  )

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

def test(request):
  return render(request, 'test.html')
