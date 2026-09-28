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


def page(title, body, page_path, description="", wide=False):
    r = lambda p: rel(page_path, p)
    nav = [("Modules", r("index.html") + "#modules"), ("Homework", r("index.html") + "#homework"),
           ("Project", r("index.html") + "#project"), ("Syllabus", r("syllabus.html"))]
    nav_html = "".join(f'<a href="{h}">{n}</a>' for n, h in nav)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description or SITE_TITLE)}">
<link rel="stylesheet" href="{r('assets/style.css')}">
<script>
window.MathJax = {{ tex: {{ inlineMath: [['\\\\(', '\\\\)']], displayMath: [['\\\\[', '\\\\]']] }} }};
</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
</head>
<body>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{r('index.html')}"><span class="brand-code">ISYE 671</span><span class="brand-name">Linear Optimization &amp; Network Flows</span></a>
    <nav>{nav_html}<a href="{REPO_URL}" class="gh">GitHub</a></nav>
  </div>
</header>
<main class="wrap {'wide' if wide else 'doc'}">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p>ISYE 671, Northern Illinois University, Spring 2026 · Dr. Ziteng Wang.
    Materials are shared under <a href="{REPO_URL}/blob/{BRANCH}/LICENSE">CC BY-NC-SA 4.0</a>.
    Homework solutions and exams are not published.</p>
  </div>
</footer>
</body>
</html>
"""


def downloads_for(md_path: Path):
    """Sibling files with the same stem (or stem-slides) that visitors can download."""
    out = [(".md", md_path)]
    for stem in (md_path.stem, md_path.stem + "-slides"):
        for ext in (".pdf", ".pptx", ".docx"):
            p = md_path.with_name(stem + ext)
            if p.exists():
                label = ("Slides " if stem.endswith("-slides") else "") + ext[1:].upper()
                out.append((label, p))
    return out


def render_doc(pandoc, md_path: Path):
    relpath = md_path.relative_to(ROOT).as_posix()
    html_path = md_path.with_suffix(".html")
    frag = subprocess.run(
        [pandoc, str(md_path), "-f", "markdown+tex_math_dollars+pipe_tables+raw_html-implicit_figures",
         "-t", "html5", "--mathjax", "--wrap=none"],
        capture_output=True, text=True, check=True).stdout
    m = re.search(r"<h1[^>]*>(.*?)</h1>", frag, re.S)
    title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else md_path.stem.replace("-", " ").title()
    if md_path.name == "syllabus.md":
        title = "Syllabus"
    dl = " ".join(
        f'<a class="chip" href="{os.path.relpath(p, html_path.parent)}" download>{html.escape(label)}</a>'
        for label, p in downloads_for(md_path))
    section = md_path.parent.name if md_path.parent != ROOT else ""
    crumb = f'<a href="{rel(relpath, "index.html")}">Home</a>' + (f" / {section.title()}" if section else "")
    body = f'<div class="doc-meta"><span class="crumb">{crumb}</span><span class="dl">Download: {dl}</span></div>\n<article class="prose">\n{frag}\n</article>'
    html_path.write_text(page(f"{title} · ISYE 671", body, html_path.relative_to(ROOT).as_posix()), encoding="utf-8")
    return html_path


def link_for(path: str):
    """Primary link + extra chips for one material item."""
    p = ROOT / path
    if not p.exists():
        sys.exit(f"Missing file referenced in build.py: {path}")
    if p.suffix == ".md":
        chips = [(label, q.relative_to(ROOT).as_posix()) for label, q in downloads_for(p) if label != ".md"]
        return path[:-3] + ".html", chips
    if p.suffix == ".ipynb":
        return COLAB_URL + path, [("Download", path)]
    return path, []


def item_html(title, path, kind):
    href, chips = link_for(path)
    ext = Path(path).suffix.lower()
    badge = {".ipynb": "Colab", ".pdf": "PDF", ".pptx": "PPTX"}.get(ext, "")
    target = ' target="_blank" rel="noopener"' if ext == ".ipynb" else ""
    chips_html = "".join(f'<a class="chip" href="{c}" download>{l}</a>' for l, c in chips)
    badge_html = f'<span class="badge">{badge}</span>' if badge else ""
    return f'<li class="{kind}"><a href="{href}"{target}>{html.escape(title)}</a>{badge_html}{chips_html}</li>'


def build_index():
    mods = []
    for i, m in enumerate(MODULES, 1):
        groups = ""
        for key, label in (("notes", "Lecture notes"), ("labs", "Colab labs"), ("homework", "Homework")):
            if m[key]:
                items = "".join(item_html(t, p, key) for t, p in m[key])
                groups += f'<div class="group"><h4>{label}</h4><ul>{items}</ul></div>'
        mods.append(f"""<section class="module" id="m{i}">
  <div class="module-head"><span class="num">{i:02d}</span><div><h3>{html.escape(m['title'])}</h3><p class="weeks">{m['weeks']}</p></div></div>
  <p class="summary">{html.escape(m['summary'])}</p>
  {groups}
