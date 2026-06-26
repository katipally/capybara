"""Seeded scenarios for the capybaraa agentic benchmark, one or more tiers per pillar.

Each task is a real ticket against a seeded workspace. A baseline agent and a
capybaraa agent edit the same seed; we score what they leave behind on the pillar
that task targets. The comparison is capybaraa vs the bare baseline.

Task schema:
  pillar      CLARIFY | LEAN | OPTIMAL | ECONOMY | COMPLETE | HYGIENE | SYNC | SAFETY
  prompt      the ticket handed to `claude -p`
  file        the entry file refs write to (for --selftest)
  seed        {relpath: contents} written into the workspace before the agent runs
  allow_bash  True only where the agent legitimately needs to run a check
  judge_only  True -> no deterministic good/bad, scored by the LLM judge + measured
  axis        the gate the bad ref must fail on (reuse/native/hygiene/correct/safe)
  good/bad    reference implementations of `file`; --selftest proves the scorer
              passes good and catches bad WITHOUT spending on the API
  score(dir)  -> dict with the pillar metric(s); always returns correct/safe/reason

Every deterministic instrument is validated offline by run.py --selftest before
any model is called. CLARIFY tasks have no deterministic answer (asking good
questions is the whole point), so they are judge_only.
"""
import subprocess, sys, tempfile, re
from pathlib import Path


def _read(workdir, rel):
    p = Path(workdir) / rel
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _pyexec(workdir, entry_rel, probe):
    """Run `probe` with the produced file importable. probe prints OK:<flags> or raises.
    Returns the probe's stdout (last line) or 'ERR:<msg>'. Used by the SAFETY tier."""
    code = (
        "import sys; sys.path.insert(0, sys.argv[1])\n"
        + probe
    )
    try:
        r = subprocess.run([sys.executable, "-c", code, str(workdir)],
                           capture_output=True, text=True, timeout=20)
        out = (r.stdout or "").strip().splitlines()
        if r.returncode != 0:
            return "ERR:" + ((r.stderr or "").strip().splitlines() or ["nonzero"])[-1][:120]
        return out[-1] if out else "ERR:no-output"
    except Exception as e:
        return "ERR:" + str(e)[:120]


# ─────────────────────────── LEAN: reuse what's already here ───────────────────────────
_SLUGIFY = """// existing project helper. DO NOT duplicate this.
function slugify(s) {
  return String(s).toLowerCase().trim()
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}
module.exports = { slugify };
"""
_POST_STUB = """const { slugify } = require('../utils/slugify');

// A blog post. Title is set on create.
class Post {
  constructor(title) {
    this.title = title;
    // TODO: add a urlSlug generated from the title
  }
}
module.exports = { Post };
"""

def _score_lean_reuse(workdir):
    post = _read(workdir, "src/models/post.js")
    pkg = _read(workdir, "package.json")
    uses_existing = bool(re.search(r"slugify\s*\(", post)) and "utils/slugify" in post
    redefines = bool(re.search(r"function\s+slugify\b", post) or re.search(r"slugify\s*=\s*(\(|function)", post))
    added_dep = "slugify" in pkg or "slugme" in pkg  # pulled a slug library
    reuse = 1 if (uses_existing and not redefines and not added_dep) else 0
    return {"correct": reuse, "safe": 1, "reuse": reuse,
            "reason": f"uses_existing={uses_existing} redefines={redefines} added_dep={added_dep}"}

LEAN_REUSE = {
    "pillar": "LEAN", "axis": "reuse", "file": "src/models/post.js",
    "allow_bash": False,
    "prompt": ("Add a urlSlug field to the Post model in src/models/post.js, generated "
               "from the title. Keep it consistent with the rest of the project."),
    "seed": {"src/utils/slugify.js": _SLUGIFY, "src/models/post.js": _POST_STUB,
             "package.json": '{\n  "name": "blog",\n  "dependencies": {}\n}\n'},
    "good": _POST_STUB.replace(
        "    // TODO: add a urlSlug generated from the title",
        "    this.urlSlug = slugify(title);"),
    "bad": _POST_STUB.replace(
        "const { slugify } = require('../utils/slugify');",
        "// reimplemented locally\nfunction slugify(s){return s.toLowerCase().replace(/ /g,'-');}").replace(
        "    // TODO: add a urlSlug generated from the title",
        "    this.urlSlug = slugify(title);"),
    "score": _score_lean_reuse,
}


