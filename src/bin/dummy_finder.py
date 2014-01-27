from copy import copy
import json
from random import random, randint
import sys


class Fragment:
  def __init__(self, main_ids, molecule):
    self.atoms = []
    atom_ids = copy(main_ids)
    candidates = filter((lambda a: a['element'] != "H"), molecule['atoms'])
    candidate_ids = map((lambda a: a['id']), candidates)

    for main_id in main_ids:
      self.atoms.append(Atom(main_id))
      cis = list(set(candidate_ids) - set(atom_ids))
      max = randint(1, 5)
      for bond in molecule['bonds']:
        if bond['a1'] == main_id and bond['a2'] in cis:
          atom = Atom(bond['a2'])
          self.atoms.append(atom)
          atom_ids.append(bond['a2'])

          bhs = atom.get_bonded_hydrogen(molecule)
          self.atoms.extend(bhs)
          atom_ids.extend(map(lambda a: a.id, bhs))
        elif bond['a2'] == main_id and bond['a1'] in cis:
          atom = Atom(bond['a1'])
          self.atoms.append(atom)
          atom_ids.append(bond['a1'])

          bhs = atom.get_bonded_hydrogen(molecule)
          self.atoms.extend(bhs)
          atom_ids.extend(map(lambda a: a.id, bhs))

        if len(self.atoms) == max:
          break

  @property
  def __dict__(self):
    return {
      'atoms': self.atoms
    }

  @property
  def __json__(self):
    return json.dumps(self, default=lambda o: o.__dict__)

class Atom:
  def __init__(self, id, charge=None):
    self.id = id
    self.charge = charge if charge != None else random()

  def get_bonded_hydrogen(self, molecule):
    hs = filter((lambda a: a['element'] == "H"), molecule['atoms'])
    hids = map((lambda a: a['id']), hs)
    bhs = []
    for bond in molecule['bonds']:
      if bond['a1'] == self.id and bond['a2'] in hids:
        bhs.append(Atom(bond['a2'], 0))
    return bhs

  @property
  def __dict__(self):
    return {
      'id': self.id,
      'charge': self.charge
    }

  @property
  def __json__(self):
    return json.dumps(self, default=lambda o: o.__dict__)


if __name__ == "__main__":
  try:
    data = json.loads(sys.argv[1])
    fragments = []
    for i in range(randint(0, 10)):
      fragments.append(Fragment(data['needle'], data['molecule']))
    result = {'fragments': fragments}
    print json.dumps(result, default=lambda o: o.__dict__)
  except:
    print json.dumps({'error': "Invalid query"})
