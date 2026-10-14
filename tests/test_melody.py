"""T32: the melody is a direct rendering of the match result (plan B12)."""
import io
import wave

from nodus.melody import NOTE_S, RATE, melody_events, melody_wav

# hero x antibody-1: four hold (one is an absence), the completion (index 4) is missing
STATES = [(True, False), (True, False), (True, True), (True, False), (False, False)]


def kinds(events):
    return [e[0] for e in events]


def test_one_event_per_condition_with_completion_last():
    ev = melody_events("antibody-1", STATES, completion_index=4)
    assert len(ev) == 5
    assert kinds(ev) == ["note", "note", "rest", "note", "held"]   # absence = rest; completion held


def test_resolve_plays_the_completion_as_the_tonic():
    ev = melody_events("antibody-1", STATES, completion_index=4, resolve=True)
    assert ev[-1][0] == "note"
    tonic = ev[-1][1]
    assert all(e[1] < tonic for e in ev[:-1] if e[0] == "note")    # the phrase climbs to it


def test_missing_non_completion_condition_is_silent():
    states = [(True, False), (False, False), (True, False), (True, False), (False, False)]
    assert kinds(melody_events("x", states, 4))[1] == "rest"


def test_completion_is_last_even_if_listed_earlier():
    states = [(False, False), (True, False), (True, False)]
    ev = melody_events("x", states, completion_index=0)
    assert ev[-1][0] == "held"


def test_wav_length_matches_the_events():
    ev = melody_events("antibody-1", STATES, 4)
    with wave.open(io.BytesIO(melody_wav(ev))) as w:
        assert w.getframerate() == RATE and w.getnchannels() == 1
        assert w.getnframes() == sum(int(d * RATE) for _, _, d in ev)


def test_held_note_is_true_silence_and_notes_start_softly():
    ev = melody_events("antibody-1", STATES, 4)
    with wave.open(io.BytesIO(melody_wav(ev))) as w:
        frames = w.readframes(w.getnframes())
    samples = [int.from_bytes(frames[i:i + 2], "little", signed=True) for i in range(0, len(frames), 2)]
    held = int(ev[-1][2] * RATE)
    assert all(s == 0 for s in samples[-held:])                    # the fifth note: silence
    assert abs(samples[0]) < 50 and max(map(abs, samples)) > 3000   # faded in, but audible


def test_same_input_same_bytes():
    ev = melody_events("antibody-1", STATES, 4)
    assert melody_wav(ev) == melody_wav(melody_events("antibody-1", STATES, 4))
    assert NOTE_S > 0
