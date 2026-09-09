#!/usr/bin/env python3
"""Lint one person's section of a team weekly status report.

It checks what management actually complained about: slang, expressive words
with no number behind them, vague quantities, unexpanded acronyms, internal
identifiers, sentence length (ASD-STE100: 25 words for descriptive text),
the shape of each block, and placeholders that must never ship.

Usage:
    lint_report.py DRAFT.md            # findings, exit 1 when any ERROR remains
    lint_report.py DRAFT.md --json
    lint_report.py -                   # read the section from stdin

ERROR  fix it, or list it under "Lint exceptions" with a one-line reason.
WARN   a question to answer while proof-reading; never fails the run.

Input is the markdown of one section (from "### Name" to "Blockers"), or the
same text as exported by Slite (sliteml markers are stripped).
"""
from __future__ import annotations

import html
import json
import re
import sys
from dataclasses import asdict, dataclass

# --------------------------------------------------------------------------- lists

TEMPLATE_LABELS = (
    "owner", "epics / features in progress", "other active issues",
    "active issues/features in progress", "recently completed", "this week",
    "next week", "blockers",
)

ALLOWED_ACRONYMS = {
    "PROJ", "KEY", "EPIC", "TASK",                             # placeholder keys
    "AI", "ID", "OK", "PHP", "HTML", "URL", "IP", "CPU", "RAM", "UTC",
    "KB", "MB", "GB", "TB", "KIB", "MIB", "GIB", "MS", "AM", "PM", "USD", "EUR",
}

# pattern -> what to write instead. Case-insensitive, whole words.
SLANG = {
    r"land(?:ed|s|ing)?": 'write "merged" or "is in version X"; "landed" reads as unserious',
    r"nail(?:ed|s)?": "say what was finished",
    r"tackl(?:e|ed|es|ing)": 'write "fixed", "started" or "worked on"',
    r"kick(?:ed|s)?[ -]?off": 'write "started"',
    r"ramp(?:ed|s)?[ -]?up": 'write "increased", with the numbers',
    r"deep[ -]dive": 'write "investigated"',
    r"heads[ -]up": 'write "note"',
    r"low[ -]hanging": "name the item",
    r"circle back|touch base": 'write "talk to X"',
    r"in[ -]flight": 'write "in progress"',
    r"black hole": 'write "data that was silently lost"',
    r"poison(?:ed|ous)?": 'write "a message the server will never accept"',
    r"drown(?:ed|s|ing)?": "say what happens, with the count",
    r"trickle[sd]?": "give the rate",
    r"blast(?:ed|s)?": "say what happened",
    r"scope[ -]?creep(?:ing)?": 'write "outside the ticket"',
    r"vib(?:e|es|ing)|\bslop\b": "remove",
    r"sanity[ -]check": 'write "check"',
    r"happy path|hot path": "say which case",
    r"greenfield|boil the ocean|north star|flywheel|silver bullet": "plain words",
    r"quick win|big win": "say what changed for whom",
    r"nuke[ds]?": 'write "deleted"',
    r"bump(?:ed|s)?": 'write "raised the version to X"',
    r"ping(?:ed|s)?": 'write "asked X"',
    r"flak(?:y|es|iness)": 'write "fails at random" or "fails intermittently"',
    r"guardrails?|footgun|yak[ -]shav\w+|bikeshed\w*|rabbit hole": "plain words",
    r"stays? dark|goes? dark|went dark": 'write "switched off until the server side deploys its part"',
    r"trip(?:ped|s)?\b(?! (?:to|over|up))": 'write "started" or "triggered"',
    r"dogfood\w*|hack(?:y|ed)?\b|gotcha|meat proxy|\bmeat\b": "plain words",
    r"\bsexy\b|\bjuice\b|\bkill(?:ed|s)?\b": "plain words",
}

