"""
predict.py  –  ML utilities for BlogVerse
Currently provides: keyword extraction and readability-score estimation.
Replace / extend with a real trained model (model.pkl) when available.
"""
import re
import math


def count_words(text: str) -> int:
    return len(text.split())


def estimate_readability(text: str) -> dict:
    """
    Simple Flesch–Kincaid–style readability estimate.
    Returns a dict with score (0–100) and label.
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words     = text.split()
    syllables = sum(_syllable_count(w) for w in words)

    if not sentences or not words:
        return {'score': 0, 'label': 'N/A'}

    asl = len(words) / len(sentences)       # avg sentence length
    asw = syllables / len(words)            # avg syllables per word
    score = max(0, min(100, 206.835 - 1.015 * asl - 84.6 * asw))

    if score >= 70:
        label = 'Easy to read'
    elif score >= 50:
        label = 'Moderate'
    else:
        label = 'Complex'

    return {'score': round(score, 1), 'label': label}


def extract_keywords(text: str, top_n: int = 5) -> list:
    """
    Naive keyword extractor – filters stop words and returns
    the most frequent meaningful words.
    """
    STOP = {
        'the','a','an','is','in','it','of','and','to','for','that',
        'this','was','are','be','as','at','by','from','or','but','with',
        'on','not','have','has','had','they','we','he','she','you','i',
        'my','our','their','its','which','who','will','would','could',
        'should','can','do','does','did','been','were','what','how'
    }
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    freq  = {}
    for w in words:
        if w not in STOP:
            freq[w] = freq.get(w, 0) + 1
    sorted_kw = sorted(freq, key=freq.get, reverse=True)
    return sorted_kw[:top_n]


def _syllable_count(word: str) -> int:
    word = word.lower().strip(".,!?;:'\"")
    vowels = 'aeiouy'
    count  = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith('e') and count > 1:
        count -= 1
    return max(1, count)


# ─── Quick demo ────────────────────────────────────────────────
if __name__ == '__main__':
    sample = (
        "Flask is a lightweight web framework for Python. "
        "It is easy to learn and suitable for small to medium web applications. "
        "Flask provides routing, templating with Jinja2, and session management."
    )
    print("Words       :", count_words(sample))
    print("Readability :", estimate_readability(sample))
    print("Keywords    :", extract_keywords(sample))
