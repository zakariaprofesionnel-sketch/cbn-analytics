from __future__ import annotations

from typing import Dict, Any, List


def _priority_from_confidence(confidence: int) -> str:
    if confidence >= 80:
        return "haute"
    if confidence >= 60:
        return "moyenne"
    return "basse"


def calculate_confidence(signal_value: float, threshold: float) -> int:
    if signal_value >= threshold:
        return min(100, 80 + (signal_value - threshold) * 2)
    return max(50, 80 - (threshold - signal_value) * 2)


def generate_recommendations(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Génère des recommandations en utilisant les signaux et les résultats ML."""
    if context.get("status") != "ok":
        return []

    s = context["signals"]
    ml_results = context.get("ml_results", {})
    recs: List[Dict[str, Any]] = []

    # Exemple : Utiliser les métriques ML
    metrics = ml_results.get("metrics", {})
    mae_test = metrics.get("MAE", 0)
    r2_score = metrics.get("R2", 0)









    """leya ena bech nefhem el modele cv wala le"""


    mean_qty = s.get("mean_qty_last_12_m3", 0)
    mae_pct = (mae_test / mean_qty * 100) if mean_qty > 0 else 0
    if mae_pct > 15:
        recs.append(
            {
                "id": "rec_high_mae",
                "type_action": "pilotage_modele",
                "reason": f"Erreur moyenne élevée (MAE={mae_test:.0f} m³, soit {mae_pct:.1f}% du volume moyen).",
                "impact_estime": "Risque de décisions sous-optimales.",
                "priority": "haute",
                "confidence": 85,
                "proposal": "Réviser les paramètres du modèle ML.",
                "requires_approval": True,
            }
        )












    # Utiliser les prévisions
    predictions = ml_results.get("predictions")
    if predictions is not None and not predictions.empty:
        if "prediction_m3" in predictions.columns:
            latest_prediction = predictions.iloc[-1]
            if latest_prediction["prediction_m3"] > 15000:
                recs.append(
                    {
                        "id": "rec_high_forecast",
                        "type_action": "approvisionnement",
                        "reason": f"Prévision élevée pour le prochain mois ({latest_prediction['prediction_m3']:,.0f} m³).",
                        "impact_estime": "Risque de rupture de stock.",
                        "priority": "haute",
                        "confidence": 90,
                        "proposal": "Augmenter les volumes d'approvisionnement.",
                        "requires_approval": True,
                    }
                )

    # Règle 3 : Tendance baissière sur 3 mois → alerte stock
    qty_trend = s.get("qty_trend_3m_pct", 0)
    if qty_trend < -10:
        recs.append({
            "id": "rec_negative_trend",
            "type_action": "surveillance",
            "reason": f"Baisse des ventes de {abs(qty_trend):.1f}% sur les 3 derniers mois.",
            "impact_estime": "Possible réduction de la demande à venir.",
            "priority": "moyenne",
            "confidence": 75,
            "proposal": "Surveiller l'évolution et ajuster les commandes en conséquence.",
            "requires_approval": False,
        })

    # Règle 4 : Tendance haussière sur 3 mois → anticiper l'approvisionnement
    if qty_trend > 10:
        recs.append({
            "id": "rec_positive_trend",
            "type_action": "approvisionnement",
            "reason": f"Hausse des ventes de {qty_trend:.1f}% sur les 3 derniers mois.",
            "impact_estime": "Risque de rupture de stock si la tendance se confirme.",
            "priority": "moyenne",
            "confidence": 75,
            "proposal": "Anticiper une augmentation des volumes commandés.",
            "requires_approval": True,
        })

    # Règle 5 : Cours Brent élevé → alerte coût d'approvisionnement
    latest_brent = s.get("latest_brent_usd", 0)
    if latest_brent > 80:
        recs.append({
            "id": "rec_high_brent",
            "type_action": "finance",
            "reason": f"Cours du Brent élevé ({latest_brent:.1f} USD/baril).",
            "impact_estime": "Augmentation des coûts d'approvisionnement.",
            "priority": "haute",
            "confidence": 90,
            "proposal": "Envisager une couverture de prix ou avancer les commandes.",
            "requires_approval": True,
        })

    # Règle 6 : Cours Brent bas → opportunité d'achat
    if 0 < latest_brent < 50:
        recs.append({
            "id": "rec_low_brent",
            "type_action": "finance",
            "reason": f"Cours du Brent bas ({latest_brent:.1f} USD/baril).",
            "impact_estime": "Opportunité de réduire les coûts d'approvisionnement.",
            "priority": "moyenne",
            "confidence": 80,
            "proposal": "Profiter des prix bas pour constituer des stocks stratégiques.",
            "requires_approval": True,
        })

    # Règle 7 : Intervalle de confiance trop large → prévision incertaine
    if predictions is not None and not predictions.empty:
        if {"borne_haute_m3", "borne_basse_m3"}.issubset(predictions.columns):
            last = predictions.iloc[-1]
            ci_width = last["borne_haute_m3"] - last["borne_basse_m3"]
            if ci_width > 2 * mae_test and mae_test > 0:
                recs.append({
                    "id": "rec_large_ci",
                    "type_action": "pilotage_modele",
                    "reason": f"Intervalle de confiance très large ({ci_width:,.0f} m³).",
                    "impact_estime": "Prévision peu fiable, décisions à risque élevé.",
                    "priority": "moyenne",
                    "confidence": 70,
                    "proposal": "Prendre les prévisions avec prudence et croiser avec d'autres indicateurs.",
                    "requires_approval": False,
                })

    # Règle 8 : MAPE trop élevé → recalibration du modèle recommandée
    mape = metrics.get("MAPE", 0)
    if mape > 20:
        recs.append({
            "id": "rec_model_drift",
            "type_action": "pilotage_modele",
            "reason": f"Erreur relative du modèle trop élevée (MAPE={mape:.1f}%).",
            "impact_estime": "Les prévisions s'écartent significativement de la réalité.",
            "priority": "haute",
            "confidence": 85,
            "proposal": "Recalibrer le modèle Prophet avec des données plus récentes.",
            "requires_approval": True,
        })

    return recs