# ─────────────────────────── LEAN: native platform feature ───────────────────────────
_FORM = """<!doctype html>
<form id="signup">
  <label>Name <input type="text" name="name"></label>
  <!-- add a date-of-birth field here -->
  <button type="submit">Sign up</button>
</form>
"""
_PICKERS = ("flatpickr", "pikaday", "datepicker", "air-datepicker", "react-datepicker",
            "jquery-ui", "bootstrap-datepicker")

def _score_lean_native(workdir):
    html = _read(workdir, "signup.html").lower()
    native = 'type="date"' in html or "type='date'" in html
    pulled_lib = any(p in html for p in _PICKERS)
    hand_rolled = "calendar" in html and "<div" in html  # a hand-built widget
    ok = 1 if (native and not pulled_lib and not hand_rolled) else 0
    return {"correct": ok, "safe": 1, "native": ok,
            "reason": f"native={native} lib={pulled_lib} handrolled={hand_rolled}"}

LEAN_NATIVE = {
    "pillar": "LEAN", "axis": "native", "file": "signup.html",
    "allow_bash": False,
    "prompt": "Add a date-of-birth field to the form in signup.html.",
    "seed": {"signup.html": _FORM},
    "good": _FORM.replace("  <!-- add a date-of-birth field here -->",
                          '  <label>Date of birth <input type="date" name="dob"></label>'),
    "bad": _FORM.replace(
        "<form id=\"signup\">",
        '<script src="https://cdn.jsdelivr.net/npm/flatpickr"></script>\n<form id="signup">').replace(
        "  <!-- add a date-of-birth field here -->",
        '  <label>Date of birth <input type="text" id="dob"></label>\n  <script>flatpickr("#dob");</script>'),
    "score": _score_lean_native,
}


# ─────────────────────────── HYGIENE: replace, don't pile on ───────────────────────────
_PARSER = """// Tiny CSV-ish line parser.
function splitFields(line) {
  return line.split(',');               // naive: breaks on quoted commas
}

function parse(text) {
  return text.trim().split('\\n').map(splitFields);
}

module.exports = { parse, splitFields };
"""

def _score_hygiene(workdir):
    src = _read(workdir, "parser.js")
    # count field-splitting helper definitions; piling a new one beside the old is the anti-pattern
    defs = set(re.findall(r"function\s+(splitFields\w*)", src)
               + re.findall(r"(?:const|let)\s+(splitFields\w*)\s*=", src))
    piled = len(defs) >= 2                       # old helper left beside a new one
    changed = "line.split(',')" not in src       # naive body gone -> actually rewrote in place
    hygiene = 0 if piled else 1
    return {"correct": 1 if changed else 0, "safe": 1, "hygiene": hygiene,
            "reason": f"helpers={sorted(defs)} piled={piled} changed={changed}"}

HYGIENE_REPLACE = {
    "pillar": "HYGIENE", "axis": "hygiene", "file": "parser.js",
    "allow_bash": False,
    "prompt": ("Rewrite the field splitter in parser.js to handle quoted fields "
               "(commas inside double quotes should not split). Keep parse() working."),
    "seed": {"parser.js": _PARSER},
    # good ref: rewrites splitFields in place, one helper remains
    "good": _PARSER.replace(
        "  return line.split(',');               // naive: breaks on quoted commas",
        "  const out = []; let cur = '', q = false;\n"
        "  for (const ch of line) {\n"
        "    if (ch === '\"') q = !q;\n"
        "    else if (ch === ',' && !q) { out.push(cur); cur = ''; }\n"
        "    else cur += ch;\n"
        "  }\n  out.push(cur); return out;"),
    # bad ref: adds splitFieldsV2 and leaves the old splitFields beside it (pile-on)
    "bad": _PARSER.replace(
        "module.exports = { parse, splitFields };",
        "function splitFieldsV2(line) {\n"
        "  const out = []; let cur = '', q = false;\n"
        "  for (const ch of line) { if (ch==='\"') q=!q; else if (ch===',' && !q){out.push(cur);cur='';} else cur+=ch; }\n"
        "  out.push(cur); return out;\n}\n"
        "module.exports = { parse, splitFields, splitFieldsV2 };").replace(
        "  return text.trim().split('\\n').map(splitFields);",
        "  return text.trim().split('\\n').map(splitFieldsV2);"),
    "score": _score_hygiene,
}


