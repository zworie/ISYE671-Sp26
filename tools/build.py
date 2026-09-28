#!/usr/bin/env python3
"""Build the ISYE 671 course website.

Converts every Markdown file under lectures/, homework/, project/, exercises/
(plus syllabus.md) into a styled HTML page, and generates index.html from the
MODULES table below. Re-run after adding or editing material:

    pip install pypandoc_binary   # once; provides pandoc
    python3 tools/build.py

The script refuses to build if a file that looks like a solution or an exam is
present in the repository (see FORBIDDEN).
"""

import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "zworie/ISYE671-Sp26"
BRANCH = "main"
REPO_URL = f"https://github.com/{REPO}"
COLAB_URL = f"https://colab.research.google.com/github/{REPO}/blob/{BRANCH}/"
DOC_DIRS = ["lectures", "homework", "project", "exercises"]

# Anything matching these must never be published.
FORBIDDEN = re.compile(r"solution|answer[-_ ]?key|midterm|final[-_ ]?exam|qualifying|exam[-_ ]", re.I)

# --------------------------------------------------------------------------
# Course content shown on the homepage. Paths are relative to the repo root.
# --------------------------------------------------------------------------
MODULES = [
    {
        "title": "Linear optimization modeling",
        "weeks": "Weeks 3–4",
        "summary": "Classic LP model families (allocation, blending, operations planning, "
                   "shift scheduling) and how to implement them in AMPL from Python.",
        "notes": [
            ("Basic LP models (slides)", "lectures/lp-basic-models.pptx"),
            ("Model adaptation scenarios: “What if?” study guide", "lectures/lp-model-adaptation-scenarios.md"),
            ("Optimization with Python & AMPL (slides)", "lectures/optimization-with-python-and-ampl.pdf"),
            ("AMPL quick reference guide", "lectures/ampl-quick-reference.md"),
        ],
        "labs": [
            ("AMPL tutorial: LP with Python & AMPL", "labs/ampl-tutorial.ipynb"),
            ("AMPL example: three ways to build a model", "labs/ampl-example.ipynb"),
        ],
        "homework": [("Homework 2", "homework/hw2.md")],
    },
    {
        "title": "Integer optimization",
        "weeks": "Weeks 5–6",
        "summary": "Fixed charges, capital budgeting, set covering, facility location, network "
                   "design and scheduling; LP relaxations, branch and bound, and solver logs.",
        "notes": [
            ("Integer optimization models", "lectures/integer-optimization.md"),
            ("Supplement: Swedish Steel product selection", "lectures/swedish-steel-supplement.md"),
            ("Solving integer programs", "lectures/solving-ip.md"),
        ],
        "labs": [
            ("Lab: solving integer programming models", "labs/solving-ip-lab.ipynb"),
            ("Exercises: integer programming modeling", "labs/ip-exercises.ipynb"),
        ],
        "homework": [("Homework 3", "homework/hw3.md")],
    },
    {
        "title": "Network flow models",
        "weeks": "Weeks 7–8",
        "summary": "Minimum cost network flow, max flow, shortest path, transportation, "
                   "assignment and matching; total unimodularity and integrality.",
        "notes": [("Network flow models", "lectures/network-flow-models.md")],
        "labs": [("Lab: network flow models in Python", "labs/network-flow-lab.ipynb")],
        "homework": [("Homework 5", "homework/hw5.md")],
    },
    {
        "title": "Advanced LP and IP models",
        "weeks": "Weeks 11–12",
        "summary": "Traveling salesman and vehicle routing formulations, and the optimization "
                   "models behind regression, SVMs, clustering and classification trees.",
        "notes": [
            ("Advanced routing models (TSP, VRP)", "lectures/advanced-routing.md"),
            ("Machine learning and optimization", "lectures/ml-and-optimization.md"),
        ],
        "labs": [
            ("Lab: advanced routing", "labs/advanced-routing-lab.ipynb"),
            ("Lab: machine learning and optimization", "labs/ml-and-optimization-lab.ipynb"),
        ],
        "homework": [("Homework 6", "homework/hw6.md")],
    },
    {
        "title": "Optimization under uncertainty",
        "weeks": "Week 13",
        "summary": "Two-stage stochastic programs, VSS and EVPI, chance constraints, robust "
                   "optimization and stochastic integer programs.",
        "notes": [
            ("Stochastic optimization", "lectures/stochastic-optimization.md"),
            ("Optimization under uncertainty", "lectures/optimization-under-uncertainty.md"),
        ],
        "labs": [("Lab: optimization under uncertainty", "labs/uncertainty-lab.ipynb")],
        "homework": [("Homework 7", "homework/hw7.md")],
    },
    {
        "title": "Large-scale methods",
        "weeks": "Week 14",
        "summary": "Column generation, Dantzig–Wolfe and Benders decomposition, and "
                   "Lagrangian relaxation.",
        "notes": [("Large-scale optimization methods", "lectures/large-scale-methods.md")],
        "labs": [("Lab: large-scale methods", "labs/large-scale-methods-lab.ipynb")],
        "homework": [],
    },
    {
        "title": "Advanced topics and next steps",
        "weeks": "Week 15",
        "summary": "Bilevel optimization, and a closing lecture on where to go after this course.",
        "notes": [
            ("Bilevel optimization", "lectures/bilevel-optimization.md"),
            ("What now? From optimization to continued learning", "lectures/what-now.md"),
        ],
        "labs": [],
        "homework": [],
    },
]