# Jargon that is not wrong but makes the reader guess. Warn, ask for the precise word.
JARGON = {
    r"shipp?(?:ed|s|ing)?\b": 'shipped where? merged, in beta, in rollout, or on all servers: say which',
    r"roll(?:ed|s|ing)?[ -]?out": 'write "released to N% of servers" or "released to all servers"',
    r"unblock(?:ed|s)?": 'write "no longer waits on X"',
    r"regression": 'write "a bug that came back" or "we broke X that worked before"',
    r"hardening": 'say what fails less often, and by how much',
    r"observability|telemetry": 'write "monitoring data" or "measurements"',
    r"pipeline": 'write "automated checks" or name the process',
    r"harness": 'write "test setup"',
    r"\bgreen\b": 'write "all checks passed"',
    r"\back(?:ed|s)?\b|acknowledg\w+": 'write "confirmed"',
    r"upstream|downstream": "name the system",
    r"refactor\w*": 'say what changed for the reader, or drop it',
    r"feature flag|behind a flag": 'write "switched off by default until X"',
    r"\btail\b": "say which items",
    r"\bride[sd]?\b|\brode\b": 'write "is included in version X"',
    r"\bspike\b": 'write "a rise of N% in X"',
    r"backlog": 'write "planned, not started"',
    r"\bfleet\b": 'write "all customer servers (N)"',
    r"\bepic\b": 'fine in the table; in prose add what the epic is for, once',
}

AI_WORDS = [
    r"additionally", r"crucial(?:ly)?", r"delv(?:e|es|ed|ing)", r"enduring", r"enhanc(?:e|ed|es|ing|ement)",
    r"foster(?:s|ed|ing)?", r"garner(?:ed|s)?", r"interplay", r"intricate", r"landscape", r"pivotal",
    r"showcas(?:e|ed|es|ing)", r"tapestry", r"testament", r"underscor(?:e|es|ed|ing)", r"vibrant",
    r"robust(?:ly|ness)?", r"seamless(?:ly)?", r"leverag(?:e|ed|es|ing)", r"utiliz(?:e|ed|es|ing|ation)",
    r"streamlin(?:e|ed|es|ing)", r"holistic", r"synerg\w*", r"empower(?:s|ed|ing)?", r"elevat(?:e|ed|es|ing)",
    r"unlock(?:ed|s|ing)?", r"journey", r"ecosystem", r"paradigm", r"substrate", r"\bwedge\b", r"\blocus\b",
    r"\bnexus\b", r"bedrock", r"modality", r"gold[ -]plat\w+", r"ratchet\w*", r"endgame", r"comprehensive(?:ly)?",
    r"cutting[ -]edge", r"state[ -]of[ -]the[ -]art", r"best[ -]in[ -]class", r"world[ -]class", r"game[ -]changer",
    r"revolutioni\w+", r"transformative", r"not just", r"it'?s worth noting", r"it is important to note",
    r"in order to", r"due to the fact", r"serves as", r"stands as", r"boasts?", r"delighted", r"excited",
    r"the bigger story", r"the real story", r"customer[ -]visible progress",
]

EXPRESSIVE = [
    r"aggressive(?:ly)?", r"significant(?:ly)?", r"massive(?:ly)?", r"huge(?:ly)?", r"critical(?:ly)?",
    r"urgent(?:ly)?", r"dramatic(?:ally)?", r"enormous(?:ly)?", r"tremendous(?:ly)?", r"substantial(?:ly)?",
    r"considerabl[ey]", r"extensive(?:ly)?", r"\bmajor\b", r"largest", r"biggest", r"smallest", r"fastest",
    r"slowest", r"highest", r"lowest", r"drastically", r"immensely", r"incredibly", r"extremely", r"\bvery\b",
    r"\breally\b", r"\bhighly\b", r"rapid(?:ly)?", r"quickly", r"vast(?:ly)?", r"serious(?:ly)?", r"severe(?:ly)?",
    r"important(?:ly)?", r"essential(?:ly)?", r"heav(?:y|ily)", r"a lot", r"\bkey\b(?= [a-z])",
]

VAGUE = [
    r"\bmany\b", r"\bseveral\b", r"numerous", r"\bmultiple\b", r"a number of", r"\ba few\b", r"\bfew\b",
    r"most of", r"the most", r"majority", r"\bvarious\b", r"a couple of", r"\bplenty\b", r"countless",
    r"a handful", r"\bsome of\b",
]

