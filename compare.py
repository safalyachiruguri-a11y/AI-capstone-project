"""Fair comparison of forward vs backward chaining (for the Results section).

For every diagnosis, a test case is built automatically: the user's 'yes' answers
are exactly the conditions of the rule that proves it; everything else is 'no'.
The user has already chosen the appliance, so only that appliance's questions
and diagnoses are in play.

  Forward           - asks ALL of the appliance's questions, then fires rules.
  Backward (known)  - the problem is known, so it checks only that one diagnosis.
  Backward (unknown)- the problem is NOT known, so it tries every diagnosis
                      of the appliance.
"""
from engine import load_kb, forward_chain, backward_chain

kb = load_kb("kb.json")
rules = kb["rules"]
questions = kb["questions"]


def make_ask(answers, app_questions, counter, cache):
    """Pretend to be the user: say 'yes' only to the facts in `answers`."""
    def ask(fact):
        if fact not in app_questions:
            return False                     # derived or other-appliance fact
        if fact not in cache:
            cache[fact] = fact in answers
            counter["q"] += 1                # count each new question once
        return cache[fact]
    return ask


cases = []
for app_name, info in kb["appliances"].items():
    for goal in info["diagnoses"]:
        rule = next(r for r in rules if r["then"] == goal)
        cases.append((app_name, info, goal, set(rule["if"])))

print(f"{'Appliance':16} {'Diagnosis':30} {'FwdQ':>5} {'BwdKQ':>6} {'BwdUQ':>6}"
      f" {'Fwd chk':>8} {'BwdK chk':>9} {'BwdU chk':>9} {'OK':>5}")

totals = [0] * 6
for app_name, info, goal, answers in cases:
    app_q, app_d = info["questions"], info["diagnoses"]

    all_facts, fired, f_checks = forward_chain(rules, answers)
    f_q = len(app_q)

    counter, cache = {"q": 0}, {}
    ok_k, st_k = backward_chain(goal, rules, set(), make_ask(answers, app_q, counter, cache))
    k_q, k_checks = counter["q"], st_k["checks"]

    counter, cache, facts = {"q": 0}, {}, set()
    ask = make_ask(answers, app_q, counter, cache)
    found, u_checks = [], 0
    for g in app_d:
        ok, st = backward_chain(g, rules, facts, ask)
        u_checks += st["checks"]
        if ok:
            found.append(g)
    u_q = counter["q"]

    correct = (goal in all_facts) and ok_k and (goal in found)
    row = [f_q, k_q, u_q, f_checks, k_checks, u_checks]
    totals = [t + v for t, v in zip(totals, row)]
    print(f"{app_name:16} {goal:30} {f_q:>5} {k_q:>6} {u_q:>6} {f_checks:>8}"
          f" {k_checks:>9} {u_checks:>9} {str(correct):>5}")

n = len(cases)
print("-" * 106)
print(f"{'AVERAGE':47} {totals[0]/n:>5.1f} {totals[1]/n:>6.1f} {totals[2]/n:>6.1f}"
      f" {totals[3]/n:>8.1f} {totals[4]/n:>9.1f} {totals[5]/n:>9.1f}")
print("\nQ = questions asked, chk = rule/goal checks.")
print("BwdK = backward, problem known. BwdU = backward, problem unknown (all of the appliance's diagnoses tried).")
