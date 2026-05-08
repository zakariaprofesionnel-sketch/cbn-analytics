"""Detection d'intention bilingue par mots-cles (francais / anglais)."""

import re
import unicodedata


def normalize_text(text: str) -> str:
    """Normalise un texte pour comparer les mots-cles avec ou sans accents."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[-_']", " ", text)
    return re.sub(r"\s+", " ", text)


# Ordre = priorite decroissante : les intents specifiques avant les generiques.
INTENT_KEYWORDS = {
    "aide": [
        "aide", "help", "what can you do", "what questions", "commands",
        "bonjour", "salut", "hello", "hi", "how can you help",
        "que peux-tu", "que sais-tu", "quelles questions", "quoi faire",
        "quelles commandes", "que peux tu faire", "que sais tu faire",
        "que peux tu", "que sais tu", "tu sais faire quoi",
        "qu est ce que tu sais faire", "qu est ce que tu peux faire",
        "what do you know", "what can i ask", "show help",
    ],
    "top_depot": [
        "meilleur depot", "top depot", "best depot", "top warehouse",
        "best warehouse", "depot ranking", "warehouse ranking",
        "classement depot", "depot le plus", "premier depot",
        "highest depot", "leading depot", "depots", "warehouses",
        "sold the most", "most sold", "most volume", "highest sales",
    ],
    "tendance": [
        "tendance", "evolution", "croissance", "augmentation", "diminution",
        "hausse", "baisse", "progression", "comparaison annuelle",
        "trend", "growth", "increase", "decrease", "drop", "rise",
        "yearly comparison", "annual comparison", "over time",
    ],
    "brent": [
        "brent", "cours brent", "cours du brent", "petrole",
        "prix du petrole", "baril", "barils", "oil", "oil price",
        "brent price", "crude", "barrel", "barrels",
    ],
    "prix_moyen": [
        "prix moyen", "prix unitaire", "tarif moyen", "cout moyen",
        "prix de vente", "prix du gasoil", "average price", "unit price",
        "selling price", "mean price", "gasoil price", "diesel price",
    ],
    "montant_total": [
        "chiffre d'affaires", "chiffre d affaires", "ca total",
        "montant total", "revenu total", "recette", "montant ht",
        "facturation", "revenus", "revenue", "turnover", "sales amount",
        "total amount", "total revenue", "net sales",
    ],
    "nb_livraisons": [
        "nombre de livraisons", "combien de livraisons", "nb livraisons",
        "livraisons", "nombre livraisons", "number of deliveries",
        "how many deliveries", "deliveries count", "delivery count",
        "deliveries",
    ],
    "volume_total": [
        "volume total", "quantite totale", "total m3", "total des ventes",
        "volume global", "total gasoil", "total volume", "total quantity",
        "overall volume", "total diesel", "total gasoil",
    ],
    "stats": [
        "statistiques", "stats", "resume", "apercu", "vue d'ensemble",
        "bilan", "synthese", "statistics", "summary", "overview",
        "dashboard", "snapshot", "recap",
    ],
    "volume": [
        "volume", "quantite", "m3", "ventes", "vendu", "consommation",
        "combien", "litres", "quantity", "sold", "sales", "consumption",
        "how much",
    ],
}

ENGLISH_MARKERS = [
    "what", "which", "how", "many", "much", "total", "average", "best",
    "top", "trend", "sales", "revenue", "deliveries", "delivery", "price",
    "oil", "diesel", "gasoil", "warehouse", "depot", "summary", "overview",
]

FRENCH_MARKERS = [
    "quel", "quelle", "combien", "meilleur", "meilleure", "moyen",
    "moyenne", "ventes", "livraisons", "prix", "chiffre", "affaires",
    "resume", "aide", "bonjour",
]


def detect_language(text: str) -> str:
    """Retourne 'en' si la question semble anglaise, sinon 'fr'."""
    t = normalize_text(text)
    if re.search(r"\b(help|what|which|how|give|show|tell)\b", t):
        return "en"
    en_score = sum(1 for marker in ENGLISH_MARKERS if re.search(rf"\b{re.escape(marker)}\b", t))
    fr_score = sum(1 for marker in FRENCH_MARKERS if re.search(rf"\b{re.escape(marker)}\b", t))
    return "en" if en_score > fr_score else "fr"


def _contains_keyword(text: str, keyword: str) -> bool:
    keyword = normalize_text(keyword)
    if len(keyword) <= 3 or " " not in keyword:
        return bool(re.search(rf"\b{re.escape(keyword)}\b", text))
    return keyword in text


def detect_intent(text: str) -> str:
    """Retourne l'intention detectee depuis le texte utilisateur."""
    t = normalize_text(text)
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if _contains_keyword(t, kw):
                return intent
    return "inconnu"
