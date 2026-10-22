"""Check that every field a report visual/filter references exists in the semantic model (TMDL)."""
import json, re, sys
from pathlib import Path
proj = Path(sys.argv[1])
sm = next(proj.glob("*.SemanticModel")); rp = next(proj.glob("*.Report"))
def unq(s):
    s = s.strip()
    return s[1:-1].replace("''", "'") if s.startswith("'") else s
model = {}
for f in (sm / "definition" / "tables").glob("*.tmdl"):
    t = None; cols = set(); meas = set()
    for line in f.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^table (.+)$", line)
        if m: t = unq(m.group(1)); continue
        m = re.match(r"^\tcolumn (.+)$", line)
        if m: cols.add(unq(m.group(1))); continue
        m = re.match(r"^\tmeasure (.+?) =", line)
        if m: meas.add(unq(m.group(1)))
    model[t] = (cols, meas)
print("tables:", {k: (len(v[0]), len(v[1])) for k, v in model.items()})
errs = set(); n = 0
def walk(o, aliases, where):
    global n
    if isinstance(o, dict):
        al = dict(aliases)
        for a in o.get("From", []) if isinstance(o.get("From"), list) else []:
            if isinstance(a, dict) and "Name" in a and "Entity" in a: al[a["Name"]] = a["Entity"]
        for kind in ("Column", "Measure", "Hierarchy", "HierarchyLevel"):
            if kind in o and isinstance(o[kind], dict):
                v = o[kind]; ex = v.get("Expression", {}).get("SourceRef", {}); prop = v.get("Property")
                ent = ex.get("Entity") or al.get(ex.get("Source"))
                if ent and prop and kind in ("Column", "Measure"):
                    n += 1
                    if ent not in model: errs.add((where, f"table {ent}"))
                    else:
                        ok = prop in (model[ent][0] if kind == "Column" else model[ent][1])
                        if not ok: errs.add((where, f"{kind} {ent}[{prop}]"))
        for v in o.values(): walk(v, al, where)
    elif isinstance(o, list):
        for v in o: walk(v, aliases, where)
for f in (rp / "definition").rglob("*.json"):
    walk(json.loads(f.read_text(encoding="utf-8")), {}, str(f.relative_to(rp)))
print("field references checked:", n)
for e in sorted(errs): print("MISSING", e)
print("OK: all references resolve" if not errs else f"{len(errs)} problems")
