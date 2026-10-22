"""Tiny notebook builder/executor so the notebooks in this repo are generated from plain Python and run
without Jupyter installed. Each notebook is saved as a normal .ipynb with outputs (text, tables, figures)."""
import ast
import base64
import contextlib
import io
import json
import sys
import traceback

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def _src(s):
    lines = s.strip("\n").split("\n")
    return [l + "\n" for l in lines[:-1]] + [lines[-1]]


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": _src(text)}


def run_cell(code, ns, count):
    outputs = []
    buf = io.StringIO()
    result = None
    try:
        tree = ast.parse(code)
        last = None
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last = ast.Expression(tree.body.pop().value)
        with contextlib.redirect_stdout(buf):
            exec(compile(tree, "<cell>", "exec"), ns)
            if last is not None:
                result = eval(compile(last, "<cell>", "eval"), ns)
    except Exception:
        buf.write(traceback.format_exc())
        sys.stderr.write(traceback.format_exc())
        raise
    if buf.getvalue():
        outputs.append({"output_type": "stream", "name": "stdout", "text": buf.getvalue().splitlines(True)})
    if result is not None:
        data = {"text/plain": repr(result).splitlines(True)}
        if hasattr(result, "to_html"):
            data["text/html"] = result.to_html(max_rows=60).splitlines(True)
            data["text/plain"] = result.to_string(max_rows=60).splitlines(True)
        outputs.append({"output_type": "execute_result", "execution_count": count, "metadata": {}, "data": data})
    for num in plt.get_fignums():
        fig = plt.figure(num)
        b = io.BytesIO()
        fig.savefig(b, format="png", dpi=110, bbox_inches="tight")
        outputs.append({"output_type": "display_data", "metadata": {}, "data": {"image/png": base64.b64encode(b.getvalue()).decode(), "text/plain": ["<Figure>"]}})
    plt.close("all")
    return outputs


def build(path, cells, ns):
    nb_cells, count = [], 0
    for kind, text in cells:
        if kind == "md":
            nb_cells.append(md(text))
        else:
            count += 1
            outs = run_cell(text, ns, count)
            nb_cells.append({"cell_type": "code", "metadata": {}, "execution_count": count, "source": _src(text), "outputs": outs})
    nb = {"cells": nb_cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                          "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 4}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("wrote", path, "cells:", len(nb_cells))


def insert_after(cells, anchor, text):
    """Insert a markdown cell after the first code cell containing `anchor` (used for written findings)."""
    for i, (k, t) in enumerate(cells):
        if k == "code" and anchor in t:
            cells.insert(i + 1, ("md", text)); return
    raise KeyError(anchor)
