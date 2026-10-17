"""Laptop Fault Diagnosis - knowledge-based agent (command-line version)."""
from engine import load_kb, forward_chain, backward_chain


def yes_no(text):
    while True:
        a = input(text + " (y/n): ").strip().lower()
        if a in ("y", "n"):
            return a == "y"
        print("Please type y or n.")


def show_rule(rule, desc):
    conds = " AND ".join(rule["if"])
    print(f"  {rule['id']}: IF {conds} THEN {rule['then']}")


def run_forward(kb):
    print("\n--- Forward chaining: answer all questions, then I reason ---")
    facts = {f for f, q in kb["questions"].items() if yes_no(q)}
    all_facts, fired, checks = forward_chain(kb["rules"], facts)

    results = [f for f in all_facts if f in kb["descriptions"]]
    if not results:
        print("\nNo diagnosis found. The knowledge base has no rule for this case.")
        return
    print("\nConclusions:")
    for f in sorted(results):
        print("  *", kb["descriptions"][f])
    print("\nWhy (rules that fired):")
    by_id = {r["id"]: r for r in kb["rules"]}
    for rid in fired:
        show_rule(by_id[rid], kb["descriptions"])
    print(f"\nRules fired: {len(fired)} | Rule checks: {checks}")


def run_backward(kb):
    print("\n--- Backward chaining: pick a problem, I check only what I need ---")
    goals = kb["diagnoses"]
    for i, g in enumerate(goals, 1):
        print(f"  {i}. {kb['descriptions'][g]}")
    choice = int(input("Which problem do you want to check? Number: ")) - 1
    goal = goals[choice]

    facts, asked = set(), {}

    def ask(fact):
        if fact not in kb["questions"]:
            return False                 # derived facts are never asked
        if fact not in asked:
            asked[fact] = yes_no(kb["questions"][fact])
        return asked[fact]

    ok, stats = backward_chain(goal, kb["rules"], facts, ask)
    if ok:
        print("\nYes - likely:", kb["descriptions"][goal])
        print("Rules used:", ", ".join(stats["fired"]))
    else:
        print("\nThat problem is NOT supported by your answers.")
    print(f"Questions asked: {len(asked)} | Goal checks: {stats['checks']}")


def main():
    kb = load_kb("kb.json")
    print("=== Laptop Fault Diagnosis Agent ===")
    mode = input("1 = forward chaining, 2 = backward chaining: ").strip()
    if mode == "1":
        run_forward(kb)
    else:
        run_backward(kb)


if __name__ == "__main__":
    main()
