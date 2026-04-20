"""Détection d'intention par correspondance de mots-clés (rule-based)."""

# Ordre = priorité décroissante : les intents spécifiques avant les génériques
INTENT_KEYWORDS = {
    "aide": [
        "aide", "help", "que peux-tu", "que sais-tu", "quelles questions",
        "bonjour", "salut", "hello", "quoi faire", "quelles commandes",
    ],
    "top_depot": [
        "meilleur dépôt", "meilleur depot", "top dépôt", "top depot",
        "quel dépôt", "quel depot", "classement dépôt", "classement depot",
        "dépôt le plus", "depot le plus", "premier dépôt", "premier depot",
        "dépôts", "depots",
    ],
    "tendance": [
        "tendance", "évolution", "evolution", "croissance", "augmentation",
        "diminution", "hausse", "baisse", "progression", "comparaison annuelle",
    ],
    "brent": [
        "brent", "cours du brent", "cours brent", "pétrole", "petrole",
        "prix du pétrole", "prix du petrole", "barils",
    ],
    "prix_moyen": [
        "prix moyen", "prix unitaire", "tarif moyen", "coût moyen", "cout moyen",
        "prix de vente", "prix du gasoil",
    ],
    "montant_total": [
        "chiffre d'affaires", "chiffre d affaires", "ca total", "montant total",
        "revenu total", "recette", "montant ht", "facturation", "revenus",
    ],
    "nb_livraisons": [
        "nombre de livraisons", "combien de livraisons", "nb livraisons",
        "livraisons", "nombre livraisons",
    ],
    "volume_total": [
        "volume total", "quantité totale", "quantite totale", "total m3",
        "total des ventes", "volume global", "total gasoil",
    ],
    "stats": [
        "statistiques", "stats", "résumé", "resume", "aperçu", "apercu",
        "vue d'ensemble", "bilan", "synthèse", "synthese",
    ],
    "volume": [
        "volume", "quantité", "quantite", "m3", "ventes", "vendu",
        "consommation", "combien", "litrés",
    ],
}


def detect_intent(text: str) -> str:
    """Retourne l'intention détectée depuis le texte utilisateur."""
    t = text.lower().strip()
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if kw in t:
                return intent
    return "inconnu"
