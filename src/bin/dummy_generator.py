from copy import copy
from datetime import datetime
import json
from os.path import exists
from random import choice, randint, random
import sys


class Molecule:
  def __init__(self, atb_id, data):
    self.atb_id = atb_id
    candidates = filter((lambda a: a['type'] != 20), data['atoms'])
    candidate_ids = map((lambda a: a['id']), candidates)
    self.fragments = []
    for i in range(randint(1, 10)):
      chc = choice(candidate_ids)
      sel = [chc]
      sel.extend(get_bonded_hydrogen(chc, data))
      self.fragments.append(Fragment(sel, data))

  @property
  def __dict__(self):
    return {
      'atb_id': self.atb_id,
      'fragments': self.fragments
    }

  @property
  def __json__(self):
    return json.dumps(self, default=lambda o: o.__dict__)

class Fragment:
  def __init__(self, main_ids, molecule):
    self.pairs = []
    atom_ids = copy(main_ids)
    candidates = filter((lambda a: a['type'] != 20), molecule['atoms'])
    candidate_ids = map((lambda a: a['id']), candidates)

    for main_id in main_ids:
      self.pairs.append(Pair(main_id))
      cis = list(set(candidate_ids) - set(atom_ids))
      max = randint(1, 5)
      for bond in molecule['bonds']:
        if bond['a1'] == main_id and bond['a2'] in cis:
          pair = Pair(bond['a2'])
          self.pairs.append(pair)
          atom_ids.append(bond['a2'])

          bhs = pair.get_bonded_hydrogen(molecule)
          self.pairs.extend(bhs)
          atom_ids.extend(map(lambda a: a.id1, bhs))
        elif bond['a2'] == main_id and bond['a1'] in cis:
          pair = Pair(bond['a1'])
          self.pairs.append(pair)
          atom_ids.append(bond['a1'])

          bhs = pair.get_bonded_hydrogen(molecule)
          self.pairs.extend(bhs)
          atom_ids.extend(map(lambda a: a.id1, bhs))

        if len(self.pairs) == max:
          break

  @property
  def __dict__(self):
    return {
      'pairs': self.pairs
    }

  @property
  def __json__(self):
    return json.dumps(self, default=lambda o: o.__dict__)

class Pair:
  def __init__(self, id1, id2=None, charge=None):
    self.id1 = id1
    self.id2 = id2 if id2 != None else id1
    self.charge = charge if charge != None else random()

  def get_bonded_hydrogen(self, molecule):
    hs = filter((lambda a: a['type'] == 20), molecule['atoms'])
    hids = map((lambda a: a['id']), hs)
    bhs = []
    for bond in molecule['bonds']:
      if bond['a1'] == self.id1 and bond['a2'] in hids:
        bhs.append(Pair(bond['a2'], charge=0))
    return bhs

  @property
  def __dict__(self):
    return {
      'id1': self.id1,
      'id2': self.id2,
      'charge': self.charge
    }

  @property
  def __json__(self):
    return json.dumps(self, default=lambda o: o.__dict__)


def get_bonded_hydrogen(atom_id, molecule):
  hs = filter((lambda a: a['type'] == 20), molecule['atoms'])
  hids = map((lambda a: a['id']), hs)
  bhs = []
  for bond in molecule['bonds']:
    if bond['a1'] == atom_id and bond['a2'] in hids:
      bhs.append(bond['a2'])
  return bhs


if __name__ == "__main__":
  try:
    data = json.loads(sys.argv[1])
    molecules = []
    for i in range(randint(0, 10)):
      molecules.append(Molecule("5276", data['molecule']))

    ffid = datetime.now().strftime("%Y%m%d%H%M%S%f")
    while exists("bin/fragments/%s.off" % ffid):
      ffid -= 1

    with open("bin/fragments/%s.off" % ffid, "w") as fp:
      fp.write(json.dumps({'molecules': molecules}, default=lambda o: o.__dict__))

    result = {'ffid': ffid}
    print json.dumps(result, default=lambda o: o.__dict__)
  except Exception as e:
    print json.dumps({'error': "Invalid query: %s" % e})