EXERCISES = [
    ("The Carpenter’s Dilemma", "exercises/carpenters-dilemma.md"),
    ("The Orbital Payload", "exercises/orbital-payload.md"),
]

CASE_STUDIES = [
    ("Linear programming: hospital staffing and resource planning", "project/case-study-1-linear-programming.md"),
    ("Integer programming: food bank distribution network design", "project/case-study-2-integer-programming.md"),
    ("Network models: municipal water distribution", "project/case-study-3-network-models.md"),
    ("Routing: grocery e-commerce delivery routes", "project/case-study-4-routing-problem.md"),
    ("Stochastic LP: crop planning under uncertainty", "project/case-study-5-stochastic-lp-ip.md"),
    ("Large-scale LP/IP: airline crew scheduling", "project/case-study-6-large-scale-lp-ip.md"),
]

HOMEWORK_TOPICS = {
    "hw2": "AMPL tutorial exercises; Rardin Ch. 4 LP applications",
    "hw3": "Integer optimization formulation exercises",
    "hw5": "Network flow practice problems",
    "hw6": "TSP and VRP modeling and implementation",
    "hw7": "Optimization under uncertainty exercises",
}

SITE_TITLE = "ISYE 671 · Linear Optimization and Network Flows"


# --------------------------------------------------------------------------
def pandoc_path():
    exe = shutil.which("pandoc")
    if exe:
        return exe
    try:
        import pypandoc
        return pypandoc.get_pandoc_path()
    except Exception:
        sys.exit("pandoc not found. Install it, or run: pip install pypandoc_binary")


def check_forbidden():
    tracked = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                             cwd=ROOT, capture_output=True, text=True).stdout.split()
    bad = [p for p in tracked if FORBIDDEN.search(Path(p).name) and not p.startswith("tools/")]
    if bad:
        sys.exit("Refusing to build: these files look like solutions or exams:\n  " + "\n  ".join(bad))


def rel(from_page: str, target: str) -> str:
    return os.path.relpath(ROOT / target, (ROOT / from_page).parent).replace(os.sep, "/")


NAV = [("Home", "index.html"), ("Materials", "materials.html"), ("Homework", "homework.html"),
       ("Project", "project.html"), ("Syllabus", "syllabus.html")]


def page(title, body, page_path, description="", active=""):
    r = lambda p: rel(page_path, p)
    on = ' class="on"'
    nav_html = "".join(f'<a href="{r(h)}"{on if n == active else ""}>{n}</a>' for n, h in NAV)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description or SITE_TITLE)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Mono&display=swap">
<link rel="stylesheet" href="{r('assets/style.css')}">
<script>
window.MathJax = {{ tex: {{ inlineMath: [['\\\\(', '\\\\)']], displayMath: [['\\\\[', '\\\\]']] }} }};
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
</head>
<body>
<header class="bar">
  <div class="wrap">
    <a class="course" href="{r('index.html')}">ISYE 671</a>
    <nav>{nav_html}</nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="wrap foot">
  ISYE 671 · Northern Illinois University · Spring 2026 ·
  <a href="{REPO_URL}">Source on GitHub</a> ·
  <a href="{REPO_URL}/blob/{BRANCH}/LICENSE">CC BY-NC-SA 4.0</a>
