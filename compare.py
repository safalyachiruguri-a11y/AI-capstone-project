"""Fair comparison of forward vs backward chaining (for the Results section).

For every diagnosis in the knowledge base, we build a test case automatically:
the user's 'yes' answers are exactly the conditions of the rule that proves it.
All other questions are answered 'no'.

Three measurements per case:
  Forward           - asks ALL questions, then fires rules.
  Backward (known)  - the goal is known, so it checks only that one problem.
  Backward (unknown)- the goal is NOT known, so it tries every diagnosis.
"""
import time
from engine import load_kb, forward_chain, backward_chain

kb = load_kb("kb.json")
rules = kb["rules"]
questions = kb["questions"]
diagnoses = kb["diagnoses"]


def make_ask(answers, counter, cache):
    """Pretend to be the user: say 'yes' only to the facts in `answers`."""
    def ask(fact):
        if fact not in questions:
            return False                     # derived facts are never asked
        if fact not in cache:
            cache[fact] = fact in answers
            counter["q"] += 1                # count each new question once
        return cache[fact]
    return ask


# One test case per diagnosis: its answers are the conditions of its rule
cases = []
for goal in diagnoses:
    for rule in rules:
        if rule["then"] == goal:
            cases.append((goal, set(rule["if"])))
            break

print(f"{'Diagnosis':32} {'Fwd Q':>6} {'BwdK Q':>7} {'BwdU Q':>7}"
      f" {'Fwd chk':>8} {'BwdK chk':>9} {'BwdU chk':>9} {'OK':>4}")

totals = [0, 0, 0, 0, 0, 0]
for goal, answers in cases:
    # Forward chaining: all questions are asked first
    all_facts, fired, f_checks = forward_chain(rules, answers)
    f_q = len(questions)

    # Backward chaining, goal known
    counter, cache = {"q": 0}, {}
    ok_k, st_k = backward_chain(goal, rules, set(), make_ask(answers, counter, cache))
    k_q, k_checks = counter["q"], st_k["checks"]

    # Backward chaining, goal unknown: try every diagnosis, share the answers
    counter, cache, facts = {"q": 0}, {}, set()
    ask = make_ask(answers, counter, cache)
    found, u_checks = [], 0
    for g in diagnoses:
        ok, st = backward_chain(g, rules, facts, ask)
        u_checks += st["checks"]
        if ok:
            found.append(g)
    u_q = counter["q"]

    correct = (goal in all_facts) and ok_k and (goal in found)
    row = [f_q, k_q, u_q, f_checks, k_checks, u_checks]
    totals = [t + v for t, v in zip(totals, row)]
    print(f"{goal:32} {f_q:>6} {k_q:>7} {u_q:>7} {f_checks:>8} {k_checks:>9}"
          f" {u_checks:>9} {str(correct):>4}")

n = len(cases)
print("-" * 92)
print(f"{'AVERAGE':32} {totals[0]/n:>6.1f} {totals[1]/n:>7.1f} {totals[2]/n:>7.1f}"
      f" {totals[3]/n:>8.1f} {totals[4]/n:>9.1f} {totals[5]/n:>9.1f}")
print("\nQ = questions asked, chk = rule/goal checks.")
print("BwdK = backward, goal known. BwdU = backward, goal unknown (all diagnoses tried).")
