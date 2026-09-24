---
layout: default
title: Contributing
robots: noindex
permalink: /contributing/
---
<br>

# CyPhiLab Contributing Guide

This document describes how we use git and GitHub in this group. It's written for people who know how to code but haven't necessarily worked in a shared codebase before. Read it once at onboarding, then use it as a reference.

The goal isn't to make everyone a professional software engineer — it's to stop the three things that actually cost us time: lost work, code that only runs on one person's laptop, and nobody knowing why a script does what it does six months later.

---

## 1. Setup (do this once)

1. Install git and create a GitHub account if you don't have one.
2. Set your identity so commits are attributed to you, not "root" or a laptop name:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "you@case.edu"
   ```
3. Clone the repo (don't download a zip):
   ```bash
   git clone git@github.com:<org>/<repo>.git
   ```
4. Install [`uv`](https://docs.astral.sh/uv/) if you don't have it (`curl -LsSf https://astral.sh/uv/install.sh | sh`), then set up the environment from the repo's `pyproject.toml`:
   ```bash
   cd <repo>
   uv sync
   ```
   This creates a `.venv` and installs the exact pinned versions from `uv.lock` — no manual `venv`/`pip` steps, and no "works on my machine" drift between people's environments.
5. Run things with `uv run`, e.g. `uv run pytest` or `uv run scripts/run_simulation.py`. This uses the project's environment automatically, so you don't need to remember to activate it. (You can still `source .venv/bin/activate` if you prefer working that way.)
6. If the repo has a `pre-commit` config, install it: `uv run pre-commit install`. This auto-formats and lints your code before it's committed, so style arguments never happen in review.

---

## 2. Repository structure

Every project in this group should roughly follow:

```
project/
├── src/            # importable code (functions, classes — not scripts)
├── scripts/        # runnable entry points (e.g. run_simulation.py)
├── tests/          # pytest tests, mirroring src/ structure
├── notebooks/      # exploratory Jupyter notebooks (see note below)
├── docs/           # any long-form documentation
├── data/           # gitignored — never commit data
├── pyproject.toml  # project + dependency declarations (uv-managed)
├── uv.lock         # exact pinned versions — always commit this
├── README.md
└── .gitignore
```

**Notebooks**: fine for exploration, but code that other people depend on (analysis functions, plotting utilities, solvers) should be moved into `src/` and imported, not copy-pasted between notebooks. A notebook with the same 40-line function pasted into it eight times is the single most common failure mode we're trying to avoid.

---

## 3. The golden rule: `main` always works

`main` should always be in a state where someone else could clone it and run it. That means:

- **Never commit directly to `main`.** All work happens on a branch.
- **Never push code to `main` that doesn't run**, even "temporarily."
- If you break `main` by accident, say so immediately in the group Teams chat — don't quietly try to fix it. Everyone breaks main eventually; hiding it is the only actual mistake.

We enforce this with a GitHub branch protection rule on `main` requiring at least one PR review before merge.

---

## 4. Branching

Create a new branch for every distinct piece of work:

```bash
git checkout main
git pull                          # make sure you're starting from the latest
git checkout -b feature/short-description
```

Naming convention:

- `feature/...` — new capability
- `fix/...` — bug fix
- `refactor/...` — restructuring, no behavior change
- `docs/...` — documentation only

Keep branches **short-lived** (days, not months). A branch that lives for six weeks will have a brutal merge at the end. If a project is genuinely big, break it into smaller branches/PRs that each leave `main` in a working state.

---

## 5. Commits

Commit early and often — a commit is a checkpoint you can return to, not a formal ceremony.

- **One logical change per commit.** "Fix boundary condition bug" and "add unit conversion helper" should be two commits, not one.
- **Write commit messages in the imperative mood**, like an instruction: `Add convergence check to solver loop`, not `Added` or `Adding`. This matches git's own conventions and reads cleanly in `git log`.
- Reference an issue number if one exists: `Fix sign error in torque calc (#42)`.

Avoid commit messages like `fix`, `updates`, `asdf`, or `final_v2_REAL`. If you can't summarize the change in one line, the commit is probably too big — split it.

---

## 6. Pull requests

When your branch is ready (or even partway done — see draft PRs below):

```bash
git push -u origin feature/short-description
```

Then open a PR on GitHub into `main`.

- **Open a draft PR early** if you want visibility or feedback mid-task — it costs nothing and lets others see what you're working on.
- **Write a real description**: what changed, why, and how you tested it. "Updates code" is not a description. If it fixes a bug, say how you confirmed the fix.
- **Keep PRs small.** A 2,000-line PR touching twelve files will not get a careful review from anyone. If you can split it into two PRs, do.
- **At least one reviewer must approve before merging** (enforced by branch protection). Assign a reviewer, don't just wait for someone to notice.
- Once approved and passing any checks, merge it yourself — don't wait on the reviewer to do it.

---

## 7. Reviewing others' code

Everyone in the group reviews, not just senior members — reviewing is one of the fastest ways to learn the codebase.

