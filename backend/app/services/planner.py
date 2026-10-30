"""Constraint-based reorder planner (CSP solved by backtracking with bound pruning).
   Variables: order quantity per medicine, each with domain {full order, minimum order, none}.
   Constraints: total cost <= budget, shelf space <= limit, supplier minimum order value."""
W_CRIT = {"vital": 3, "essential": 2, "desirable": 1}
W_STATUS = {"Critical": 3, "Low": 2}

def plan(items, budget, free_space, suppliers, node_limit=200000):
    for it in items:
        it["weight"] = W_CRIT[it["criticality"]] * W_STATUS.get(it["status"], 1)
    items = sorted(items, key=lambda x: -x["weight"])        # most important variable first
    n = len(items)
    doms = []
    for it in items:
        d = [(it["q_target"], it["weight"] * 1.4)]
        if it["q_min"] < it["q_target"]:
            d.append((it["q_min"], it["weight"] * 1.0))
        d.append((0, 0.0))
        doms.append(d)
    suffix = [0.0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix[i] = suffix[i + 1] + doms[i][0][1]
    best = {"v": -1, "ch": [0] * n}
    nodes, tot = [0], {}

    def rec(i, cost, vol, val, ch):
        if nodes[0] >= node_limit: return
        nodes[0] += 1
        if val + suffix[i] <= best["v"]: return              # cannot beat best plan found so far
        if i == n:
            if any(0 < t < suppliers[s]["min_order_value"] for s, t in tot.items()): return
            best["v"], best["ch"] = val, list(ch)
            return
        it = items[i]
        for q, v in doms[i]:
            c, w = q * it["price"], q * it["storage_units"]
            if cost + c > budget or vol + w > free_space: continue
            tot[it["supplier_id"]] = tot.get(it["supplier_id"], 0) + c
            ch.append(q); rec(i + 1, cost + c, vol + w, val + v, ch); ch.pop()
            tot[it["supplier_id"]] -= c
    rec(0, 0.0, 0.0, 0.0, [])

    lines, spent, space, per = [], 0.0, 0.0, {}
    for it, q in zip(items, best["ch"]):
        c = q * it["price"]
        spent += c; space += q * it["storage_units"]
        per[it["supplier_id"]] = per.get(it["supplier_id"], 0) + c
        reason = ("Full order: covers lead time plus 14 days of demand." if q == it["q_target"] and q else
                  "Reduced order: the minimum to restore the reorder point within the limits." if q else
                  "Not funded now: lower priority than funded items under the budget, shelf space and supplier minimum limits.")
        lines.append({"medicine_id": it["id"], "name": it["name"], "supplier": suppliers[it["supplier_id"]]["name"],
                      "criticality": it["criticality"], "status": it["status"], "quantity": q, "full_quantity": it["q_target"],
                      "cost": round(c), "reason": reason})
    sup = [{"name": suppliers[s]["name"], "total": round(t), "minimum": suppliers[s]["min_order_value"],
            "met": t == 0 or t >= suppliers[s]["min_order_value"]} for s, t in per.items() if t > 0]
    return {"lines": lines, "spent": round(spent), "budget": budget, "space_used": round(space, 1), "space_free": round(free_space, 1),
            "suppliers": sup, "nodes": nodes[0], "optimal": nodes[0] < node_limit}
