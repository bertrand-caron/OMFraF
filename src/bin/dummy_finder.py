import json
from random import random, randint
import sys


class Fragment:
  def __init__(self, main_id, molecule):
    self.atoms = [Atom(main_id)]

    max = randint(1, 5)
    for bond in molecule['bonds']:
      if bond['atom1'] == main_id:
        self.atoms.append(Atom(bond['atom2']))
      elif bond['atom2'] == main_id:
        self.atoms.append(Atom(bond['atom1']))
      
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
  def __init__(self, id):
    self.id = id
    self.charge = random()

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
      fragments.append(Fragment(data['needle'][0], data['molecule']))
    result = {'fragments': fragments}
    print json.dumps(result, default=lambda o: o.__dict__)
  except:
    print json.dumps({'error': "Invalid query"})