- Aim to review within 1–2 business days so people aren't blocked.
- Comment on logic, correctness, and clarity — not personal style preferences that `pre-commit`/formatters should be handling automatically.
- Ask questions instead of issuing verdicts: "What happens here if the mesh has zero elements?" is more useful than "this is wrong."
- Approving a PR doesn't mean it's perfect — it means you're confident it's correct and reasonably clear. Nitpicks can be left as non-blocking comments.

---

## 8. Issues

Use GitHub Issues for anything bigger than a five-minute task: bugs, feature requests, "we should really refactor X."

- One issue = one problem. Don't bundle five unrelated things into one issue.
- Link PRs to the issues they resolve using `Closes #12` in the PR description — GitHub will auto-close the issue on merge.
- If you start work on something, assign yourself so two people don't duplicate it.

---

## 9. Data, secrets, and environments

- **Never commit data files, results, or anything over a few hundred KB.** Use `.gitignore` (see below). If data needs to be shared, use a shared drive, Box, or Git LFS — not the repo.
- **Never commit API keys, passwords, or credentials.** If you do this by accident, rotate the credential immediately — removing it from a later commit does not remove it from history.
- **Pin your dependencies.** Add packages with `uv add <package>` rather than `pip install` — it updates `pyproject.toml` and re-pins exact versions in `uv.lock` automatically. **Always commit `uv.lock`**; that's what makes everyone's (and every cluster job's) environment identical. If you edit `pyproject.toml` by hand, run `uv sync` afterward to update the lockfile.

### `.gitignore`

Start from GitHub's official template: **[github/gitignore → Python.gitignore](https://github.com/github/gitignore/blob/main/Python.gitignore)**. It already covers `__pycache__/`, `.venv/`, `.env`, `.ipynb_checkpoints`, and similar standard Python/tooling clutter, so there's no need to maintain that list by hand.

It won't know about our lab-specific conventions, so add these on top of it:

```
data/
results/
*.mat
```

---

## 10. Tests and documentation

You don't need exhaustive test coverage on research code, but:

- Any function other people call (solvers, data-processing utilities, unit conversions) should have at least one test that checks a known input/output pair.
- Run `pytest` before opening a PR, not after someone flags a failure.
- Use docstrings on shared functions — NumPy-style is standard in scientific Python:

  ```python
  def natural_frequency(k, m):
      """Compute the natural frequency of a spring-mass system.

      Parameters
      ----------
      k : float
          Spring stiffness [N/m].
      m : float
          Mass [kg].

      Returns
      -------
      float
          Natural frequency [rad/s].
      """
  ```

- Comment on *why*, not *what*. `# convert to SI because the sensor reports mbar` is useful; `# multiply x by 100` is not.

---

## 11. Quick command reference

| Task | Command |
|---|---|
| Start a new branch | `git checkout -b feature/name` |
| Check what's changed | `git status` |
| Stage and commit | `git add -p` then `git commit -m "message"` |
| Push a new branch | `git push -u origin feature/name` |
| Update your branch with latest `main` | `git checkout main && git pull && git checkout feature/name && git merge main` |
| See history | `git log --oneline --graph` |
| Undo uncommitted changes to a file | `git checkout -- filename` |
| Temporarily shelve changes | `git stash` / `git stash pop` |

If you're not sure what a command will do, don't guess — ask, or check **[oh-shit-git.com](https://ohshitgit.com)**. Almost every git mistake is recoverable if you stop and ask before running more commands.

---

## 12. Further resources

If you want to build up git skills beyond what this doc covers:

- **[Learn Git Branching](https://learngitbranching.js.org/)** — an interactive, visual sandbox for practicing branching, merging, and rebasing. Best starting point if you've only ever used `add`/`commit`/`push`.
- **[Version Control with Git — Software Carpentry](https://swcarpentry.github.io/git-novice/)** — a novice-friendly lesson written specifically for researchers, covering why version control matters for reproducible science.
- **[GitHub Skills](https://skills.github.com/)** — free, hands-on courses that run inside real GitHub repos. Good for learning pull requests and code review specifically, i.e. exactly the workflow in this doc.
- **[Pro Git (free online book)](https://git-scm.com/book/en/v2)** — the canonical deep reference for when you want to understand what git is actually doing under the hood.
- **[Oh Shit, Git!?!](https://ohshitgit.com/)** — a blunt, fast cheat sheet for undoing common git mistakes. Bookmark this before you need it.
- **[The Turing Way](https://book.the-turing-way.org/)** — a handbook for reproducible, collaborative research aimed at researchers rather than software engineers; covers version control alongside project structure and collaboration.

---

## 13. New member checklist

- <input type="checkbox" disabled> Git installed, `user.name`/`user.email` configured
- <input type="checkbox" disabled> SSH key added to your GitHub account
- <input type="checkbox" disabled> Repo cloned, virtual environment set up, `pytest` passes locally
- <input type="checkbox" disabled> Read this document
- <input type="checkbox" disabled> Opened one small practice PR (e.g., fix a typo in the README) to see the review flow before your first real change
