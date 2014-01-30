import json
import os
import sys


FRAGMENTDIR = "fragments/"


class ValidationError(Exception):
  pass

class LoadError(Exception):
  pass


class Fragment:
  def __init__(self, atb_id):
    self.atb_id = atb_id
    self.atoms = []

  def add_atom(self, id, charge, other_id):
    self.atoms.append(Atom(id, charge, other_id))

  @property
  def __dict__(self):
    return {
      'atb_id': self.atb_id,
      'atoms': map(lambda a: a.__dict__, self.atoms)
    }


class Atom:
  def __init__(self, id, charge, other_id):
    self.id = id
    self.charge = charge
    self.other_id = other_id

  @property
  def __dict__(self):
    return {
      'id': self.id,
      'charge': self.charge,
      'other_id': self.other_id
    }


def load_off(off_name):
  if not os.path.exists(off_name):
    raise LoadError("Could not find fragment file %s" % off_name)

  with open(off_name, 'r') as fp:
    data = fp.read()

  try:
    return json.loads(data)
  except ValueError as e:
    raise LoadError("Invalid fragment file: %s" % e)

def get_fragments(off_name, needle):
  off = load_off(off_name)
  fragments = []
  for molecule in off["molecules"]:
    for fragment in molecule["fragments"]:
      if not "pairs" in fragment:
        continue

      aids = map(lambda p: p["id1"], fragment["pairs"])
      match = True
      for aid in needle:
        if not aid in aids:
          match = False
          break
      if match:
        frag = Fragment(molecule["atb_id"])
        for pair in fragment["pairs"]:
          frag.add_atom(pair["id1"], pair["charge"], pair["id2"])
        fragments.append(frag)
  return fragments

def find_fragments(args):
  try:
    data = json.loads(args)
  except ValueError as e:
    return {'error': "Query not in JSON format: %s" % e}

  try:
    validate_query(data)
  except ValidationError as e:
    return {'error': "Invalid query: %s" % e}

  # This is safe now, as all has been validated
  off_name = data["off"]
  needle = data["needle"]

  try:
    fragments = get_fragments(off_name, needle)
  except LoadError as e:
    return {'error': "Could not load fragments: %s" % e}

  return {'fragments': fragments}

def validate_query(data):
  if not 'off' in data or len(data['off']) == 0:
    raise ValidationError("OFF not set")
  elif not 'needle' in data or len(data['needle']) == 0:
    raise ValidationError("Needle not set")


if __name__ == "__main__":
  result = find_fragments(sys.argv[1])
  print json.dumps(result, default=lambda o: o.__dict__)
