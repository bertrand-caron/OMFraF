from django.core.cache import cache
import json
import logging
import omfraf
import os
from subprocess import Popen, PIPE
import re


logger = logging.getLogger('omfraf')

DEFAULTSHELL = 1
DEFAULTREPO = "lipids"
BINDIR = os.path.normpath("%s/../bin/" % os.path.dirname(omfraf.__file__))
REPODIR = os.path.normpath("%s/mop/data/fragments/" % BINDIR)
FRAGMENTSDIR = "%s/fragments" % BINDIR
FRAGMENTGENERATOR = "python fragment_generator.py"
FRAGMENTFINDER = "python fragment_finder.py"


class ValidationError(Exception):
  pass

class GeneratorError(Exception):
  pass

class FinderError(Exception):
  pass


def get_repositories():
  repos = []
  for _, dirs, _ in os.walk(REPODIR):
    repos = dirs
    break

  return {'repos': repos}


def get_atb_outfile(molid, repo=None, shell=None):
  return "%s_%s_%s.off" % (repo or DEFAULTREPO, shell or DEFAULTSHELL, molid)

def generate_fragments(args):
  try:
    validate_args(args)
  except ValidationError as e:
    return {'error': e.message}

  # This is safe now, as all have been validated
  data = args.get("data")
  repo = args.get("repo", None)
  shell_size = args.get("shell", None)

  md = json.loads(data)["molecule"]
  if "molid" in md and md["molid"].isdigit():
    outfile = get_atb_outfile(md["molid"], repo, shell_size)
    off = "%s/%s" % (FRAGMENTSDIR, outfile)
    if os.path.isfile(off):
      with open(off, 'r') as fp:
        try:
          od = json.loads(fp.read())
          return {'off': outfile, 'missing_atoms': od['missing_atoms']}
        except ValueError as e:
          pass

  try:
    ack = store_fragments(data, repo, shell_size)
  except GeneratorError as e:
    return {'error': e.message}

  return ack

def store_fragments(data, repo=None, shell_size=None):
  logger.debug("Storing fragments for: %s" % data)

  md = json.loads(data)["molecule"]
  if "molid" in md and md["molid"].isdigit():
    args = "-o %s" % get_atb_outfile(md["molid"], repo, shell_size)
  else:
    args = ""
  if repo:
    args += " -r %s" % repo
  if shell_size:
    args += " -s %s" % shell_size

  p = Popen(
    "%s %s \'%s\'" % (FRAGMENTGENERATOR, args, data),
    cwd=BINDIR,
    shell=True,
    stdout=PIPE,
    stderr=PIPE
  )

  out, err = p.communicate()
  if len(err) > 0:
    raise GeneratorError(err)

  #logger.debug("FG: %s" % out[:-1])
  try:
    ack = json.loads(out)
  except ValueError as e:
    logger.info(out)
    raise GeneratorError("Generator returned invalid data: (%s)" % e)

  if not 'off' in ack:
    if 'error' in ack:
      e = ack['error']
    else:
      e = "KeyError: 'off'"
    raise GeneratorError("Generator could not store fragments (%s)" % e)

  return ack


def load_fragments(args):
  try:
    validate_args(args)
  except ValidationError as e:
    return {'error': e.message}

  # This is safe now, as all have been validated
  data = args.get("data")

  try:
    fragments = get_fragments(data)
  except FinderError as e:
    return {'error': e.message}

  return fragments


def get_fragments(data):
  logger.debug("Looking for: %s" % data)

  p = Popen(
    "%s \'%s\'" % (FRAGMENTFINDER, data),
    cwd=BINDIR,
    shell=True,
    stdout=PIPE,
    stderr=PIPE
  )

  out, err = p.communicate()
  if len(err) > 0:
    raise FinderError(err)

  #logger.debug("FF: %s" % out[:-1])
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

  return fragments


def validate_args(args):
  data = args.get("data")

  if not data:
    raise ValidationError("Missing query data")

  try:
    _ = json.loads(data)
  except ValueError as e:
    raise ValidationError("Query data not in JSON format (%s)" % e)

  return True
