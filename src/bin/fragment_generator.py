#!/usr/bin/python
from datetime import datetime
from getopt import getopt, GetoptError
import json
import os
from subprocess import Popen, PIPE
import sys
from tempfile import NamedTemporaryFile


GENERATOR = "mop/build/fragments"
DEFAULT_REPO = "mop/data/fragments/lipids/"
DEFAULT_SHELL_SIZE = 1


class ValidationError(Exception):
  pass


def molecule_to_lgf(molecule):
  lgf = ""
  lgf += atoms_to_lgf(molecule["atoms"])
  lgf += bonds_to_lgf(molecule["bonds"])
  return lgf

def atoms_to_lgf(atoms):
  lgf = "@nodes\n"
  lgf += "partial_charge\tlabel\tlabel2\tatomType\tcoordX\tcoordY\t" + \
      "coordZ\tinitColor\t\n"
  for atom in atoms:
    lgf += "0\t%s\tX\t%s\t0\t0\t0\t0\t\n" % (atom["id"], atom["type"])
  return lgf

def bonds_to_lgf(bonds):
  lgf = "@edges\n"
  lgf += "\t\tlabel\n"
  for i, bond in enumerate(bonds):
    lgf += "%s\t%s\t%s\t\n" % (i + 1, bond["a1"], bond["a2"])
  return lgf


def generate_fragments(lgf, repo, shell, outfile):
  molecules = []
  with NamedTemporaryFile() as fp:
    fp.write(lgf)
    fp.seek(0)

    for file in os.listdir(repo):
      name, ext = os.path.splitext(file)
      if ext == ".lgf":
        molecules.append(
          generate_molecule_fragments(
            name, "%s/%s" % (repo, file), shell, fp.name
          )
        )

  res = json.dumps({"molecules": molecules}, default=(lambda o: o.__dict__))
  with open(outfile, "w") as fp:
    fp.write(res)

  return {'off': outfile}


def generate_molecule_fragments(molid, molfile, shell, infile):
  p = Popen(
    "%s -s %s -atb_id %s %s %s" % (GENERATOR, shell, molid, infile, molfile),
    shell=True,
    stdout=PIPE,
    stderr=PIPE
  )

  out, err = p.communicate()
  if len(err) > 0:
    raise ValidationError(err)

  try:
    # Broken! return json.loads(out)
    return out
  except ValueError as e:
    raise ValidationError("Generator returned invalid JSON: %s" % e)


def main(argv):
  repo = DEFAULT_REPO
  shell = DEFAULT_SHELL_SIZE

  ffid = datetime.now().strftime("%Y%m%d%H%M%S%f")
  while os.path.exists("fragments/%s.off" % ffid):
    ffid = str(int(ffid) - 1)
  outfile = "fragments/%s.off" % ffid

  try:
    opts, args = getopt(
      argv[1:],
      "r:s:o:",
      ["repository=", "shell_size=", "ofile="]
    )
  except (GetoptError, IndexError) as e:
    raise ValidationError("Invalid script invocation: %s" % e)

  for o, v in opts:
    if o in ("-r", "--repository"):
      rp = os.path.normpath(v)
      if os.path.exists(rp):
        repo = rp
      else:
        raise ValidationError("Provided repository does not exist")
    elif o in ("-s", "--shell_size"):
      try:
        shell = int(v)
        if shell < 1:
          raise ValidationError("Shell size needs to be a positive integer")
      except ValueError as e:
        raise ValidationError("Shell size needs to be an integer")
    elif o in ("-o", "--ofile"):
      op = os.path.normpath(v)
      dir, _ = os.path.split(op)
      if os.path.exists(dir):
        outfile = op
      else:
        raise ValidationError("Output folder does not exist")

  try:
    data = args[0]
    jd = json.loads(data)
  except IndexError as e:
    raise ValidationError("Invalid script invocation: JSON query not set")
  except ValueError as e:
    raise ValidationError("JSON query is invalid: %s" % e)

  lgf = molecule_to_lgf(jd["molecule"])

  out = generate_fragments(lgf, repo, shell, outfile)
  print json.dumps(out, default=lambda o: o.__dict__)


if __name__ == "__main__":
  try:
    main(sys.argv)
  except Exception as e:
    print json.dumps({"error": "Invalid query: %s" % e})