</section>""")

    hw_rows = "".join(
        f'<tr><td><a href="homework/{n}.html">Homework {n[2:]}</a></td><td>{html.escape(t)}</td>'
        f'<td><a class="chip" href="homework/{n}.docx" download>DOCX</a></td></tr>'
        for n, t in HOMEWORK_TOPICS.items())
    cases = "".join(item_html(t, p, "notes") for t, p in CASE_STUDIES)
    exercises = "".join(item_html(t, p, "notes") for t, p in EXERCISES)
    n_notes = sum(len(m["notes"]) for m in MODULES)
    n_labs = sum(len(m["labs"]) for m in MODULES)

    body = f"""
<section class="hero">
  <p class="eyebrow">Graduate course · Northern Illinois University · Spring 2026</p>
  <h1>Linear Optimization and Network Flows</h1>
  <p class="lede">Open course materials for ISYE 671. The course covers formulating and solving linear,
  integer, network, stochastic and large-scale optimization models, implemented in AMPL and Python on
  Google Colab, with generative AI used as a coding co-pilot under an explicit disclosure policy.</p>
  <p class="instructor">Instructor: Dr. Ziteng Wang, Department of Industrial and Systems Engineering</p>
  <div class="cta">
    <a class="btn primary" href="#modules">Browse materials</a>
    <a class="btn" href="syllabus.html">Syllabus</a>
    <a class="btn" href="{REPO_URL}/archive/refs/heads/{BRANCH}.zip">Download everything (.zip)</a>
  </div>
</section>

<section class="quicknav">
  <a href="#modules"><strong>{n_notes}</strong><span>Lecture notes and slides</span></a>
  <a href="#modules"><strong>{n_labs}</strong><span>Colab notebooks</span></a>
  <a href="#homework"><strong>{len(HOMEWORK_TOPICS)}</strong><span>Homework assignments</span></a>
  <a href="#project"><strong>{len(CASE_STUDIES)}</strong><span>Project case studies</span></a>
</section>

<section class="start" id="start">
  <h2>Getting started</h2>
  <ol>
    <li><strong>Read the notes.</strong> Each lecture note opens as a web page with rendered math; PDF or slide versions are linked where available.</li>
    <li><strong>Run the labs in Colab.</strong> The “Colab” links open a notebook directly from this repository. No local installation is needed.</li>
    <li><strong>Get a free AMPL license.</strong> Request an AMPL Community Edition license at <a href="https://ampl.com/ce">ampl.com/ce</a> (or a course license at <a href="https://ampl.com/courses">ampl.com/courses</a>) and paste your UUID where a notebook says <code>YOUR-AMPL-LICENSE-UUID</code>.</li>
  </ol>
  <p class="textbook">Textbook: R. L. Rardin, <em>Optimization in Operations Research</em>, 2nd ed., Pearson. Background: ISYE 370 or equivalent, plus basic coding.</p>
</section>

<section id="modules">
  <h2>Course modules</h2>
  <div class="modules">
  {''.join(mods)}
  </div>
</section>

<section id="exercises" class="two-col">
  <div>
    <h2>In-class exercises</h2>
    <p>Short warm-up problems used in class to show why modeling matters. Try them before opening a solver.</p>
    <ul class="plain">{exercises}</ul>
  </div>
  <div id="homework">
    <h2>Homework</h2>
    <p>Assignments as given in Spring 2026. Several refer to exercises inside the lecture notes and labs above.
    Homework 1 and 4 are not included. Solutions are not published.</p>
    <table class="hw"><thead><tr><th>Assignment</th><th>Topic</th><th></th></tr></thead><tbody>{hw_rows}</tbody></table>
  </div>
</section>

<section id="project">
  <h2>Course project</h2>
  <p>Students pick one of six case studies and deliver a model, a Colab implementation, analysis and a
  managerial memo. See the <a href="project/project-requirements.html">project requirements</a>.</p>
  <ul class="plain cases">{cases}</ul>
</section>

<section id="about" class="about">
  <h2>About these materials</h2>
  <p>This site publishes lecture notes, labs, homework assignments and project case studies from the Spring 2026
  offering. Homework solutions and exams are not published. Use the materials for self-study or adapt them
  for teaching under the <a href="{REPO_URL}/blob/{BRANCH}/LICENSE">CC BY-NC-SA 4.0</a> license. To report an error,
  open an issue on <a href="{REPO_URL}/issues">GitHub</a>.</p>
</section>
"""
    (ROOT / "index.html").write_text(
        page(SITE_TITLE, body, "index.html",
             "Open course materials for ISYE 671 at Northern Illinois University: lecture notes, "
             "Colab labs, homework and project case studies.", wide=True),
        encoding="utf-8")


def main():
    check_forbidden()
    pandoc = pandoc_path()
    docs = [ROOT / "syllabus.md"] + sorted(p for d in DOC_DIRS for p in (ROOT / d).glob("*.md"))
    for md in docs:
        render_doc(pandoc, md)
    build_index()
    (ROOT / ".nojekyll").touch()
    print(f"Built index.html and {len(docs)} document pages.")


if __name__ == "__main__":
    main()
