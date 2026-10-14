"""The unfinished melody (plan B12): a match result rendered as sound. Pure Python, no I/O.

One note per condition, in condition order, with the completion step always last:
- a condition that holds plays its note;
- an absence (∅) that holds is a short rest: silence is the finding;
- a condition that doesn't hold is a rest;
- the completion step, when it hasn't happened, is a HELD silence: four notes, then nothing
  where the fifth should be. resolve=True plays it, so you hear what completing it sounds like.
The tension notes climb towards the leading tone; the completion note is the tonic that
resolves the phrase. The sound carries no information that isn't in the match result.
"""
import hashlib
import io
import math
import struct
import wave

RATE = 44_100          # samples per second
NOTE_S = 0.34          # one note
REST_S = 0.17          # a short rest (an absence that holds)
HELD_S = 0.9           # the held breath where the completion note should be
FADE_S = 0.010         # 10 ms fades: no clicks between notes
TENSION = [-10, -8, -5, -3, -1]   # semitones below the tonic: D, E, G, A, B (major, leading tone last)
KEY_SHIFTS = [0, 2, 4, 5, 7]      # each lesson gets its own key, chosen deterministically


def _tonic(lesson_id):
    shift = KEY_SHIFTS[int(hashlib.sha256(lesson_id.encode()).hexdigest(), 16) % len(KEY_SHIFTS)]
    return 523.25 * 2 ** (shift / 12)          # C5, transposed


def melody_events(lesson_id, states, completion_index, resolve=False):
    """states: [(holds, is_absence)] in condition order. Returns [(kind, freq, seconds)]."""
    tonic = _tonic(lesson_id)
    others = [s for i, s in enumerate(states) if i != completion_index]
    steps = TENSION[-len(others):] if others else []
    events = []
    for (holds, absence), semis in zip(others, steps):
        if holds and not absence:
            events.append(("note", tonic * 2 ** (semis / 12), NOTE_S))
        elif holds and absence:
            events.append(("rest", 0.0, REST_S))
        else:
            events.append(("rest", 0.0, NOTE_S))
    completion_holds = states[completion_index][0]
    if completion_holds or resolve:
        events.append(("note", tonic, NOTE_S * 2))
    else:
        events.append(("held", 0.0, HELD_S))
    return events


def melody_wav(events):
    """Render events as 16-bit mono WAV bytes (a soft sine with two overtones and a decay)."""
    frames = bytearray()
    fade = int(FADE_S * RATE)
    for kind, freq, seconds in events:
        n = int(seconds * RATE)
        for i in range(n):
            if kind != "note":
                frames += b"\x00\x00"
                continue
            t = i / RATE
            wave_val = (0.62 * math.sin(2 * math.pi * freq * t)
                        + 0.25 * math.sin(4 * math.pi * freq * t)
                        + 0.08 * math.sin(6 * math.pi * freq * t))
            env = math.exp(-2.2 * t / seconds) * min(1.0, i / fade, (n - 1 - i) / fade)
            frames += struct.pack("<h", int(0.32 * 32767 * wave_val * env))
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(bytes(frames))
    return buf.getvalue()