</footer>
</body>
</html>
"""


def downloads_for(md_path: Path):
    """Sibling files with the same stem (or stem-slides) that visitors can download."""
    out = [("Markdown", md_path)]
    for stem in (md_path.stem, md_path.stem + "-slides"):
        for ext in (".pdf", ".pptx", ".docx"):
            q = md_path.with_name(stem + ext)
            if q.exists():
                label = ("slides " if stem.endswith("-slides") else "") + ext[1:].upper()
                out.append((label, q))
    return out


def render_doc(pandoc, md_path: Path):
    html_path = md_path.with_suffix(".html")
    page_rel = html_path.relative_to(ROOT).as_posix()
    frag = subprocess.run(
        [pandoc, str(md_path), "-f", "markdown+tex_math_dollars+pipe_tables+raw_html-implicit_figures",
         "-t", "html5", "--mathjax", "--wrap=none"],
        capture_output=True, text=True, check=True).stdout
    m = re.search(r"<h1[^>]*>(.*?)</h1>", frag, re.S)
    title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else md_path.stem.replace("-", " ").title()
    section = {"lectures": "Materials", "exercises": "Materials", "homework": "Homework",
               "project": "Project"}.get(md_path.parent.name, "Syllabus")
    if section == "Syllabus":
        title = "Syllabus"
    back = dict(NAV)[section]
    dl = " · ".join(f'<a href="{os.path.relpath(q, html_path.parent)}" download>{html.escape(l)}</a>'
                    for l, q in downloads_for(md_path))
    body = (f'<p class="docbar"><a href="{rel(page_rel, back)}">← {section}</a>'
            f'<span>Download: {dl}</span></p>\n<article class="prose">\n{frag}\n</article>')
    html_path.write_text(page(f"{title} – ISYE 671", body, page_rel, active=section), encoding="utf-8")


def links(path: str):
    """HTML links for one material: main link plus plain download links."""
    q = ROOT / path
    if not q.exists():
        sys.exit(f"Missing file referenced in build.py: {path}")
    if q.suffix == ".md":
        extra = [(l, x.relative_to(ROOT).as_posix()) for l, x in downloads_for(q) if l != "Markdown"]
        main = path[:-3] + ".html"
    elif q.suffix == ".ipynb":
        extra = []
        main = COLAB_URL + path
    else:
        extra, main = [], path
    return main, extra


def entry(title, path):
    main, extra = links(path)
    ext = Path(path).suffix.lower()
    tgt = ' target="_blank" rel="noopener"' if ext == ".ipynb" else ""
    tag = ""
    ex = "".join(f' <a class="alt" href="{h}" download>{l}</a>' for l, h in extra)
    return f'<li><a href="{main}"{tgt}>{html.escape(title)}</a>{tag}{ex}</li>'


def ul(items):
    return "<ul>" + "".join(entry(t, p) for t, p in items) + "</ul>" if items else '<span class="none">—</span>'


def write(name, title, body, active, description=""):
    (ROOT / name).write_text(page(title, body, name, description, active), encoding="utf-8")


def build_index():
    n_notes = sum(len(m["notes"]) for m in MODULES)
    n_labs = sum(len(m["labs"]) for m in MODULES)
    topics = "".join(f"<li>{html.escape(m['title'])}</li>" for m in MODULES)
    body = f"""
<h1>Linear Optimization and Network Flows</h1>
<p class="sub">ISYE 671 · Graduate course · Northern Illinois University · Spring 2026<br>
Instructor: Dr. Ziteng Wang, Industrial and Systems Engineering</p>

<p>This site shares the materials from the Spring 2026 offering of ISYE 671. Students learn to
formulate linear, integer, network, stochastic and large-scale optimization models and to solve
them with AMPL and Python in Google Colab. Generative AI is used as a coding assistant, with
full disclosure required.</p>

