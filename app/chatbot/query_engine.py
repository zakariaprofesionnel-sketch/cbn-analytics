"""Moteur de requêtes pandas — répond aux questions sur les données CSV."""
import os
import pandas as pd

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DATA_DIR = os.path.join(_ROOT, "data", "processed")

NOMS_MOIS = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril",
    5: "mai", 6: "juin", 7: "juillet", 8: "août",
    9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre",
}


def _fmt(n: float, decimales: int = 0) -> str:
    if decimales == 0:
        return f"{n:,.0f}".replace(",", " ")
    return f"{n:,.{decimales}f}".replace(",", " ")


def _load_ventes() -> pd.DataFrame:
    path = os.path.join(_DATA_DIR, "ventes_gasoil.csv")
    df = pd.read_csv(path, parse_dates=["date_livraison"])
    df["annee"] = df["date_livraison"].dt.year
    df["mois"] = df["date_livraison"].dt.month
    return df


def _load_brent() -> pd.DataFrame:
    path = os.path.join(_DATA_DIR, "cours_brent.csv")
    df = pd.read_csv(path, parse_dates=["date"])
    df["annee"] = df["date"].dt.year
    return df


def _label_periode(year, month) -> str:
    if year and month:
        return f" en {NOMS_MOIS.get(month, month)} {year}"
    if year:
        return f" en {year}"
    if month:
        return f" en {NOMS_MOIS.get(month, month)}"
    return ""


def repondre(intent: str, year=None, month=None, depot=None) -> str:
    try:
        df = _load_ventes()
    except Exception as e:
        return f"Erreur lors du chargement des données : {e}"

    df_f = df.copy()
    if year:
        df_f = df_f[df_f["annee"] == year]
        if df_f.empty:
            return f"Aucune donnée disponible pour l'année {year}. Les données couvrent 2015 à 2018."
    if month:
        df_f = df_f[df_f["mois"] == month]
        if df_f.empty:
            label = f"{NOMS_MOIS.get(month, month)} {year or ''}".strip()
            return f"Aucune donnée disponible pour {label}."

    p = _label_periode(year, month)

    # ── Volume ──────────────────────────────────────────────────────────────
    if intent in ("volume_total", "volume"):
        vol = df_f["quantite_m3"].sum()
        return f"Le volume total de gasoil vendu{p} est de **{_fmt(vol)} m³**."

    # ── Chiffre d'affaires ───────────────────────────────────────────────────
    if intent == "montant_total":
        mnt = df_f["montant_ht"].sum()
        return f"Le chiffre d'affaires HT{p} s'élève à **{_fmt(mnt)} TND**."

    # ── Prix moyen ───────────────────────────────────────────────────────────
    if intent == "prix_moyen":
        prix = df_f["prix_unitaire"].mean()
        return f"Le prix unitaire moyen du gasoil{p} est de **{_fmt(prix, 2)} TND/m³**."

    # ── Nombre de livraisons ─────────────────────────────────────────────────
    if intent == "nb_livraisons":
        n = len(df_f)
        return f"Le nombre de livraisons de gasoil{p} est de **{_fmt(n)}**."

    # ── Top dépôts ───────────────────────────────────────────────────────────
    if intent == "top_depot":
        top = (
            df_f.groupby("code_depot")["quantite_m3"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )
        if top.empty:
            return "Aucun dépôt trouvé pour cette période."
        medals = ["🥇", "🥈", "🥉", "4.", "5."]
        lines = [
            f"{medals[i]} Dépôt **{dep}** — {_fmt(vol)} m³"
            for i, (dep, vol) in enumerate(top.items())
        ]
        return f"Top 5 des dépôts par volume{p} :\n\n" + "\n\n".join(lines)

    # ── Tendance annuelle ────────────────────────────────────────────────────
    if intent == "tendance":
        par_an = df.groupby("annee")["quantite_m3"].sum().sort_index()
        if len(par_an) < 2:
            return "Pas assez de données pour calculer une tendance."
        lines = [f"• **{a}** : {_fmt(v)} m³" for a, v in par_an.items()]
        premier, dernier = par_an.iloc[0], par_an.iloc[-1]
        delta_pct = (dernier - premier) / premier * 100
        sens = "hausse" if delta_pct > 0 else "baisse"
        lines.append(
            f"\nÉvolution globale : **{sens} de {abs(delta_pct):.1f} %** "
            f"entre {par_an.index[0]} et {par_an.index[-1]}."
        )
        return "Évolution annuelle des ventes de gasoil :\n\n" + "\n".join(lines)

    # ── Cours du Brent ───────────────────────────────────────────────────────
    if intent == "brent":
        try:
            db = _load_brent()
            if year:
                db = db[db["annee"] == year]
            if db.empty:
                return f"Aucune donnée Brent disponible pour {year}."
            moy = db["cours_brent_usd"].mean()
            mini = db["cours_brent_usd"].min()
            maxi = db["cours_brent_usd"].max()
            label = f" en {year}" if year else " sur la période 2015–2018"
            return (
                f"Cours du Brent{label} :\n\n"
                f"• Moyenne : **{moy:.2f} USD/baril**\n"
                f"• Minimum : {mini:.2f} USD/baril\n"
                f"• Maximum : {maxi:.2f} USD/baril"
            )
        except Exception:
            return "Les données Brent sont indisponibles."

    # ── Résumé statistique ───────────────────────────────────────────────────
    if intent == "stats":
        vol = df_f["quantite_m3"].sum()
        mnt = df_f["montant_ht"].sum()
        prix = df_f["prix_unitaire"].mean()
        n = len(df_f)
        nb_dep = df_f["code_depot"].nunique()
        return (
            f"Résumé des données de vente{p} :\n\n"
            f"• Volume total : **{_fmt(vol)} m³**\n"
            f"• Chiffre d'affaires HT : **{_fmt(mnt)} TND**\n"
            f"• Prix moyen : **{_fmt(prix, 2)} TND/m³**\n"
            f"• Nombre de livraisons : **{_fmt(n)}**\n"
            f"• Dépôts actifs : **{nb_dep}**"
        )

    # ── Aide ─────────────────────────────────────────────────────────────────
    if intent == "aide":
        return (
            "Je suis l'assistant CBN Analytics. Voici ce que je peux répondre :\n\n"
            "• **Volume** — *Quel est le volume total vendu en 2016 ?*\n"
            "• **CA** — *Quel est le chiffre d'affaires en 2017 ?*\n"
            "• **Prix** — *Quel est le prix moyen du gasoil en 2015 ?*\n"
            "• **Livraisons** — *Combien de livraisons en mars 2017 ?*\n"
            "• **Dépôts** — *Quel est le meilleur dépôt en 2018 ?*\n"
            "• **Tendance** — *Quelle est la tendance des ventes ?*\n"
            "• **Brent** — *Quel est le cours du Brent en 2016 ?*\n"
            "• **Résumé** — *Donne-moi un résumé des données en 2017*\n\n"
            "Vous pouvez préciser une **année** (2015–2018) et/ou un **mois** dans votre question."
        )

    # ── Intention inconnue ───────────────────────────────────────────────────
    return (
        "Je n'ai pas compris votre question. Essayez par exemple :\n\n"
        "• *Quel est le volume total en 2016 ?*\n"
        "• *Quel est le meilleur dépôt ?*\n"
        "• *Quelle est la tendance des ventes ?*\n\n"
        "Tapez **aide** pour voir tout ce que je sais faire."
    )
