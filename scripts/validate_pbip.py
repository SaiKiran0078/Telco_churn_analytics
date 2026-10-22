"""Validate every JSON file of a .pbip project against Microsoft's published schemas (local clone of microsoft/json-schemas).
usage: validate_pbip.py <project_dir> <schemas_root>"""
import json, sys, os
from pathlib import Path
import jsonschema
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7

proj, root = Path(sys.argv[1]), Path(sys.argv[2])
BASE = "https://developer.microsoft.com/json-schemas/"

def retrieve(uri):
    if not uri.startswith(BASE):
        raise LookupError(uri)
    p = root / uri[len(BASE):]
    if not p.is_file():
        raise LookupError(uri)
    return Resource.from_contents(json.loads(p.read_text(encoding="utf-8")), default_specification=DRAFT7)

registry = Registry(retrieve=retrieve)
n = bad = 0
for f in sorted(proj.rglob("*")):
    if f.suffix not in (".json", ".pbir", ".pbip", ".pbism") and f.name != ".platform":
        continue
    if "StaticResources" in f.parts and "SharedResources" in f.parts:
        continue
    d = json.loads(f.read_text(encoding="utf-8"))
    sch = d.get("$schema") if isinstance(d, dict) else None
    if not sch:
        print("no $schema:", f.relative_to(proj)); continue
    n += 1
    try:
        schema = retrieve(sch).contents
        v = jsonschema.Draft7Validator(schema, registry=registry)
        errs = sorted(v.iter_errors(d), key=lambda e: list(e.path))
        if errs:
            bad += 1
            print("INVALID:", f.relative_to(proj))
            for e in errs[:4]:
                print("   ", "/".join(map(str, e.path)), "->", e.message[:200])
    except LookupError as ex:
        print("schema not found:", sch, "for", f.relative_to(proj))
print(f"checked {n} files with schemas; invalid: {bad}")