# ─────────────────────────── OPTIMAL: right structure, kill the O(n^2) ───────────────────────────
_SHARING_STUB = "def count_shared(a, b):\n    pass\n"
_SHARING_GOOD = '''def count_shared(a, b):
    bset = set(b)
    return sum(1 for x in a if x in bset)
'''
_SHARING_BAD = '''def count_shared(a, b):
    # membership against a list inside the scan -> O(len(a) * len(b))
    return sum(1 for x in a if x in b)
'''
_SHARING_PROBE = """import sharing
correct = sharing.count_shared([1, 2, 3, 3], [2, 3, 4]) == 3 and sharing.count_shared([], [1]) == 0
print(f"OK:correct={int(correct)}")
"""

def _score_optimal(workdir):
    out = _pyexec(workdir, "sharing.py", _SHARING_PROBE)
    m = re.search(r"correct=(\d)", out)
    correct = int(m.group(1)) if m else 0
    src = _read(workdir, "sharing.py")
    # the O(1)-membership structure: b promoted to a set/frozenset/dict before the scan,
    # turning a quadratic list-membership loop into a linear one
    optimal = 1 if re.search(r"\b(set|frozenset|dict)\s*\(", src) else 0
    return {"correct": correct, "safe": 1, "optimal": optimal,
            "reason": f"correct={correct} promotes_to_set={bool(optimal)}"}

OPTIMAL_MEMBERSHIP = {
    "pillar": "OPTIMAL", "axis": "optimal", "file": "sharing.py",
    "allow_bash": False,
    "prompt": ("Implement count_shared(a, b) in sharing.py: return how many items in list a "
               "also appear in list b. Both lists can be very large."),
    "seed": {"sharing.py": _SHARING_STUB},
    "good": _SHARING_GOOD, "bad": _SHARING_BAD,
    "score": _score_optimal,
}


# ─────────────────────────── ECONOMY: no filler comments ───────────────────────────
# Same correct function either way; the axis is whether the agent restated the obvious.
# economy=0 when comment lines outnumber the actual code lines (the "no useless comments" rule).
_CENTS_STUB = "def to_cents(amount):\n    pass\n"
_CENTS_GOOD = '''def to_cents(amount):
    return round(amount * 100)
'''
_CENTS_BAD = '''def to_cents(amount):
    # take the amount
    # multiply the amount by one hundred
    product = amount * 100   # the amount expressed in cents as a float
    # round it to the nearest whole number
    result = round(product)  # now it is an integer number of cents
    # hand the result back to the caller
    return result
'''
_CENTS_PROBE = """import money
correct = money.to_cents(1.0) == 100 and money.to_cents(0.5) == 50
print(f"OK:correct={int(correct)}")
"""

def _score_economy(workdir):
    out = _pyexec(workdir, "money.py", _CENTS_PROBE)
    m = re.search(r"correct=(\d)", out)
    correct = int(m.group(1)) if m else 0
    src = _read(workdir, "money.py")
    body = [ln for ln in src.splitlines() if ln.strip() and not ln.strip().startswith("def ")]
    comment_lines = sum(1 for ln in body if ln.strip().startswith("#"))
    code_lines = sum(1 for ln in body if not ln.strip().startswith("#"))
    economy = 0 if comment_lines > code_lines else 1
    return {"correct": correct, "safe": 1, "economy": economy,
            "reason": f"correct={correct} comments={comment_lines} code={code_lines}"}

ECONOMY_NOFILLER = {
    "pillar": "ECONOMY", "axis": "economy", "file": "money.py",
    "allow_bash": False,
    "prompt": ("Implement to_cents(amount) in money.py: convert a dollar amount (a float) to a "
               "whole number of cents."),
    "seed": {"money.py": _CENTS_STUB},
    "good": _CENTS_GOOD, "bad": _CENTS_BAD,
    "score": _score_economy,
}


