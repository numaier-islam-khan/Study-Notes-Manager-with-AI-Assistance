"""
ai_tools.py - AI/NLP powered features for the Study Notes Manager
Provides: title generation, summarization, keyword extraction, quiz generation.
Uses: nltk, rake-nltk, sumy, scikit-learn
"""

import re
import random
import string

# ── NLTK bootstrap ──────────────────────────────────────────────────────────
import nltk

def _download(resource, path):
    try:
        nltk.data.find(path)
    except LookupError:
        nltk.download(resource, quiet=True)

_download("punkt",         "tokenizers/punkt")
_download("punkt_tab",     "tokenizers/punkt_tab")
_download("stopwords",     "corpora/stopwords")
_download("averaged_perceptron_tagger",    "taggers/averaged_perceptron_tagger")
_download("averaged_perceptron_tagger_eng","taggers/averaged_perceptron_tagger_eng")

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus   import stopwords

STOP_WORDS = set(stopwords.words("english"))

# ── Optional imports (graceful degradation) ─────────────────────────────────
try:
    from rake_nltk import Rake
    RAKE_AVAILABLE = True
except ImportError:
    RAKE_AVAILABLE = False

try:
    from sumy.parsers.plaintext   import PlaintextParser
    from sumy.nlp.tokenizers      import Tokenizer
    from sumy.summarizers.lsa     import LsaSummarizer
    SUMY_AVAILABLE = True
except ImportError:
    SUMY_AVAILABLE = False


# ── Title Generation ─────────────────────────────────────────────────────────

def generate_title(content: str) -> str:
    """
    Auto-generate a short title from the note content.
    Strategy: extract the most frequent non-stop nouns/words.
    """
    if not content or not content.strip():
        return "Untitled Note"

    words = word_tokenize(content.lower())
    # Keep only alphabetic words longer than 3 chars that aren't stop words
    filtered = [w for w in words if w.isalpha() and len(w) > 3 and w not in STOP_WORDS]

    if not filtered:
        # Fallback: first 5 words of content
        return " ".join(content.split()[:5]).title()

    # Count frequency
    freq = {}
    for w in filtered:
        freq[w] = freq.get(w, 0) + 1

    # Take top 4 words and title-case them
    top_words = sorted(freq, key=freq.get, reverse=True)[:4]
    return " ".join(w.capitalize() for w in top_words)


# ── Summarization ─────────────────────────────────────────────────────────────

def summarize_text(content: str, num_sentences: int = 3) -> str:
    """
    Generate a concise summary of the note content.
    Uses sumy (LSA) if available, otherwise falls back to extractive method.
    """
    if not content or len(content.strip()) < 50:
        return content.strip()

    if SUMY_AVAILABLE:
        try:
            parser    = PlaintextParser.from_string(content, Tokenizer("english"))
            summarizer = LsaSummarizer()
            sentences  = summarizer(parser.document, num_sentences)
            summary    = " ".join(str(s) for s in sentences)
            return summary if summary.strip() else _fallback_summary(content, num_sentences)
        except Exception:
            pass

    return _fallback_summary(content, num_sentences)


def _fallback_summary(content: str, num_sentences: int = 3) -> str:
    """Simple extractive summary: pick first N sentences."""
    sentences = sent_tokenize(content)
    chosen    = sentences[:num_sentences]
    return " ".join(chosen)


# ── Keyword Extraction ────────────────────────────────────────────────────────

def extract_keywords(content: str, max_keywords: int = 8) -> str:
    """
    Extract important keywords/phrases from the note.
    Uses RAKE if available, otherwise TF-based approach.
    Returns a comma-separated string.
    """
    if not content or len(content.strip()) < 20:
        return ""

    if RAKE_AVAILABLE:
        try:
            rake = Rake()
            rake.extract_keywords_from_text(content)
            phrases = rake.get_ranked_phrases()[:max_keywords]
            # Clean up multi-word phrases
            clean = [p.strip() for p in phrases if len(p.split()) <= 4]
            if clean:
                return ", ".join(clean[:max_keywords])
        except Exception:
            pass

    return _fallback_keywords(content, max_keywords)


def _fallback_keywords(content: str, max_keywords: int = 8) -> str:
    """
    TF-based keyword extraction without RAKE.
    """
    words   = word_tokenize(content.lower())
    filtered = [w for w in words if w.isalpha() and len(w) > 4 and w not in STOP_WORDS]

    freq = {}
    for w in filtered:
        freq[w] = freq.get(w, 0) + 1

    top = sorted(freq, key=freq.get, reverse=True)[:max_keywords]
    return ", ".join(top)


# ── Quiz Generation ───────────────────────────────────────────────────────────

def generate_quiz(content: str) -> dict:
    """
    Generate quiz questions from note content.
    Returns a dict with 'mcq', 'true_false', and 'short' question lists.
    """
    sentences = sent_tokenize(content)
    # Filter short/useless sentences
    usable    = [s.strip() for s in sentences if len(s.split()) >= 6]

    quiz = {
        "mcq":        _generate_mcq(usable, content),
        "true_false":  _generate_true_false(usable),
        "short":       _generate_short(usable),
    }
    return quiz


def _generate_mcq(sentences: list, full_text: str, num: int = 3) -> list:
    """
    Create multiple-choice questions by blanking a key word in a sentence.
    Distractors are random words from the text.
    """
    questions = []
    all_words  = [w for w in word_tokenize(full_text.lower())
                  if w.isalpha() and len(w) > 4 and w not in STOP_WORDS]
    unique_words = list(set(all_words))

    random.shuffle(sentences)
    for sentence in sentences[:num]:
        words = [w for w in word_tokenize(sentence) if w.isalpha() and len(w) > 4 and w not in STOP_WORDS]
        if not words:
            continue
        answer = random.choice(words)
        # Blank the answer in the question
        question_text = sentence.replace(answer, "______", 1)

        # Build 3 wrong options
        distractors = [w for w in unique_words if w != answer.lower()]
        random.shuffle(distractors)
        wrong_options = distractors[:3]

        options = wrong_options + [answer.lower()]
        random.shuffle(options)

        questions.append({
            "question": f"Fill in the blank: {question_text}",
            "options":  [o.capitalize() for o in options],
            "answer":   answer.lower().capitalize()
        })

    return questions


def _generate_true_false(sentences: list, num: int = 3) -> list:
    """
    Create True/False questions. Half are True (original sentence),
    half are False (sentence with a word swapped).
    """
    questions = []
    random.shuffle(sentences)

    for sentence in sentences[:num]:
        if random.random() > 0.5:
            # True question
            questions.append({"question": sentence, "answer": "True"})
        else:
            # False: replace one word to make it incorrect
            words   = sentence.split()
            if len(words) > 5:
                idx    = random.randint(2, len(words) - 2)
                original = words[idx]
                fake_word = original[::-1]  # Reverse the word as a fake
                words[idx] = fake_word
                modified   = " ".join(words)
                questions.append({"question": modified, "answer": "False"})
            else:
                questions.append({"question": sentence, "answer": "True"})

    return questions


def _generate_short(sentences: list, num: int = 3) -> list:
    """
    Generate short-answer questions using Who/What/Why structure.
    """
    starters = [
        "What is the main idea of: ",
        "Explain in your own words: ",
        "Why is the following important: ",
        "Describe what is meant by: ",
        "What do you understand from: ",
    ]
    questions = []
    random.shuffle(sentences)

    for sentence in sentences[:num]:
        starter = random.choice(starters)
        questions.append({
            "question": f"{starter}\"{sentence}\"",
            "hint":     "Answer based on the note content."
        })

    return questions