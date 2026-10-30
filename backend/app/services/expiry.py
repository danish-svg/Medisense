"""Expiry action planner using AO* search over an AND/OR graph.
   OR node  = choose one option.   AND node = every sub-step must be done (costs add up).
   Cost = expected money lost. AO* expands the most promising partial plan first."""

class Node:
    def __init__(s, name, kind, cost=0.0, kids=None, label=""):
        s.name, s.kind, s.cost, s.kids, s.label = name, kind, cost, kids or [], label or name
        s.expanded, s.best = False, []

def h(n):                                   # optimistic estimate (half the true cost) before a node is expanded
    if n.kind == "LEAF": return n.cost * .5
    v = [h(k) for k in n.kids]
    return min(v) if n.kind == "OR" else sum(v)

def f(n):                                   # current best cost estimate; marks the best child(ren)
    if not n.expanded: return h(n)
    if n.kind == "LEAF": return n.cost
    v = [f(k) for k in n.kids]
    if n.kind == "OR":
        i = min(range(len(v)), key=v.__getitem__); n.best = [n.kids[i]]; return v[i]
    n.best = n.kids; return sum(v)

def tip(n):                                 # first unexpanded node on the current best plan
    if not n.expanded: return n
    for k in n.best:
        t = tip(k)
        if t: return t
    return None

def exact(n):
    if n.kind == "LEAF": return n.cost
    v = [exact(k) for k in n.kids]
    return min(v) if n.kind == "OR" else sum(v)

def leaves(n):
    return [n] if n.kind == "LEAF" else [l for k in n.best for l in leaves(k)]

def ao_star(root):
    steps = []
    while True:
        f(root)
        t = tip(root)
        if not t: break
        t.expanded = True
        steps.append({"expanded": t.name, "estimate": round(f(root))})
    f(root)
    return steps

ACTIONS = {"Discount": "Discount and sell through", "Transfer": "Transfer to another branch",
           "Return": "Return to supplier", "Split": "Transfer half, discount half"}

def plan(units, price, days, branch, absorb):
    v = units * price
    accept = .85 if days >= 45 else .5 if days >= 30 else .1             # supplier return acceptance chance
    ship = 120 + .4 * units
    L = lambda n, c, lb: Node(n, "LEAF", c, label=lb)
    root = Node("Root", "OR", kids=[
        Node("Discount", "OR", kids=[L("Discount price cut", v * .475, "25% price cut, about 70% sells through")]),
        Node("Transfer", "AND", kids=[L("T ship", ship, f"Ship to {branch}"), L("T resale", v * (1 - absorb), f"{branch} sells about {round(absorb*100)}% in time")]),
        Node("Return", "AND", kids=[L("R ship", 100, "Courier to supplier"), L("R credit", v * (accept * .15 + (1 - accept)), f"Supplier accepts with {round(accept*100)}% chance, 15% restocking fee")]),
        Node("Split", "AND", kids=[L("S transfer", ship * .6 + v / 2 * (1 - absorb), f"Move half to {branch}"), L("S discount", v / 2 * .475, "25% price cut on the other half")])])
    steps = ao_star(root)
    chosen = root.best[0]
    return {"action": ACTIONS[chosen.name], "option": chosen.name, "expected_loss": round(exact(chosen)),
            "plan": [{"step": l.label, "cost": round(l.cost)} for l in leaves(chosen)],
            "options": sorted([{"name": ACTIONS[k.name], "cost": round(exact(k)), "chosen": k is chosen} for k in root.kids], key=lambda x: x["cost"]),
            "steps": steps, "value": round(v)}
