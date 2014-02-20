#!/usr/bin/python
from datetime import datetime
from getopt import getopt, GetoptError
import json
import os
from subprocess import Popen, PIPE
import sys
from tempfile import NamedTemporaryFile


SAVEDIR = "fragments/"
GENERATOR = "mop/build/fragments"
REPODIR = "mop/data/fragments/"
DEFAULT_REPO = "lipids"
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
    lgf += "%s\t%s\t%s\t\n" % (bond["a1"], bond["a2"], i)
  return lgf


def generate_fragments(lgf, repo, shell, outfile, atom_ids):
  repo_path = os.path.normpath("%s/%s" % (REPODIR, repo))
  molecules = []
  with NamedTemporaryFile() as fp:
    fp.write(lgf)
    fp.seek(0)

    for file in os.listdir(repo_path):
      name, ext = os.path.splitext(file)
      if ext == ".lgf":
        mf = generate_molecule_fragments(
          name, "%s/%s" % (repo_path, file), shell, fp.name
        )
        if len(mf["fragments"]) > 0:
          molecules.append(mf)

  found_ids = set()
  for molecule in molecules:
    for fragment in molecule["fragments"]:
      for pair in fragment["pairs"]:
        found_ids.add(pair["id1"])

  missing_atoms = set(atom_ids) - found_ids
  res = json.dumps({
    "molecules": molecules,
    "missing_atoms": list(missing_atoms)
  }, default=(lambda o: o.__dict__))
  outpath = os.path.normpath("%s/%s" % (SAVEDIR, outfile))
  with open(outpath, "w") as fp:
    fp.write(res)

  return {'off': outfile, 'missing_atoms': list(missing_atoms)}


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
    return json.loads(out)
  except ValueError as e:
    raise ValidationError("Generator returned invalid JSON: %s" % e)


def main(argv):
  repo = DEFAULT_REPO
  shell = DEFAULT_SHELL_SIZE

  ffid = datetime.now().strftime("%Y%m%d%H%M%S%f")
  while os.path.exists("%s/%s.off" % (SAVEDIR, ffid)):
    ffid = str(int(ffid) - 1)
  outfile = "%s.off" % ffid

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
      repo_path = os.path.normpath("%s/%s" % (REPODIR, rp))
      if os.path.exists(repo_path):
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
      op = os.path.normpath("%s/%s" % (SAVEDIR, v))
      dir, _ = os.path.split(op)
      if os.path.exists(dir):
        outfile = v
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
  atom_ids = map(lambda a: a["id"], jd["molecule"]["atoms"])

  out = generate_fragments(lgf, repo, shell, outfile, atom_ids)
  print json.dumps(out, default=lambda o: o.__dict__)


if __name__ == "__main__":
  try:
    main(sys.argv)
  except Exception as e:
    print json.dumps({"error": "Invalid query: %s" % e})
