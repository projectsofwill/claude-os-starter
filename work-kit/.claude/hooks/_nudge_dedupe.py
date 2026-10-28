#!/usr/bin/env python3
"""Session-scoped once-per-session dedupe for non-blocking nudge hooks.

Shared by stop_milestone_check.py and pretooluse_okf_nav_nudge.py so a nudge
fires at most once per (session, subkey) instead of on EVERY Stop / EVERY
Grep-Glob into an indexed dir. Motivation: the lessening audit (2026-07-06)
counted the Stop nudge firing 284× (up to 33×/session) and the OKF nav nudge
126× — pure agent-context noise with near-zero added signal after the first fire.

Keyed by the `session_id` the harness puts in every hook's stdin payload; a
zero-byte marker file in the system temp dir records that this (kind, session,
subkey) already fired. A fresh session -> a fresh session_id -> a fresh marker,
so the nudge fires once again in the next session.

FAIL OPEN: any error, or a missing session_id, returns True (fire the nudge),
preserving the original always-fire behavior rather than silently suppressing a
guard. Never raises.
"""

import hashlib
import os
import tempfile


def _h(value, length):
    return hashlib.sha1(str(value).encode("utf-8", "ignore")).hexdigest()[:length]


def should_fire(kind, session_id, subkey=""):
    """Return True the FIRST time (kind, session_id, subkey) is seen, else False.

    kind        short label for the nudge (e.g. "changelog", "okf-nav").
    session_id  from the hook stdin payload; falsy -> always fire (can't dedupe).
    subkey      optional discriminator (e.g. a target dir) so distinct targets
                each get one nudge within a session.
    """
    try:
        if not session_id:
            return True  # no session handle -> preserve old always-fire behavior
        name = "claude_nudge_%s_%s" % (kind, _h(session_id, 16))
        if subkey:
            name += "_" + _h(subkey, 12)
        marker = os.path.join(tempfile.gettempdir(), name + ".flag")
        # Atomic create-if-absent; losing the race counts as already-fired.
        try:
            fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
        except FileExistsError:
            return False
        return True
    except Exception:
        return True  # fail open — a dedupe bug must never suppress the guard