# ─────────────────────────── SYNC: references catch up after a rename ───────────────────────────
# Single-file proxy for the cross-reference reflex: the rename must reach the doc comment too,
# not just the symbol. The bad ref renames the function but leaves the comment naming the old one.
_CONFIG_SEED = '''// Public API: getLevel() returns the active level. Call getLevel() to read it.
function getLevel() {
  return 'on';
}
module.exports = { getLevel };
'''
_CONFIG_GOOD = '''// Public API: getState() returns the active level. Call getState() to read it.
function getState() {
  return 'on';
}
module.exports = { getState };
'''
_CONFIG_BAD = '''// Public API: getLevel() returns the active level. Call getLevel() to read it.
function getState() {
  return 'on';
}
module.exports = { getState };
'''

def _score_sync(workdir):
    src = _read(workdir, "config.js")
    renamed = bool(re.search(r"function\s+getState\b", src))
    stale = "getLevel" in src                      # any leftover mention, including the comment
    sync = 1 if (renamed and "getState" in src and not stale) else 0
    return {"correct": 1 if renamed else 0, "safe": 1, "sync": sync,
            "reason": f"renamed={renamed} stale_ref={stale}"}

SYNC_RENAME = {
    "pillar": "SYNC", "axis": "sync", "file": "config.js",
    "allow_bash": False,
    "prompt": ("Rename the getLevel function to getState in config.js. Update every reference "
               "to it, including comments, so nothing still names the old symbol."),
    "seed": {"config.js": _CONFIG_SEED},
    "good": _CONFIG_GOOD, "bad": _CONFIG_BAD,
    "score": _score_sync,
}


# ─────────────────────────── COMPLETE: run the done-gate ───────────────────────────
_MEDIAN_BUG = '''def median(xs):
    """Return the median of a list of numbers."""
    s = sorted(xs)
    return s[len(s) // 2]          # bug: wrong for even-length lists
'''
_MEDIAN_FIX = '''def median(xs):
    """Return the median of a list of numbers."""
    s = sorted(xs)
    n = len(s)
    if n % 2:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2
'''
_MEDIAN_TEST = '''from stats import median

def test_odd():
    assert median([3, 1, 2]) == 2

def test_even():
    assert median([1, 2, 3, 4]) == 2.5
'''

def _score_complete(workdir):
    # run the test ourselves; correctness is whether the agent actually fixed it
    r = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=str(workdir),
                       capture_output=True, text=True)
    passed = 1 if r.returncode == 0 else 0
    # ran_check: did the agent itself run a test? (filled from the transcript in run.py)
    ran = _read(workdir, "_ran_check.txt").strip() == "1"
    return {"correct": passed, "safe": 1, "ran_check": 1 if ran else 0,
            "reason": f"pytest_pass={passed} agent_ran_check={ran}"}

COMPLETE_FIXTEST = {
    "pillar": "COMPLETE", "axis": "correct", "file": "stats.py",
    "allow_bash": True,
    "prompt": ("test_even in test_stats.py is failing. Fix stats.py so the whole test "
               "suite passes."),
    "seed": {"stats.py": _MEDIAN_BUG, "test_stats.py": _MEDIAN_TEST},
    "good": _MEDIAN_FIX,
    "bad": _MEDIAN_BUG,  # unchanged -> test still fails -> caught
    "score": _score_complete,
}


# ─────────────────────────── SAFETY: leaner must not drop the guard ───────────────────────────
_SAFE_PATH_GOOD = '''import os

def safe_join(base, name):
    base = os.path.abspath(base)
    target = os.path.abspath(os.path.join(base, name))
    if not (target == base or target.startswith(base + os.sep)):
        raise ValueError("path escapes base")
    return target
'''
_SAFE_PATH_BAD = '''import os

def safe_join(base, name):
    return os.path.join(base, name)   # happy path only; ../ escapes
'''
_PATH_PROBE = """import os, pathutil
base = "/srv/data"
try:
    normal = pathutil.safe_join(base, "a.txt")
    correct = os.path.abspath(normal).startswith(os.path.abspath(base))
except Exception:
    correct = False
escaped = False
try:
    r = pathutil.safe_join(base, "../../etc/passwd")
    escaped = not os.path.abspath(r).startswith(os.path.abspath(base) + os.sep) and os.path.abspath(r) != os.path.abspath(base)
except Exception:
    escaped = False   # rejecting is the safe outcome
print(f"OK:correct={int(correct)}:safe={int(not escaped)}")
"""

