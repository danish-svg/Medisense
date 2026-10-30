"""Substitute finder: walks the semantic network (Medicine -belongs to-> Category <-belongs to- Medicine)."""
def find(target, rows):
    t, out = target.a, []
    for r in rows:
        a = r.a
        if a["id"] == t["id"] or a["category"] != t["category"]: continue
        if a["stock"] <= 0 or a["expiry_days"] <= 0 or a["status"] in ("Critical", "Expired"): continue
        score = (min(a["days_cover"], 30) / 30 * 60
                 + (1 - min(abs(a["unit_price"] - t["unit_price"]) / max(t["unit_price"], 1), 1)) * 25
                 + min(a["expiry_days"], 180) / 180 * 15)
        out.append({"medicine_id": a["id"], "name": a["name"], "stock": a["stock"], "expiry_days": a["expiry_days"],
                    "unit_price": a["unit_price"], "score": round(score),
                    "path": f'{t["name"]} belongs to {t["category"]}, which also contains {a["name"]}'})
    return {"for": t["name"], "category": t["category"], "needs_pharmacist_confirmation": True,
            "note": "Suggestions only. A pharmacist must confirm suitability before any substitute is dispensed.",
            "options": sorted(out, key=lambda x: -x["score"])[:5]}
