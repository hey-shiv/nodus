"""B2: the keyword baseline (TF-IDF cosine), the "ordinary search" NODUS is compared with.

Pure Python, no dependencies. Declared in eval/DECLARATION.md before it was run.
"""
import math
import re
from collections import Counter

STOPWORDS = set("""a an and are as at be because been but by for from had has have in into is it
its of on or that the their them then there these this to was were which while will with
without would same so not no all any every one other than""".split())


def tokens(text):
    return [w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOPWORDS and len(w) > 1]


def lesson_text(lesson):
    """Everything a text search could know about a lesson, from data/lessons/."""
    parts = [lesson.name, lesson.summary, lesson.safe_pattern]
    for c in lesson.conditions:
        parts.append(c.text)
        parts.extend(cit.quote for cit in c.citations)
    return " ".join(parts)


class TfIdf:
    def __init__(self, corpus):
        self.n = len(corpus)
        df = Counter()
        for doc in corpus:
            df.update(set(tokens(doc)))
        self.idf = {w: math.log((1 + self.n) / (1 + d)) + 1 for w, d in df.items()}

    def vector(self, text):
        tf = Counter(tokens(text))
        return {w: c * self.idf.get(w, math.log(1 + self.n) + 1) for w, c in tf.items()}

    def similarity(self, a, b):
        va, vb = self.vector(a), self.vector(b)
        dot = sum(va[w] * vb.get(w, 0) for w in va)
        na = math.sqrt(sum(v * v for v in va.values()))
        nb = math.sqrt(sum(v * v for v in vb.values()))
        return dot / (na * nb) if na and nb else 0.0