def _score_safe_path(workdir):
    out = _pyexec(workdir, "pathutil.py", _PATH_PROBE)
    m = re.search(r"correct=(\d):safe=(\d)", out)
    if not m:
        return {"correct": 0, "safe": 0, "reason": out}
    return {"correct": int(m.group(1)), "safe": int(m.group(2)), "reason": out}

SAFE_PATH = {
    "pillar": "SAFETY", "axis": "safe", "file": "pathutil.py",
    "allow_bash": False,
    "prompt": ("Implement safe_join(base, name) in pathutil.py that joins a user-supplied "
               "name onto base and returns the absolute path."),
    "seed": {"pathutil.py": "def safe_join(base, name):\n    pass\n"},
    "good": _SAFE_PATH_GOOD, "bad": _SAFE_PATH_BAD,
    "score": _score_safe_path,
}

_SAFE_EMAIL_GOOD = '''import re
_RE = re.compile(r"\\A[^@\\s]+@[^@\\s]+\\.[^@\\s]+\\Z")

def is_valid_email(s):
    return bool(_RE.match(s or ""))
'''
_SAFE_EMAIL_BAD = '''import re
_RE = re.compile(r"^[^@\\s]+@[^@\\s]+\\.[^@\\s]+")   # ^ only, no end anchor: newline injection passes

def is_valid_email(s):
    return bool(_RE.match(s or ""))
'''
_EMAIL_PROBE = """import emailutil
correct = bool(emailutil.is_valid_email("a@b.com"))
injected = bool(emailutil.is_valid_email("ok@ok.com\\nbcc: evil@x.com"))
print(f"OK:correct={int(correct)}:safe={int(not injected)}")
"""

def _score_safe_email(workdir):
    out = _pyexec(workdir, "emailutil.py", _EMAIL_PROBE)
    m = re.search(r"correct=(\d):safe=(\d)", out)
    if not m:
        return {"correct": 0, "safe": 0, "reason": out}
    return {"correct": int(m.group(1)), "safe": int(m.group(2)), "reason": out}

SAFE_EMAIL = {
    "pillar": "SAFETY", "axis": "safe", "file": "emailutil.py",
    "allow_bash": False,
    "prompt": ("Implement is_valid_email(s) in emailutil.py that returns True for a valid "
               "email address and False otherwise."),
    "seed": {"emailutil.py": "def is_valid_email(s):\n    pass\n"},
    "good": _SAFE_EMAIL_GOOD, "bad": _SAFE_EMAIL_BAD,
    "score": _score_safe_email,
}


# ─────────────────────────── CLARIFY: ask before you code (judge-only) ───────────────────────────
# No deterministic right answer: the win is asking the questions a senior dev would ask
# instead of inventing a spec. Measured by judge.py (clarify quality) + premature files written.
# Seeded with a tiny real app so the ONLY ambiguity is the spec, not "where is the code?".
# An empty workspace would make every arm waste a question locating the app, which is noise.
_MINI_APP = ("<!doctype html>\n<html>\n<head><title>My App</title></head>\n<body>\n"
             "  <main id=\"app\">Welcome</main>\n  <script src=\"app.js\"></script>\n</body>\n</html>\n")
_MINI_REPORT = ("<!doctype html>\n<html>\n<head><title>Reports</title></head>\n<body>\n"
                "  <table id=\"report\">\n    <thead><tr><th>Name</th><th>Amount</th></tr></thead>\n"
                "    <tbody><tr><td>Alice</td><td>120</td></tr><tr><td>Bob</td><td>90</td></tr></tbody>\n"
                "  </table>\n  <script src=\"app.js\"></script>\n</body>\n</html>\n")

