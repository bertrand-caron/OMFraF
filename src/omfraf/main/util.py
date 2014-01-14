from django.core.cache import cache
import json
import logging
import os
from subprocess import Popen, PIPE
import re


logger = logging.getLogger('omfraf')

# TODO
if os.name == 'nt':
  FRAGMENTFINDER = "python bin/dummy_finder.py"
else:
  FRAGMENTFINDER = "python bin/dummy_finder.py"


class ValidationError(Exception):
  pass

class FinderError(Exception):
  pass


def get_fragments(data):
  logger.debug("Looking for: %s" % data)
  
  p = Popen(
    "%s \'%s\'" % (FRAGMENTFINDER, data),
    shell=True,
    stdout=PIPE,
    stderr=PIPE
  )
  
  out, err = p.communicate()
  if len(err) > 0:
    raise FinderError(err)

  logger.debug("FF: %s" % out[:-1])
  try:
    fragments = json.loads(out)
  except ValueError as e:
    raise FinderError("Fragment Finder returned invalid data: (%s)" % e)
  
  if not 'fragments' in fragments:
    if 'error' in fragments:
      e = fragments['error']
    else:
      e = "KeyError: 'fragments'"
    raise FinderError("Fragment Finder could not find fragments (%s)" % e)

  return {'fragments': add_bonds(fragments['fragments'], json.loads(data))}

def add_bonds(fragments, data):
  for fragment in fragments:
    fas = map((lambda a: a['id']), fragment['atoms'])
    fragment['bonds'] = []
    for bond in data['molecule']['bonds']:
      if bond['atom1'] in fas and bond['atom2'] in fas:
        fragment['bonds'].append(bond)
  return fragments

def get_charges(args):
  try:
    validate_args(args)
  except ValidationError as e:
    return {'error': e.message}

  # This is safe now, as all have been validated
  data = args.get("data")

#   cachedCharges = cache.get(data)
#   if cachedCharges:
#     return cachedCharges

  try:
    charges = get_fragments(data)
  except FinderError as e:
    return {'error': e.message}

  # Cache for a year (infinitely enough..)
  # cache.set(data, pos, 60 * 60 * 24 * 365)
  return charges

def validate_args(args):
  data = args.get("data")
  
  if not data:
    raise ValidationError("Missing molecule data")
  
  try:
    _ = json.loads(data)
  except ValueError as e:
    raise ValidationError("Molecule data not in JSON format (%s)" % e)
  
  return True