<h2>What's here</h2>
<table class="index">
<tr><td><a href="materials.html">Materials</a></td><td>{n_notes} lecture notes and slide decks, {n_labs} Colab notebooks, in-class exercises</td></tr>
<tr><td><a href="homework.html">Homework</a></td><td>{len(HOMEWORK_TOPICS)} assignments (solutions are not published)</td></tr>
<tr><td><a href="project.html">Project</a></td><td>Project requirements and {len(CASE_STUDIES)} case studies</td></tr>
<tr><td><a href="syllabus.html">Syllabus</a></td><td>Objectives, grading, schedule and AI policy</td></tr>
</table>

<h2>Topics</h2>
<ol class="topics">{topics}</ol>

<h2>Running the labs</h2>
<p>Each lab opens directly in Google Colab; nothing needs to be installed. The notebooks use AMPL,
which needs a free license: request one at <a href="https://ampl.com/ce">ampl.com/ce</a> and paste
the UUID where a notebook says <code>YOUR-AMPL-LICENSE-UUID</code>.</p>

<h2>Textbook</h2>
<p>R. L. Rardin, <em>Optimization in Operations Research</em>, 2nd ed., Pearson.
Prerequisites: an undergraduate operations research course and basic programming.</p>

<p class="small">All files can be <a href="{REPO_URL}/archive/refs/heads/{BRANCH}.zip">downloaded as one zip</a>
or browsed on <a href="{REPO_URL}">GitHub</a>. Found an error? <a href="{REPO_URL}/issues">Open an issue</a>.</p>
"""
    write("index.html", SITE_TITLE, body, "Home",
          "Open course materials for ISYE 671 at Northern Illinois University: lecture notes, "
          "Colab labs, homework and project case studies.")


def build_materials():
    rows = "".join(
        f'<tr><td class="n">{i}</td><td><strong>{html.escape(m["title"])}</strong>'
        f'<div class="when">{m["weeks"]}</div></td><td data-label="Lecture notes">{ul(m["notes"])}</td>'
        f'<td data-label="Labs (Colab)">{ul(m["labs"])}</td></tr>'
        for i, m in enumerate(MODULES, 1))
    body = f"""
<h1>Materials</h1>
<p>Lecture notes open as web pages, with PDF or slide versions linked beside them.
Labs open in Google Colab.</p>
<table class="grid">
<thead><tr><th></th><th>Topic</th><th>Lecture notes</th><th>Labs (Colab)</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<h2>In-class exercises</h2>
<p>Short warm-up problems from class. Try them before opening a solver.</p>
{ul(EXERCISES)}
"""
    write("materials.html", "Materials – ISYE 671", body, "Materials")


def build_homework():
    rows = "".join(
        f'<tr><td><a href="homework/{n}.html">Homework {n[2:]}</a></td><td>{html.escape(t)}</td>'
        f'<td><a href="homework/{n}.docx" download>DOCX</a></td></tr>'
        for n, t in HOMEWORK_TOPICS.items())
    body = f"""
<h1>Homework</h1>
<p>Assignments as given in Spring 2026. Most point to exercises in the
<a href="materials.html">lecture notes and labs</a>. Homework 1 and 4 are not included,
and solutions are not published.</p>
<table class="grid">
<thead><tr><th>Assignment</th><th>Topic</th><th>File</th></tr></thead>
<tbody>{rows}</tbody>
</table>
"""
    write("homework.html", "Homework – ISYE 671", body, "Homework")


def build_project():
    body = f"""
<h1>Course project</h1>
<p>Teams of one or two choose a case study, formulate and implement the model in Colab, analyze
the results and write a memo for a decision maker. Details are in the
<a href="project/project-requirements.html">project requirements</a>.</p>
<h2>Case studies</h2>
<ol class="cases">{"".join(entry(t, p) for t, p in CASE_STUDIES)}</ol>
"""
    write("project.html", "Project – ISYE 671", body, "Project")


def main():
    check_forbidden()
    pandoc = pandoc_path()
    docs = [ROOT / "syllabus.md"] + sorted(p for d in DOC_DIRS for p in (ROOT / d).glob("*.md"))
    for md in docs:
        render_doc(pandoc, md)
    build_index()
    build_materials()
    build_homework()
    build_project()
    (ROOT / ".nojekyll").touch()
    print(f"Built 5 site pages and {len(docs)} document pages.")


if __name__ == "__main__":
    main()
