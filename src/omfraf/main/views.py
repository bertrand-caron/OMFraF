import json as simplejson
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from omfraf.main import settings
from util import get_repositories, generate_fragments, load_fragments, mop_update

def index(request):
  return render(request, 'index.html')

@csrf_exempt
def repos(request):
  repos = get_repositories()
  repos.update({'version': settings.VERSION})
  return HttpResponse(
    simplejson.dumps(repos, indent=2, default=(lambda o: o.__dict__)),
    content_type="application/json"
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
    content_type="application/json"
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
    content_type="application/json"
  )

@never_cache
def update_mop(request):
  out = mop_update()
  return HttpResponse(out)
