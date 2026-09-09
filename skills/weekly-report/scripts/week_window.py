#!/usr/bin/env python3
"""Report window for a team weekly status report.

The squad note is titled by ISO week and filled by Thursday midday (Europe).
The window one section covers runs from the previous report day (Thursday)
to the current one.

Usage:
    week_window.py                 # window that ends on the coming/current Thursday
    week_window.py --week 35       # window for ISO week 35 of the current year
    week_window.py --date 2026-08-20   # pretend today is that date
    week_window.py --json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os

THURSDAY = 3  # Monday == 0


def window_for(today: dt.date) -> dict:
    # The report day is the Thursday of today's ISO week. Before Thursday we
    # are writing for it; on Thursday it is due; after Thursday the next one.
    monday = today - dt.timedelta(days=today.weekday())
    report_day = monday + dt.timedelta(days=THURSDAY)
    if today > report_day:
        report_day += dt.timedelta(days=7)
    start = report_day - dt.timedelta(days=7)
    iso_year, iso_week, _ = report_day.isocalendar()
    week_monday = report_day - dt.timedelta(days=THURSDAY)
    week_next_monday = week_monday + dt.timedelta(days=7)
    return {
        "today": today.isoformat(),
        "today_weekday": today.strftime("%A"),
        "report_day": report_day.isoformat(),
        "window_start": start.isoformat(),
        "window_end": report_day.isoformat(),
        "iso_week": iso_week,
        "iso_year": iso_year,
        "slite_week_fragment": f"week {iso_week:02d}",
        "slite_week_title_hint": (
            f"Weekly status report - week {iso_week:02d} - "
            f"{week_monday.strftime('%d-%b')} to {week_next_monday.strftime('%d-%b')}"
        ),
        "squad_note_date_hint": week_monday.strftime("%b %d, %Y"),
        "previous_report_day": start.isoformat(),
        "jql_updated": f'updated >= "{start.isoformat()}"',
        "jql_resolved": f'resolved >= "{start.isoformat()}"',
        "state_dir": os.path.expanduser(
            f"~/.local/state/weekly-report/{iso_year}-W{iso_week:02d}"
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--week", type=int, help="ISO week number (current ISO year)")
    p.add_argument("--date", help="pretend today is YYYY-MM-DD")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    today = dt.date.fromisoformat(a.date) if a.date else dt.date.today()
    if a.week:
        today = dt.date.fromisocalendar(today.isocalendar()[0], a.week, THURSDAY + 1)
    w = window_for(today)
    if a.json:
        print(json.dumps(w, indent=2))
        return
    width = max(len(k) for k in w)
    for k, v in w.items():
        print(f"{k:<{width}}  {v}")


if __name__ == "__main__":
    main()
