"""Extraction d'entites bilingue : annee, mois, depot."""

import re

from chatbot.intent_detector import normalize_text


MOIS_MAP = {
    "janvier": 1, "january": 1, "jan": 1,
    "fevrier": 2, "february": 2, "feb": 2,
    "mars": 3, "march": 3, "mar": 3,
    "avril": 4, "april": 4, "apr": 4,
    "mai": 5, "may": 5,
    "juin": 6, "june": 6, "jun": 6,
    "juillet": 7, "july": 7, "jul": 7,
    "aout": 8, "august": 8, "aug": 8,
    "septembre": 9, "september": 9, "sep": 9, "sept": 9,
    "octobre": 10, "october": 10, "oct": 10,
    "novembre": 11, "november": 11, "nov": 11,
    "decembre": 12, "december": 12, "dec": 12,
}


def extract_year(text: str):
    """Extrait une annee 2015-2018 depuis le texte."""
    match = re.search(r"\b(201[5-8])\b", text)
    return int(match.group(1)) if match else None


def extract_month(text: str):
    """Extrait un numero de mois (1-12) depuis le texte."""
    t = normalize_text(text)
    for name, num in MOIS_MAP.items():
        if re.search(rf"\b{re.escape(name)}\b", t):
            return num
    numeric_match = re.search(r"\bmonth\s*(\d{1,2})\b|\bmois\s*(\d{1,2})\b", t)
    if numeric_match:
        month = int(numeric_match.group(1) or numeric_match.group(2))
        if 1 <= month <= 12:
            return month
    return None


def extract_depot(text: str):
    """Extrait un code depot numerique depuis le texte."""
    t = normalize_text(text)
    match = re.search(
        r"\bdepot\s*(?:n|no|num|numero|number)?\s*\.?\s*(\d+)\b|"
        r"\bwarehouse\s*(?:n|no|num|number)?\s*\.?\s*(\d+)\b",
        t,
    )
    if match:
        return int(match.group(1) or match.group(2))
    return None
