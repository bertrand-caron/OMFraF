from django.core.cache import cache
import json
import logging
import omfraf
import os
from subprocess import Popen, PIPE
import re


logger = logging.getLogger('omfraf')

BINDIR = os.path.normpath("%s/../bin/" % os.path.dirname(omfraf.__file__))
FRAGMENTGENERATOR = "python dummy_generator.py"
FRAGMENTFINDER = "python fragment_finder.py"


class ValidationError(Exception):
  pass

class GeneratorError(Exception):
  pass

class FinderError(Exception):
  pass

class UnknownElementError(Exception):
  pass

class Molecule:
  def __init__(self):
    self.atoms = []
    self.bonds = []

  def get_atom(self, id):
    for atom in self.atoms:
      if atom.id == id:
        return atom

  def get_atom_bonds(self, atom, type=None):
    if type == None:
      bonds = self.bonds
    else:
      bonds = filter(lambda b: b.type == type, self.bonds)
    return filter(lambda b: b.a1 == atom or b.a2 == atom, bonds)

  def parse(self, data):
    for atom in data["atoms"]:
      self.atoms.append(Atom(self, atom["id"], atom["element"]))

    for bond in data["bonds"]:
      a1 = self.get_atom(bond["a1"])
      a2 = self.get_atom(bond["a2"])
      self.bonds.append(Bond(self, a1, a2, bond["bondType"]))

    return self

  @property
  def __json__(self):
    return {
      "atoms": map(lambda a: a.__json__, self.atoms),
      "bonds": map(lambda b: b.__json__, self.bonds)
    }

class Atom:
  def __init__(self, molecule, id, element):
    self.molecule = molecule
    self.id = id
    self.element = element

  @property
  def type(self):
    bas = self.get_bonded_atoms()
    if self.element == 'C':
      bhs = filter(lambda a: a.element == 'H', bas)
      if len(bhs) == 0:
        return 13
      else:
        return 12
    elif self.element == 'H':
      if bas and bas[0].element == 'C':
        return 20
      else:
        return 21
    elif self.element == 'O':
      if len(filter(lambda a: a.element == 'C', bas)) == len(bas) and \
          len(bas) > 1:
        return 4
      elif len(bas) > 1:
        return 3
      elif bas and len(filter(lambda a: a.element == 'O', \
          bas[0].get_bonded_atoms(2))) > 1:
        return 2
      else:
        return 1
    elif self.element == 'N':
      if len(bas) > 3:
        return 8
      elif len(bas) == 1:
        return 9
      elif len(self.get_bonded_atoms(5)) > 1:
        return 9
      elif len(filter(lambda a: a.element == 'H', bas)) < 2:
        return 6
      else:
        return 7
    elif self.element == 'S':
      if len(bas) > 2:
        return 42
      else:
        return 23
    elif self.element == 'P':
      return 30
    elif self.element == 'Si':
      return 31
    elif self.element == 'F':
      return 32
    elif self.element == 'Cl':
      return 33
    elif self.element == 'Br':
      return 34

    raise UnknownElementError("Encountered element of type %s" % self.element)

  def get_bonded_atoms(self, type=None):
    return map(
      lambda b: b.a2 if b.a1 == self else b.a1,
      self.molecule.get_atom_bonds(self, type)
    )

  @property
  def __json__(self):
    return {
      "id": self.id,
      "type": self.type
    }

class Bond:
  def __init__(self, molecule, a1, a2, type):
    self.molecule = molecule
    self.a1 = a1
    self.a2 = a2
    self.type = type

  @property
  def is_aromatic(self):
    return self.type == 5

  @property
  def __json__(self):
    return {
      "a1": self.a1.id,
      "a2": self.a2.id
    }


def generate_fragments(args):
  try:
    validate_args(args)
  except ValidationError as e:
    return {'error': e.message}

  # This is safe now, as all have been validated
  data = args.get("data")

  try:
    ack = store_fragments(data)
  except GeneratorError as e:
    return {'error': e.message}

  return ack

def fix_element_types(data):
  jd = json.loads(data)
  jd["molecule"] = Molecule().parse(jd["molecule"]).__json__
  return json.dumps(jd)

def store_fragments(data):
  try:
    data = fix_element_types(data)
  except UnknownElementError as e:
    raise GeneratorError("Could not resolve all element types: %s" % e)

  logger.debug("Storing fragments for: %s" % data)

  p = Popen(
    "%s \'%s\'" % (FRAGMENTGENERATOR, data),
    cwd=BINDIR,
    shell=True,
    stdout=PIPE,
    stderr=PIPE
  )

  out, err = p.communicate()
  if len(err) > 0:
    raise GeneratorError(err)

  logger.debug("FG: %s" % out[:-1])
  try:
    ack = json.loads(out)
  except ValueError as e:
    raise GeneratorError("Generator returned invalid data: (%s)" % e)

  if not 'ffid' in ack:
    if 'error' in ack:
      e = ack['error']
    else:
      e = "KeyError: 'ffid'"
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
