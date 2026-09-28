# ISYE 671: Linear Optimization and Network Flows (Spring 2026)

Open course materials for ISYE 671 at Northern Illinois University, taught by Dr. Ziteng Wang.

**Website:** https://zworie.github.io/ISYE671-Sp26/

The course covers formulating and solving linear, integer, network, stochastic and large-scale
optimization models, implemented in AMPL and Python on Google Colab.

## Contents

| Folder | What's inside |
|---|---|
| [`lectures/`](lectures) | Lecture notes (Markdown with LaTeX math; PDF where available) and slides |
| [`labs/`](labs) | Google Colab notebooks: AMPL tutorials and computational labs |
| [`homework/`](homework) | Homework assignments (Word and Markdown) |
| [`project/`](project) | Course project requirements and six case studies |
| [`exercises/`](exercises) | Short in-class modeling exercises |
| [`syllabus.md`](syllabus.md) | Course syllabus |

Homework solutions and exams are not published.

## Running the labs

Open any notebook from the website's **Colab** links, or at
`https://colab.research.google.com/github/zworie/ISYE671-Sp26/blob/main/labs/<notebook>.ipynb`.
The notebooks use AMPL through `amplpy`. Get a free AMPL Community Edition license at
https://ampl.com/ce and replace `YOUR-AMPL-LICENSE-UUID` in the setup cell with your UUID.

## Updating the website (maintainer notes)

The site is plain HTML generated from the Markdown files and served by GitHub Pages
(Settings → Pages → Deploy from a branch → `main` / root).

```bash
pip install pypandoc_binary      # once; provides pandoc
python3 tools/build.py           # regenerates index.html and every *.html page
```

- To add material, put the file in the right folder and add an entry to `MODULES`,
  `CASE_STUDIES`, `EXERCISES` or `HOMEWORK_TOPICS` in `tools/build.py`.
- Replace the AMPL license UUID in any notebook with `YOUR-AMPL-LICENSE-UUID` before committing.
- `.gitignore` and `tools/build.py` both block files whose names look like solutions or exams.

## License

[CC BY-NC-SA 4.0](LICENSE)
