"""Extraction d'entités : année, mois, dépôt."""
import re

MOIS_MAP = {
    "janvier": 1,
    "février": 2, "fevrier": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "août": 8, "aout": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "décembre": 12, "decembre": 12,
}


def extract_year(text: str):
    """Extrait une année 2015–2018 depuis le texte."""
    match = re.search(r"\b(201[5-8])\b", text)
    return int(match.group(1)) if match else None


def extract_month(text: str):
    """Extrait un numéro de mois (1–12) depuis le texte."""
    t = text.lower()
    for name, num in MOIS_MAP.items():
        if name in t:
            return num
    return None


def extract_depot(text: str):
    """Extrait un code dépôt numérique depuis le texte."""
    match = re.search(r"\bdép[oô]t\s*n?°?\s*(\d+)\b|\bdepot\s*n?°?\s*(\d+)\b", text.lower())
    if match:
        return int(match.group(1) or match.group(2))
    return None
