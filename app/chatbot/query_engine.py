"""Moteur de requetes pandas pour le chatbot bilingue."""

import os

import pandas as pd


_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DATA_DIR = os.path.join(_ROOT, "data", "processed")

MONTH_NAMES = {
    "fr": {
        1: "janvier", 2: "fevrier", 3: "mars", 4: "avril",
        5: "mai", 6: "juin", 7: "juillet", 8: "aout",
        9: "septembre", 10: "octobre", 11: "novembre", 12: "decembre",
    },
    "en": {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December",
    },
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
    df["mois"] = df["date"].dt.month
    return df


def _label_periode(year, month, lang: str) -> str:
    names = MONTH_NAMES.get(lang, MONTH_NAMES["fr"])
    if lang == "en":
        if year and month:
            return f" in {names.get(month, month)} {year}"
        if year:
            return f" in {year}"
        if month:
            return f" in {names.get(month, month)}"
        return ""

    if year and month:
        return f" en {names.get(month, month)} {year}"
    if year:
        return f" en {year}"
    if month:
        return f" en {names.get(month, month)}"
    return ""


def _period_label_plain(year, month, lang: str) -> str:
    names = MONTH_NAMES.get(lang, MONTH_NAMES["fr"])
    if year and month:
        return f"{names.get(month, month)} {year}"
    if year:
        return str(year)
    if month:
        return str(names.get(month, month))
    return ""


def _filter_ventes(df: pd.DataFrame, year=None, month=None, depot=None):
    df_f = df.copy()
    if year:
        df_f = df_f[df_f["annee"] == year]
    if month:
        df_f = df_f[df_f["mois"] == month]
    if depot:
        df_f = df_f[df_f["code_depot"] == depot]
    return df_f


def _empty_sales_message(year=None, month=None, depot=None, lang: str = "fr") -> str:
    period = _period_label_plain(year, month, lang)
    depot_part = f" for depot {depot}" if lang == "en" and depot else ""
    depot_part = f" pour le depot {depot}" if lang == "fr" and depot else depot_part

    if lang == "en":
        if period:
            return f"No sales data available for {period}{depot_part}. The dataset covers 2015 to 2018."
        return f"No sales data available{depot_part}."
    if period:
        return f"Aucune donnee de vente disponible pour {period}{depot_part}. Les donnees couvrent 2015 a 2018."
    return f"Aucune donnee de vente disponible{depot_part}."


def _help(lang: str) -> str:
    if lang == "en":
        return (
            "I am the CBN Analytics assistant. You can ask me questions in English or French:\n\n"
            "- **Volume**: *What is the total volume sold in 2016?*\n"
            "- **Revenue**: *What was the turnover in 2017?*\n"
            "- **Price**: *What was the average gasoil price in 2015?*\n"
            "- **Deliveries**: *How many deliveries were made in March 2017?*\n"
            "- **Depots**: *Which depot sold the most in 2018?*\n"
            "- **Trend**: *What is the sales trend?*\n"
            "- **Brent**: *What was the Brent price in 2016?*\n"
            "- **Summary**: *Give me a summary for 2017.*\n\n"
            "You can specify a **year** from 2015 to 2018, a **month**, and optionally a **depot**."
        )

    return (
        "Je suis l'assistant CBN Analytics. Vous pouvez poser vos questions en francais ou en anglais :\n\n"
        "- **Volume** : *Quel est le volume total vendu en 2016 ?*\n"
        "- **CA** : *Quel est le chiffre d'affaires en 2017 ?*\n"
        "- **Prix** : *Quel est le prix moyen du gasoil en 2015 ?*\n"
        "- **Livraisons** : *Combien de livraisons en mars 2017 ?*\n"
        "- **Depots** : *Quel est le meilleur depot en 2018 ?*\n"
        "- **Tendance** : *Quelle est la tendance des ventes ?*\n"
        "- **Brent** : *Quel est le cours du Brent en 2016 ?*\n"
        "- **Resume** : *Donne-moi un resume des donnees en 2017.*\n\n"
        "Vous pouvez preciser une **annee** de 2015 a 2018, un **mois**, et optionnellement un **depot**."
    )


def _unknown(lang: str) -> str:
    if lang == "en":
        return (
            "I did not understand the question. Try for example:\n\n"
            "- *What is the total volume in 2016?*\n"
            "- *Which depot sold the most?*\n"
            "- *What is the sales trend?*\n\n"
            "Type **help** to see what I can answer."
        )

    return (
        "Je n'ai pas compris votre question. Essayez par exemple :\n\n"
        "- *Quel est le volume total en 2016 ?*\n"
        "- *Quel est le meilleur depot ?*\n"
        "- *Quelle est la tendance des ventes ?*\n\n"
        "Tapez **aide** pour voir ce que je sais faire."
    )


def repondre(intent: str, year=None, month=None, depot=None, lang: str = "fr") -> str:
    lang = "en" if lang == "en" else "fr"

    if intent == "aide":
        return _help(lang)

    try:
        df = _load_ventes()
    except Exception as e:
        if lang == "en":
            return f"Error while loading sales data: {e}"
        return f"Erreur lors du chargement des donnees : {e}"

    df_f = _filter_ventes(df, year=year, month=month, depot=depot)
    if df_f.empty and intent not in ("brent", "tendance"):
        return _empty_sales_message(year=year, month=month, depot=depot, lang=lang)

    p = _label_periode(year, month, lang)
    depot_label = ""
    if depot:
        depot_label = f" for depot {depot}" if lang == "en" else f" pour le depot {depot}"

    if intent in ("volume_total", "volume"):
        vol = df_f["quantite_m3"].sum()
        if lang == "en":
            return f"The total gasoil volume sold{p}{depot_label} is **{_fmt(vol)} m3**."
        return f"Le volume total de gasoil vendu{p}{depot_label} est de **{_fmt(vol)} m3**."

    if intent == "montant_total":
        mnt = df_f["montant_ht"].sum()
        if lang == "en":
            return f"The net turnover{p}{depot_label} is **{_fmt(mnt)} TND**."
        return f"Le chiffre d'affaires HT{p}{depot_label} s'eleve a **{_fmt(mnt)} TND**."

    if intent == "prix_moyen":
        prix = df_f["prix_unitaire"].mean()
        if lang == "en":
            return f"The average gasoil unit price{p}{depot_label} is **{_fmt(prix, 2)} TND/m3**."
        return f"Le prix unitaire moyen du gasoil{p}{depot_label} est de **{_fmt(prix, 2)} TND/m3**."

    if intent == "nb_livraisons":
        n = len(df_f)
        if lang == "en":
            return f"The number of gasoil deliveries{p}{depot_label} is **{_fmt(n)}**."
        return f"Le nombre de livraisons de gasoil{p}{depot_label} est de **{_fmt(n)}**."

    if intent == "top_depot":
        top = (
            df_f.groupby("code_depot")["quantite_m3"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )
        if top.empty:
            return "No depot found for this period." if lang == "en" else "Aucun depot trouve pour cette periode."
        lines = [
            f"{i + 1}. Depot **{dep}** - {_fmt(vol)} m3"
            for i, (dep, vol) in enumerate(top.items())
        ]
        title = f"Top 5 depots by volume{p}:" if lang == "en" else f"Top 5 des depots par volume{p} :"
        return title + "\n\n" + "\n\n".join(lines)

    if intent == "tendance":
        trend_df = _filter_ventes(df, month=month, depot=depot)
        par_an = trend_df.groupby("annee")["quantite_m3"].sum().sort_index()
        if len(par_an) < 2:
            return "Not enough data to calculate a trend." if lang == "en" else "Pas assez de donnees pour calculer une tendance."
        lines = [f"- **{a}**: {_fmt(v)} m3" for a, v in par_an.items()]
        premier, dernier = par_an.iloc[0], par_an.iloc[-1]
        delta_pct = (dernier - premier) / premier * 100
        if lang == "en":
            direction = "increase" if delta_pct > 0 else "decrease"
            lines.append(
                f"\nOverall change: **{abs(delta_pct):.1f}% {direction}** "
                f"between {par_an.index[0]} and {par_an.index[-1]}."
            )
            return "Annual gasoil sales trend:\n\n" + "\n".join(lines)

        direction = "hausse" if delta_pct > 0 else "baisse"
        lines.append(
            f"\nEvolution globale : **{direction} de {abs(delta_pct):.1f} %** "
            f"entre {par_an.index[0]} et {par_an.index[-1]}."
        )
        return "Evolution annuelle des ventes de gasoil :\n\n" + "\n".join(lines)

    if intent == "brent":
        try:
            db = _load_brent()
            if year:
                db = db[db["annee"] == year]
            if month:
                db = db[db["mois"] == month]
            if db.empty:
                period = _period_label_plain(year, month, lang)
                if lang == "en":
                    return f"No Brent data available for {period}."
                return f"Aucune donnee Brent disponible pour {period}."
            moy = db["cours_brent_usd"].mean()
            mini = db["cours_brent_usd"].min()
            maxi = db["cours_brent_usd"].max()
            label = p if (year or month) else (" over 2015-2018" if lang == "en" else " sur la periode 2015-2018")
            if lang == "en":
                return (
                    f"Brent price{label}:\n\n"
                    f"- Average: **{moy:.2f} USD/barrel**\n"
                    f"- Minimum: {mini:.2f} USD/barrel\n"
                    f"- Maximum: {maxi:.2f} USD/barrel"
                )
            return (
                f"Cours du Brent{label} :\n\n"
                f"- Moyenne : **{moy:.2f} USD/baril**\n"
                f"- Minimum : {mini:.2f} USD/baril\n"
                f"- Maximum : {maxi:.2f} USD/baril"
            )
        except Exception:
            return "Brent data is unavailable." if lang == "en" else "Les donnees Brent sont indisponibles."

    if intent == "stats":
        vol = df_f["quantite_m3"].sum()
        mnt = df_f["montant_ht"].sum()
        prix = df_f["prix_unitaire"].mean()
        n = len(df_f)
        nb_dep = df_f["code_depot"].nunique()
        if lang == "en":
            return (
                f"Sales data summary{p}{depot_label}:\n\n"
                f"- Total volume: **{_fmt(vol)} m3**\n"
                f"- Net turnover: **{_fmt(mnt)} TND**\n"
                f"- Average price: **{_fmt(prix, 2)} TND/m3**\n"
                f"- Deliveries: **{_fmt(n)}**\n"
                f"- Active depots: **{nb_dep}**"
            )
        return (
            f"Resume des donnees de vente{p}{depot_label} :\n\n"
            f"- Volume total : **{_fmt(vol)} m3**\n"
            f"- Chiffre d'affaires HT : **{_fmt(mnt)} TND**\n"
            f"- Prix moyen : **{_fmt(prix, 2)} TND/m3**\n"
            f"- Nombre de livraisons : **{_fmt(n)}**\n"
            f"- Depots actifs : **{nb_dep}**"
        )

    return _unknown(lang)
