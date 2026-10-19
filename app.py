"""Browser interface for the Household Appliance Fault Diagnosis Agent.

Run:   py app.py
Then the page opens at http://localhost:8000 (the terminal prints the address).

It uses only the Python standard library plus your own engine.py and kb.json,
so the reasoning shown on screen is exactly what the command-line agent does.
"""
import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from engine import load_kb, forward_chain, backward_chain

HERE = os.path.dirname(os.path.abspath(__file__))
KB = load_kb(os.path.join(HERE, "kb.json"))
RULES = KB["rules"]
RULE_BY_ID = {r["id"]: r for r in RULES}


class NeedAnswer(Exception):
    """Raised when backward chaining needs the user to answer a question."""

    def __init__(self, fact):
        self.fact = fact


def kb_summary():
    """Everything the page needs to build its menus."""
    appliances = {}
    for name, info in KB["appliances"].items():
        appliances[name] = {
            "questions": [{"id": q, "text": KB["questions"][q]} for q in info["questions"]],
            "diagnoses": info["diagnoses"],
        }
    all_diagnoses = [d for a in KB["appliances"].values() for d in a["diagnoses"]]
    return {
        "appliances": appliances,
        "descriptions": KB["descriptions"],
        "questions": KB["questions"],
        "allDiagnoses": all_diagnoses,
        "ruleCount": len(RULES),
    }


def forward_run(appliance, yes):
    info = KB["appliances"][appliance]
    yes = [f for f in yes if f in info["questions"]]
    all_facts, fired, checks = forward_chain(RULES, set(yes))
    fired_rules = [RULE_BY_ID[i] for i in fired]
    conclusions = [r["then"] for r in fired_rules if r["then"] in KB["descriptions"]]
    return {
        "fired": fired_rules,
        "checks": checks,
        "conclusions": conclusions,
        "asked": len(info["questions"]),
        "given": sorted(yes),
    }


def backward_step(appliance, goal, answers):
    """Stateless step: re-run backward chaining with the answers so far.
    Either it needs one more answer (status 'ask') or it is finished ('done')."""
    info = KB["appliances"][appliance]
    allowed = set(info["questions"])

    def ask(fact):
        if fact not in allowed:
            return False                      # derived or other-appliance fact
        if fact in answers:
            return bool(answers[fact])
        raise NeedAnswer(fact)                # we need the user to answer this

    try:
        ok, stats = backward_chain(goal, RULES, set(), ask)
    except NeedAnswer as need:
        return {"status": "ask", "fact": need.fact,
                "question": KB["questions"][need.fact], "asked": len(answers)}
    return {
        "status": "done",
        "proven": ok,
        "fired": [RULE_BY_ID[i] for i in stats["fired"]],
        "checks": stats["checks"],
        "asked": len(answers),
        "given": sorted(f for f, v in answers.items() if v),
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(os.path.join(HERE, "index.html"), "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        elif self.path == "/api/kb":
            self._send(200, json.dumps(kb_summary()))
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            appliance = body.get("appliance")
            if appliance not in KB["appliances"]:
                raise ValueError("unknown appliance")
            if self.path == "/api/forward":
                result = forward_run(appliance, body.get("yes", []))
            elif self.path == "/api/backward":
                goal = body.get("goal")
                if goal not in KB["appliances"][appliance]["diagnoses"]:
                    raise ValueError("unknown problem for this appliance")
                result = backward_step(appliance, goal, body.get("answers", {}))
            else:
                self._send(404, json.dumps({"error": "not found"}))
                return
            self._send(200, json.dumps(result))
        except (ValueError, KeyError, json.JSONDecodeError) as err:
            self._send(400, json.dumps({"error": str(err)}))

    def log_message(self, *args):
        pass                                   # keep the terminal quiet


def main():
    for port in range(8000, 8011):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    else:
        raise SystemExit("No free port between 8000 and 8010.")
    url = f"http://localhost:{port}"
    print(f"Agent interface running at {url}")
    print("Press Ctrl+C in this window to stop it.")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