ABSOLUTE = [
    r"\bentire\b", r"\bwhole\b", r"every known", r"all remaining", r"completely", r"\bfully\b",
    r"end[ -]to[ -]end", r"\beverything\b", r"\balways\b", r"\bnever\b", r"\ball of the\b", r"\bevery\b",
]

RELATIVE_TIME = [
    r"last week'?s (?:proposal|plan|fix|change|report|analysis|decision)", r"\bearlier\b", r"previously", r"recently",
    r"a while ago", r"yesterday", r"tomorrow", r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    r"the other day",
]
MONTH_RE = re.compile(r"\b(?:January|February|March|April|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)\b")

LATIN = [r"\be\.g\.", r"\bi\.e\.", r"\betc\.?", r"\bvs\.?\b", r"\bcf\.", r"\bviz\.", r"\bet al\b", r"\bvia\b", r"\bper se\b"]

ING_NOUNS = {
    "during", "nothing", "something", "anything", "everything", "thing", "things", "morning", "evening",
    "string", "ring", "bring", "spring", "king", "wing", "sing", "meeting", "building", "ceiling", "warning",
    "setting", "settings", "sibling", "ongoing", "upcoming", "incoming", "outgoing", "existing", "remaining",
}

MONTHS = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
DATE_RE = re.compile(
    rf"\b(?:0?[1-9]|[12]\d|3[01])/(?:0[1-9]|1[0-2])(?:/\d{{2,4}})?\b|\b\d{{4}}-\d{{2}}-\d{{2}}\b"
    rf"|\b\d{{1,2}} (?:{MONTHS})[a-z]*\b|\b(?:{MONTHS})[a-z]* \d{{1,2}}\b", re.I)
FRACTION_RE = re.compile(r"\(\d+/\d+\)")  # (done/total) in a Progress cell is not a date
DIGIT_RE = re.compile(r"\d")
TICKET_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,9}-\d+\b")
VERSION_RE = re.compile(r"\b\d+(?:\.\d+){1,3}(?:-\d+)?\b")

SLITE_ID = re.compile(r"\s*\{/\*\s*#[^}]*\*/\}")
MD_LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML_A = re.compile(r"<a\b[^>]*>(.*?)</a>", re.S)
HTML_TAG = re.compile(r"<[^>]+>")
URL_RE = re.compile(r"https?://\S+")
CODE_SPAN = re.compile(r"`[^`]+`")
BOLD = re.compile(r"\*\*(.+?)\*\*")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F000-\U0001F2FF]")
IDENT_RE = re.compile(r"\b[a-z]+_[a-z0-9_]+\b|\b[a-z]+[A-Z][A-Za-z0-9]+\b|(?<!\w)/[\w.-]+(?:/[\w.-]+)+|\b\w+\(\)")
IDENT_ALLOW = {"cPanel", "iOS", "macOS", "eBay", "iPhone", "cPanel/WHM"}
PLACEHOLDER_RE = re.compile(r"\[\?\]|\bTODO\b|\bTBD\b|\bXXX\b|paste-link|\{date\}|\bdd/mm/yy\b|\[none\]|\[no epic in progress\]|\?\?\?")

# ------------------------------------------------------------------------- model


@dataclass
class Finding:
    severity: str
    rule: str
    line: int
    message: str
    excerpt: str


