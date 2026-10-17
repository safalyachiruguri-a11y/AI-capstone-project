"""Inference engine: forward chaining and backward chaining."""
import json


def load_kb(path):
    """Read the knowledge base (questions + rules) from a JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def forward_chain(rules, known_facts):
    """Data-driven reasoning.
    Start with known facts, keep firing rules until nothing new appears.
    Returns (all_facts, list_of_fired_rule_ids, number_of_rule_checks)."""
    facts = set(known_facts)
    fired = []
    checks = 0
    changed = True
    while changed:                       # repeat until a full pass adds nothing
        changed = False
        for rule in rules:
            checks += 1
            all_true = set(rule["if"]) <= facts      # are all conditions known?
            if all_true and rule["then"] not in facts:
                facts.add(rule["then"])              # derive a new fact
                fired.append(rule["id"])
                changed = True
    return facts, fired, checks


def backward_chain(goal, rules, facts, ask=None, stats=None, stack=None):
    """Goal-driven reasoning.
    To prove `goal`: it is true if it is a known fact, OR some rule concludes it
    and ALL that rule's conditions can be proven (recursively).
    If nothing proves it and `ask` is given, ask the user.
    `facts` is updated in place. Returns (True/False, stats)."""
    if stats is None:
        stats = {"checks": 0, "fired": []}
    if stack is None:
        stack = set()                    # goals being proved now (avoids infinite loops)

    stats["checks"] += 1
    if goal in facts:
        return True, stats
    if goal in stack:
        return False, stats

    stack.add(goal)
    for rule in rules:
        if rule["then"] == goal:
            ok = all(backward_chain(c, rules, facts, ask, stats, stack)[0]
                     for c in rule["if"])
            if ok:
                facts.add(goal)
                stats["fired"].append(rule["id"])
                stack.discard(goal)
                return True, stats
    stack.discard(goal)

    if ask is not None and ask(goal):    # last resort: ask the user
        facts.add(goal)
        return True, stats
    return False, stats