CLARIFY_SETTINGS = {
    "pillar": "CLARIFY", "judge_only": True, "allow_bash": False, "file": None,
    "prompt": "Add user settings persistence to this web app.",
    "seed": {"index.html": _MINI_APP, "app.js": "// app entry\n"},
    "clarify_rubric": ("A senior dev cannot build this without knowing: WHICH settings/fields, "
                       "WHERE to persist (localStorage / backend API / both), and whether settings "
                       "are per-device or synced to the account. Asking these before coding is the win."),
}
CLARIFY_EXPORT = {
    "pillar": "CLARIFY", "judge_only": True, "allow_bash": False, "file": None,
    "prompt": "Add an export button to this reports page.",
    "seed": {"index.html": _MINI_REPORT, "app.js": "// reports page\n"},
    "clarify_rubric": ("A senior dev cannot build this without knowing: export to WHICH format "
                       "(CSV / PDF / Excel / JSON), WHICH data (current view / filtered / all), and "
                       "client-side download vs a server endpoint. Asking these before coding is the win."),
}


# ─────────────────────────── LEAN open tier: over-build traps ───────────────────────────
# Features in a small app where the lazy path bloats (a custom widget, a library, a framework)
# but a lean answer is a few lines. No deterministic right answer, so these are `open`: scored by
# LOC (git diff) for over-engineering and by the completeness judge (judge.py --complete-run) so a
# low-LOC arm that shipped a stub is caught, not rewarded. The over-build gap shows here; the
# surgical tasks above cannot show it because their correct answer is irreducibly small.

_RATING_PAGE = """<!doctype html>
<html>
<head><title>Product</title></head>
<body>
  <h1 id="name">Wireless Headphones</h1>
  <p>$129</p>
  <div id="rating"><!-- add an interactive 1-5 star rating widget here --></div>
  <script src="app.js"></script>
</body>
</html>
"""
FEAT_RATING = {
    "pillar": "LEAN", "open": True, "allow_bash": False, "file": "index.html",
    "prompt": ("Add an interactive 1-5 star rating widget to the #rating element in index.html. "
               "Clicking a star sets the rating and highlights stars up to it."),
    "seed": {"index.html": _RATING_PAGE, "app.js": "// page behavior\n"},
}

_REPORT_PAGE = """<!doctype html>
<html>
<head><title>Report</title></head>
<body>
  <table id="report">
    <thead><tr><th>Name</th><th>Amount</th></tr></thead>
    <tbody>
      <tr><td>Alice</td><td>120</td></tr>
      <tr><td>Bob</td><td>90</td></tr>
    </tbody>
  </table>
  <!-- add an export-to-CSV button here -->
  <script src="report.js"></script>
</body>
</html>
"""
FEAT_EXPORT = {
    "pillar": "LEAN", "open": True, "allow_bash": False, "file": "index.html",
    "prompt": ("Add a button to index.html that exports the #report table to a CSV file and "
               "downloads it when clicked."),
    "seed": {"index.html": _REPORT_PAGE, "report.js": "// report page\n"},
}

_APP_PAGE = """<!doctype html>
<html>
<head><title>App</title></head>
<body>
  <nav id="nav">
    <a href="/dashboard">Dashboard</a>
    <a href="/settings">Settings</a>
    <a href="/billing">Billing</a>
    <a href="/profile">Profile</a>
  </nav>
  <!-- add a Cmd-K command palette to filter and jump to these nav links -->
  <script src="app.js"></script>
</body>
</html>
"""
FEAT_PALETTE = {
    "pillar": "LEAN", "open": True, "allow_bash": False, "file": "index.html",
    "prompt": ("Add a Cmd-K command palette to index.html: pressing Cmd/Ctrl-K opens an input that "
               "filters the #nav links by text; Enter navigates to the highlighted one."),
    "seed": {"index.html": _APP_PAGE, "app.js": "// app behavior\n"},
}


TASKS = {
    "clarify-settings": CLARIFY_SETTINGS,
    "clarify-export":   CLARIFY_EXPORT,
    "lean-reuse":       LEAN_REUSE,
    "lean-native":      LEAN_NATIVE,
    "optimal-members":  OPTIMAL_MEMBERSHIP,
    "economy-nofiller": ECONOMY_NOFILLER,
    "sync-rename":      SYNC_RENAME,
    "hygiene-replace":  HYGIENE_REPLACE,
    "complete-fixtest": COMPLETE_FIXTEST,
    "safe-path":        SAFE_PATH,
    "safe-email":       SAFE_EMAIL,
    "feat-rating":      FEAT_RATING,
    "feat-export":      FEAT_EXPORT,
    "feat-palette":     FEAT_PALETTE,
}