class Linter:
    def __init__(self, text: str):
        self.raw_lines = text.splitlines()
        self.findings: list[Finding] = []
        self.doc_clean = "\n".join(self.clean(l) for l in self.raw_lines)
        self.seen_acronyms: set[str] = set()
        self.epic_warned = False

    # ---- helpers
    def add(self, sev: str, rule: str, line: int, msg: str, excerpt: str = "") -> None:
        self.findings.append(Finding(sev, rule, line, msg, excerpt.strip()[:110]))

    @staticmethod
    def clean(line: str) -> str:
        s = SLITE_ID.sub("", line)
        s = HTML_A.sub(r"\1", s)
        s = HTML_TAG.sub("", s)
        s = MD_LINK.sub(r"\1", s)
        s = URL_RE.sub("", s)
        s = html.unescape(s)
        s = s.replace("**", "").replace("__", "")
        s = re.sub(r"(?<![\w*])\*(?!\s|\*)([^*\n]+?)\*(?![\w*])", r"\1", s)
        s = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", s)
        return s.strip()

    @staticmethod
    def sentences(text: str) -> list[str]:
        t = re.sub(r"(\d)\.(\d)", r"\1<D>\2", text)
        t = re.sub(r"\b(e\.g|i\.e|etc|vs|cf|approx|no)\.", lambda m: m.group(0).replace(".", "<D>"), t, flags=re.I)
        parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])", t)
        return [p.replace("<D>", ".").strip() for p in parts if p.strip()]

    @staticmethod
    def words(s: str) -> list[str]:
        return re.findall(r"[A-Za-z0-9][A-Za-z0-9'’/\-]*", s)

    @staticmethod
    def label_of(line: str) -> tuple[str, str] | None:
        s = SLITE_ID.sub("", line).strip()
        m = re.match(r"^\*\*([^*]+?)\*\*:?\s*(.*)$", s)
        if not m:
            return None
        label = m.group(1).rstrip(":").strip().lower()
        for t in TEMPLATE_LABELS:
            if label.startswith(t):
                return t, m.group(2).strip()
        return None

    # ---- word-level rules on one cleaned string
    def word_rules(self, ln: int, clean: str, raw: str, block: str, in_table: bool = False) -> None:
        low = clean.lower()
        for pat, fix in SLANG.items():
            for m in re.finditer(rf"\b(?:{pat})\b", clean, re.I):
                self.add("ERROR", "slang", ln, f'"{m.group(0)}": {fix}', clean)
        for pat, fix in JARGON.items():
            for m in re.finditer(rf"\b(?:{pat})\b", clean, re.I):
                if pat == r"\bepic\b":
                    if in_table or block.startswith("epics") or self.epic_warned:
                        continue
                    self.epic_warned = True
                self.add("WARN", "jargon", ln, f'"{m.group(0)}": {fix}', clean)
        for pat in AI_WORDS:
            for m in re.finditer(rf"\b(?:{pat})\b", clean, re.I):
                self.add("WARN" if in_table else "ERROR", "ai-vocabulary", ln, f'"{m.group(0)}": plain word or delete (unslop 7/23/26)', clean)
        for pat in LATIN:
            for m in re.finditer(pat, clean, re.I):
                self.add("ERROR", "latin", ln, f'"{m.group(0)}": STE has no Latin abbreviations; write "for example", "that is", "and more", "through"', clean)
        if ";" in clean:
            self.add("ERROR", "semicolon", ln, "STE: no semicolons; make two sentences", clean)
        if "—" in clean and not (in_table and clean.strip() == "—"):
            self.add("ERROR", "em-dash", ln, "no em dashes (unslop 13); end the sentence or use a comma; list items use 'KEY: title'", clean)
        if re.search(r"\s–\s|\s-\s", clean) and not in_table:
            self.add("WARN", "dash", ln, "dash used as a connector; end the sentence or use a comma", clean)
        if re.search(r"(?<!\w)!(?!\d)", clean):
            self.add("WARN", "exclamation", ln, "no exclamation marks in a status report", clean)
        if EMOJI_RE.search(raw):
            self.add("ERROR", "emoji", ln, "no emoji in the section", clean)
        for m in PLACEHOLDER_RE.finditer(raw):
            self.add("ERROR", "placeholder", ln, f'"{m.group(0)}" must be filled or removed before publishing', clean)
        if re.search(r"\bN/A\b|\bn/a\b", clean):
            self.add("WARN", "na", ln, 'write "None"', clean)
        if CODE_SPAN.search(raw):
            sev = "WARN" if block.startswith("recently") else "ERROR"
            self.add(sev, "code-span", ln, "internal identifier in an executive report: say what it does instead", clean)
        for m in IDENT_RE.finditer(clean):
            tok = m.group(0)
            if TICKET_RE.fullmatch(tok) or VERSION_RE.fullmatch(tok) or tok in IDENT_ALLOW:
                continue
            sev = "WARN" if block.startswith("recently") else "ERROR"
            self.add(sev, "identifier", ln, f'"{tok}" looks like code, a path or a flag: describe the behaviour instead', clean)
        # numbers without thousands separators (skip keys, versions, years, MR refs)
        scrub = TICKET_RE.sub(" ", VERSION_RE.sub(" ", clean))
        scrub = re.sub(r"!\d+", " ", scrub)
        for m in re.finditer(r"(?<![\d,.])\d{4,}(?![\d,.%])", scrub):
            n = int(m.group(0))
            if 1900 <= n <= 2099:
                continue
            self.add("WARN", "number-format", ln, f'"{m.group(0)}": use a thousands separator ({n:,})', clean)
        if in_table:
            for m in DATE_RE.finditer(FRACTION_RE.sub(" ", clean)):
                self.add("ERROR", "date-in-prose", ln, f'"{m.group(0)}": no dates in the name or Progress cell; write a duration ("paused 2 weeks")', clean)
        # acronyms
        self.acronyms(ln, clean, raw, block, in_table)

    def acronyms(self, ln: int, clean: str, raw: str, block: str, in_table: bool) -> None:
        text = CODE_SPAN.sub(" ", clean)
        for m in re.finditer(r"\b([A-Z][A-Z0-9]{1,6})\b", text):
            acr = m.group(1)
            if acr in ALLOWED_ACRONYMS or acr in self.seen_acronyms:
                continue
            if re.match(r"^[IVXLC]+$", acr):
                continue
            after = text[m.end():m.end() + 2]
            before = text[max(0, m.start() - 1):m.start()]
            if after.startswith("-") and re.match(r"-\d", text[m.end():m.end() + 2]):
                continue  # ticket key
            if before == "-" or before == "!":
                continue
            if acr.isdigit():
                continue
            self.seen_acronyms.add(acr)
            expanded = re.search(rf"\({re.escape(acr)}\)", self.doc_clean) or \
                re.search(rf"\b{re.escape(acr)} \(", self.doc_clean)
            if expanded:
                continue
            self.add("ERROR", "acronym", ln,
                     f'"{acr}" is not expanded anywhere: write the words, then "({acr})" on first use, or use the plain word',
                     clean)

    # ---- sentence-level rules
    def sentence_rules(self, ln: int, clean: str, block: str) -> None:
        sents = self.sentences(clean)
        if len(sents) > 6:
            self.add("ERROR", "paragraph-length", ln, f"{len(sents)} sentences in one paragraph; STE allows 6", clean)
        for s in sents:
            n = len(self.words(s))
            if n > 25:
                self.add("ERROR", "sentence-length", ln, f"{n} words; STE descriptive limit is 25. Split it.", s)
            s_nokeys = re.sub(r"!\d+", " ", TICKET_RE.sub(" ", s))
            has_digit = bool(DIGIT_RE.search(s_nokeys))
            eta_sentence = bool(re.search(r"\bETA\b|\bdue\b|\bdeadline\b", s, re.I))
            for m in DATE_RE.finditer(FRACTION_RE.sub(" ", s)):
                if not eta_sentence:
                    self.add("ERROR", "date-in-prose", ln,
                             f'"{m.group(0)}": no calendar dates in the text. Delivery takes a week or more, so the day a change merged is noise. Say the stage: merged, in review, in beta, on all servers. Dates live in the ETA column only.', s)
            for m in MONTH_RE.finditer(s):
                if not eta_sentence:
                    self.add("WARN", "date-in-prose", ln, f'"{m.group(0)}": a month name is a date; say the stage instead', s)
            for pat in EXPRESSIVE:
                for m in re.finditer(rf"\b(?:{pat})\b", s, re.I):
                    w = m.group(0)
                    if w.lower().startswith("critical") and re.search(r"priority", s, re.I):
                        continue
                    if not has_digit:
                        self.add("ERROR", "expressive", ln,
                                 f'"{w}" with no number in the same sentence: give the number or use a neutral word', s)
            for pat in VAGUE:
                for m in re.finditer(rf"(?:{pat})", s, re.I):
                    if not has_digit:
                        self.add("ERROR", "vague-quantity", ln,
                                 f'"{m.group(0)}": how many? 5 or 5,000? Give the number.', s)
            for pat in ABSOLUTE:
                for m in re.finditer(rf"(?:{pat})", s, re.I):
                    if not has_digit:
                        self.add("WARN", "absolute-claim", ln,
                                 f'"{m.group(0)}": only if you counted this run; give the count (Aug 23: "all subtasks done" was false)', s)
            for pat in RELATIVE_TIME:
                for m in re.finditer(rf"(?:{pat})", s, re.I):
                    self.add("WARN", "relative-time", ln,
                             f'"{m.group(0)}": the reader did not read the previous report. Say the thing itself, not when it was.', s)
            # -ing forms: sentence-initial participle, or progressive/gerund after a helper
            first = self.words(s)[0] if self.words(s) else ""
            if first.lower().endswith("ing") and first.lower() not in ING_NOUNS and len(first) > 5:
                self.add("WARN", "ing-form", ln,
                         f'"{first}": STE avoids -ing verb forms. Write "We started X" or "X is in progress".', s)
            for m in re.finditer(r"\b(is|are|was|were|be|been|being|while|by|after|before|when|keep|keeps|kept|stop|stops|start|starts|started)\s+(\w+ing)\b", s, re.I):
                if m.group(2).lower() in ING_NOUNS:
                    continue
                self.add("WARN", "ing-form", ln, f'"{m.group(0)}": use a simple tense (we did X / X does Y)', s)
            for m in re.finditer(r"\b(is|are|was|were|been|be|being)\s+(?:(?:not|now|also|still|already|then)\s+)?(\w+ed|built|done|made|sent|lost|found|kept|held|shown|seen|written|taken|given|known|set|put|cut|hit|left|met|read|run|split|spent|begun|broken|chosen|driven|frozen|hidden|merged|paid|told|understood)\b", s, re.I):
                if m.group(2).lower() in {"needed", "expected", "scheduled", "planned", "closed", "done"}:
                    continue
                self.add("WARN", "passive", ln, f'"{m.group(0)}": name the actor (we merged X, the server rejected Y)', s)
        if block == "this week":
            nokeys = re.sub(r"!\d+", " ", TICKET_RE.sub(" ", clean))
            if not DIGIT_RE.search(nokeys):
                self.add("WARN", "no-number", ln,
                         "no number anywhere in this bullet: how much, how many, at what stage? ('the most machines' — is it 5, or 5,000?)", clean)

    # ---- block shapes
    def check_completed_bullet(self, ln: int, raw: str) -> None:
        s = SLITE_ID.sub("", raw).strip()
        if re.match(r"^-\s+\*?_?none_?\*?$", s, re.I):
            return
        m = re.match(r"^-\s+(?:\[([A-Z][A-Z0-9]+-\d+)\]\(https?://[^)]+\)|([A-Z][A-Z0-9]+-\d+)):\s+(.+)$", s)
        if not m:
            self.add("ERROR", "completed-shape", ln,
                     'a completed item is "- [KEY](url): plain title", one line. No dash, no description, no numbers.', s)
            return
        title = self.clean(m.group(3))
        if len(self.words(title)) > 15:
            self.add("ERROR", "completed-length", ln, f"{len(self.words(title))} words after the key; keep the title to 15", title)
        if len(self.sentences(title)) > 1 or re.search(r"[.;] ", title):
            self.add("ERROR", "completed-description", ln, "one title, not a description; details belong in This week", title)
        if URL_RE.search(m.group(3)) or MD_LINK.search(m.group(3)):
            self.add("ERROR", "completed-links", ln, "only the ticket link; merge request links go to This week", s)

    def check_table(self, rows: list[tuple[int, str]], label: str) -> None:
        parsed = []
        for ln, raw in rows:
            cells = [c.strip() for c in SLITE_ID.sub("", raw).strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c) and cells:
                continue
            parsed.append((ln, cells))
        if len(parsed) < 2:
            self.add("ERROR", "table-empty", rows[0][0] if rows else 0, f'the "{label}" table has no rows', "")
            return
        header = [h.lower() for h in parsed[0][1]]

        def col(name):
            for i, h in enumerate(header):
                if h.startswith(name):
                    return i
            return None

        c_key = next((c for c in (col("jira"), col("tracker"), col("ticket"),
                                  col("issue key"), col("key")) if c is not None), None)
        c_name, c_jira, c_status, c_prog, c_eta = (col("epic") if col("epic") is not None else col("issue"),
                                                    c_key, col("status"), col("progress"), col("eta"))
        for ln, cells in parsed[1:]:
            get = lambda i: cells[i] if i is not None and i < len(cells) else ""
            name, jira, status, prog, eta = get(c_name), get(c_jira), get(c_status), get(c_prog), get(c_eta)
            cn = self.clean(name)
            if re.search(r"\[no epic|\[none\]", cn, re.I):
                self.add("ERROR", "table-placeholder", ln, "placeholder row still present", cn)
                continue
            if len(self.words(cn)) > 8:
                self.add("ERROR", "table-name", ln, f"{len(self.words(cn))} words in the name cell; name only (max 8), the explanation goes to This week", cn)
            if re.search(r" — | – |: | - ", cn):
                self.add("ERROR", "table-name", ln, "no explanatory clause in the name cell", cn)
            if not (re.search(r"\[[A-Z][A-Z0-9]+-\d+\]\(https?://", jira) or HTML_A.search(jira) or jira.strip() == "—"):
                self.add("ERROR", "table-jira", ln, "the key cell must be a linked tracker key", jira)
            if len(self.words(self.clean(status))) > 3:
                self.add("ERROR", "table-status", ln, "Status is the tracker's status word (Development, In Rollout, Done)", status)
            if DATE_RE.search(self.clean(status)):
                self.add("ERROR", "table-status", ln, "no date in the Status cell; the word only", status)
            cp = self.clean(prog)
            if not re.fullmatch(r"(\d{1,3}% \(\d+/\d+\)(, [^,]{1,40})?|\d{1,3}%(, [^,]{1,40})?|—|\[\?\])", cp):
                self.add("ERROR", "table-progress", ln,
                         'Progress is "NN% (done/total)" plus at most six words after a comma, not text', cp)
            elif len(cp) > 45:
                self.add("ERROR", "table-progress", ln, "Progress note longer than six words", cp)
            ce = self.clean(eta)
            if not re.fullmatch(r"\d{2}/\d{2}/\d{2,4}|—|\[\?\]", ce):
                self.add("ERROR", "table-eta", ln, "ETA is dd/mm/yy from the epic's due date; ask, never guess", ce)
            self.word_rules(ln, cn, name, "epics", in_table=True)
            self.word_rules(ln, cp, prog, "epics", in_table=True)

    # ---- driver
    def run(self) -> list[Finding]:
        block = "preamble"
        table_rows: list[tuple[int, str]] = []
        table_label = ""
        counts = {"recently completed": 0, "this week": 0, "next week": 0}
        completed_titles: list[str] = []
        this_week_text: list[str] = []
        prev_blank = True
        para_start, para_lines = None, []

        def flush_para():
            nonlocal para_start, para_lines
            if para_start is not None and para_lines:
                joined = " ".join(self.clean(l) for l in para_lines)
                self.sentence_rules(para_start, joined, block)
            para_start, para_lines = None, []

        def flush_table():
            nonlocal table_rows, table_label
            if table_rows:
                self.check_table(table_rows, table_label)
            table_rows = []

        for i, raw in enumerate(self.raw_lines, 1):
            s = SLITE_ID.sub("", raw).rstrip()
            if not s.strip():
                flush_para(); flush_table(); prev_blank = True
                continue
            if s.strip().startswith("|"):
                flush_para()
                table_rows.append((i, s))
                table_label = block
                continue
            flush_table()
            if s.startswith("### ") or s.startswith("<separator") or s.strip() in {"---", "***"}:
                flush_para(); block = "heading"; continue
            lab = self.label_of(s)
            if lab:
                flush_para()
                block, trailing = lab
                if block == "blockers":
                    if trailing and not re.fullmatch(r"None\.?", trailing.strip()):
                        self.blocker_text(i, trailing)
                        self.word_rules(i, self.clean(trailing), trailing, block)
                        self.sentence_rules(i, self.clean(trailing), block)
                elif trailing and block in counts:
                    counts[block] += 1
                    self.word_rules(i, self.clean(trailing), trailing, block)
                    self.sentence_rules(i, self.clean(trailing), block)
                continue
            if block in ("heading", "owner"):
                continue
            clean = self.clean(s)
            is_bullet = bool(re.match(r"^\s*(?:[-*+]|\d+\.)\s+", s))
            if block == "recently completed":
                counts[block] += 1
                if is_bullet:
                    self.check_completed_bullet(i, s)
                    m = re.match(r"^-\s+(?:\[[^\]]+\]\([^)]+\)|[A-Z]+-\d+):\s+(.+)$", s.strip())
                    if m:
                        completed_titles.append(self.clean(m.group(1)).lower())
                else:
                    self.add("ERROR", "completed-shape", i, "Recently completed is a bullet list of tickets only", clean)
                self.word_rules(i, clean, s, block)
                continue
            if block in counts:
                counts[block] += 1
            if block == "this week":
                this_week_text.append(clean.lower())
            if is_bullet and re.match(r"^\s*[-*+]\s+\*\*[^*]+:?\*\*:?", s):
                self.add("ERROR", "inline-header", i, 'bold label with a colon at the start of a bullet (unslop 16): write prose', clean)
            if len(BOLD.findall(s)) > 1:
                self.add("WARN", "bold", i, "more than one bold span in a line; bold is for the template labels", clean)
            if block == "next week" and is_bullet:
                if not (TICKET_RE.search(clean) or MD_LINK.search(s) or HTML_A.search(s)):
                    self.add("WARN", "next-week-link", i, "no ticket behind this plan; link the ticket or drop the plan", clean)
                if re.match(r"^(continue|keep|ongoing|more)\b", clean, re.I):
                    self.add("WARN", "next-week-vague", i, 'say which part: "Finish X (2 of 5 parts left)"', clean)
            if block == "blockers":
                self.blocker_text(i, clean)
                self.word_rules(i, clean, s, block)
                continue
            self.word_rules(i, clean, s, block)
            if is_bullet or prev_blank:
                flush_para()
                para_start = i
            para_lines.append(s)
            prev_blank = False
        flush_para(); flush_table()

        if counts["this week"] == 0:
            self.add("ERROR", "empty-block", 0, "This week is empty", "")
        if counts["next week"] == 0:
            self.add("ERROR", "empty-block", 0, "Next week is empty", "")
        tw = " ".join(this_week_text)
        tw_words = len(self.words(tw))
        if tw_words > 300:
            self.add("WARN", "this-week-length", 0,
                     f"This week is {tw_words} words; the budget is 150 to 300. Cut mechanism, keep results and numbers.", "")
        for t in completed_titles:
            core = " ".join(self.words(t)[:6]).lower()
            if len(self.words(t)) >= 6 and core in tw:
                self.add("WARN", "duplicate", 0, f'completed title reappears in This week: "{t[:60]}" — the two blocks duplicate each other', "")
        return self.findings

    def blocker_text(self, ln: int, text: str) -> None:
        if re.fullmatch(r"None\.?", text.strip(), re.I):
            return
        if not re.search(r"\b(week|weeks|days|month)\b", text, re.I):
            self.add("WARN", "blocker-duration", ln, "a blocker says for how long (N weeks), on whom, and what unblocks it", text)
        if len(self.words(text)) > 40:
            self.add("WARN", "blocker-length", ln, "a blocker is one line; risks and notes belong in This week", text)


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if not args:
        print(__doc__); sys.exit(2)
    text = sys.stdin.read() if args[0] == "-" else open(args[0], encoding="utf-8").read()
    findings = Linter(text).run()
    errors = [f for f in findings if f.severity == "ERROR"]
    warns = [f for f in findings if f.severity == "WARN"]
    if as_json:
        print(json.dumps([asdict(f) for f in findings], indent=2, ensure_ascii=False))
    else:
        for f in sorted(findings, key=lambda f: (f.severity != "ERROR", f.line, f.rule)):
            loc = f"L{f.line}" if f.line else "L-"
            print(f"{f.severity:<5} {loc:<5} [{f.rule}] {f.message}")
            if f.excerpt:
                print(f"           > {f.excerpt}")
        print(f"\n{len(errors)} errors, {len(warns)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
