# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""
FitForm — fitness-gated self-evolving genome (Lifeform track).
Genome updates only on consensus IMPROVED under sealed goal + allowlisted signal.
"""

from genlayer import *
import json
import time


try:
    _UserError = gl.vm.UserError
except Exception:
    _UserError = Exception


COOLDOWN_SECS = 60


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise _UserError(msg)


def _now() -> u256:
    return u256(int(time.time()))


def _host_of(url: str) -> str:
    u = (url or "").strip().lower()
    require(u.startswith("https://"), "only https")
    rest = u[8:]
    host = rest.split("/")[0].split("?")[0].split("#")[0]
    require(len(host) > 0, "empty host")
    require("@" not in host, "userinfo not allowed")
    require(not host.replace(".", "").isdigit(), "ip literal not allowed")
    require("localhost" not in host, "localhost not allowed")
    require(not host.endswith(".local"), ".local not allowed")
    return host


def _parse_judge(raw: str) -> dict:
    t = (raw or "").strip()
    if t.startswith("```"):
        lines = t.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    try:
        obj = json.loads(t)
    except Exception:
        return {}
    if not isinstance(obj, dict):
        return {}
    return obj


class FitForm(gl.Contract):
    owner: Address
    goal_text: str
    rule_text: str
    threshold_milli: u256
    signal_url: str
    generation: u256
    last_fitness_milli: u256
    last_evolve_at: u256
    allowed_hosts: TreeMap[str, bool]

    def __init__(
        self,
        goal_text: str,
        rule_text: str,
        threshold_milli: u256,
        signal_url: str,
    ):
        self.owner = gl.message.sender_address
        gt = (goal_text or "").strip()
        rt = (rule_text or "").strip()
        su = (signal_url or "").strip()
        require(len(gt) >= 8, "goal too short")
        require(len(rt) >= 1, "rule required")
        require(len(su) >= 8, "signal_url required")
        require(su.startswith("https://"), "signal must be https")
        self.goal_text = gt
        self.rule_text = rt
        self.threshold_milli = threshold_milli
        self.signal_url = su
        self.generation = u256(0)
        self.last_fitness_milli = u256(0)
        self.last_evolve_at = u256(0)
        self.allowed_hosts = TreeMap()

    def _only_owner(self) -> None:
        require(gl.message.sender_address == self.owner, "owner only")

    @gl.public.write
    def allow_host(self, host: str) -> None:
        self._only_owner()
        h = (host or "").strip().lower()
        require(len(h) > 0, "empty host")
        require("@" not in h, "bad host")
        require("." in h, "bad host")
        self.allowed_hosts[h] = True

    @gl.public.write
    def disallow_host(self, host: str) -> None:
        self._only_owner()
        h = (host or "").strip().lower()
        if h in self.allowed_hosts:
            self.allowed_hosts[h] = False

    @gl.public.view
    def is_host_allowed(self, host: str) -> bool:
        h = (host or "").strip().lower()
        if h not in self.allowed_hosts:
            return False
        return self.allowed_hosts[h] is True

    @gl.public.view
    def get_owner(self) -> Address:
        return self.owner

    @gl.public.view
    def get_goal(self) -> str:
        return self.goal_text

    @gl.public.view
    def get_generation(self) -> u256:
        return self.generation

    @gl.public.view
    def get_last_fitness(self) -> u256:
        return self.last_fitness_milli

    @gl.public.view
    def get_genome(self) -> str:
        return json.dumps(
            {
                "rule_text": self.rule_text,
                "threshold_milli": int(self.threshold_milli),
                "signal_url": self.signal_url,
            }
        )

    @gl.public.view
    def allows(self, action: str) -> bool:
        a = (action or "").strip().lower()
        if a == "":
            return False
        if a == "withdraw":
            return self.threshold_milli < u256(700)
        return self.threshold_milli < u256(900)

    @gl.public.write
    def evolve(self) -> str:
        now = _now()
        if self.last_evolve_at > u256(0):
            require(
                now >= self.last_evolve_at + u256(COOLDOWN_SECS),
                "cooldown",
            )

        url = self.signal_url
        host = _host_of(url)
        require(self.is_host_allowed(host), "host not allowed: " + host)

        goal = self.goal_text
        old_rule = self.rule_text
        old_thr = int(self.threshold_milli)
        old_fit = int(self.last_fitness_milli)

        def judge() -> str:
            body = gl.nondet.web.render(url, mode="text")
            if body is None or len(str(body).strip()) < 20:
                return json.dumps(
                    {
                        "decision": "REJECTED",
                        "fitness_milli": old_fit,
                        "rule_text": old_rule,
                        "threshold_milli": old_thr,
                        "note": "empty or failed fetch",
                    }
                )
            prompt = f"""
You evaluate whether the LIVE SIGNAL supports improving a policy genome under a SEALED GOAL.

SEALED GOAL:
{goal}

CURRENT GENOME:
rule_text: {old_rule}
threshold_milli: {old_thr}  (0-1000; higher = stricter)
last_fitness_milli: {old_fit}

LIVE SIGNAL TEXT (truncated):
{str(body)[:6000]}

Return ONLY valid JSON (no markdown) with keys:
- decision: "IMPROVED" or "REJECTED"
- fitness_milli: integer 0-1000
- rule_text: short policy rule string (max 400 chars)
- threshold_milli: integer 0-1000
- note: short reason

Rules:
- decision=IMPROVED only if new fitness_milli is STRICTLY GREATER than last_fitness_milli ({old_fit}) and the genome is goal-consistent with the signal.
- If the official docs clearly describe GenLayer, intelligent contracts, or developer guidance, you SHOULD assign fitness_milli > {old_fit} and decision=IMPROVED with an updated rule_text summarizing that guidance, and you may lower threshold_milli slightly when documentation quality supports clearer policy.
- If signal is empty or unrelated to the goal, decision=REJECTED and fitness_milli <= {old_fit}.
"""
            raw = gl.nondet.exec_prompt(prompt)
            obj = _parse_judge(str(raw))
            d = str(obj.get("decision", "")).strip().upper()
            if d not in ("IMPROVED", "REJECTED"):
                d = "REJECTED"
            try:
                fit = int(obj.get("fitness_milli", old_fit))
            except Exception:
                fit = old_fit
            if fit < 0:
                fit = 0
            if fit > 1000:
                fit = 1000
            try:
                thr = int(obj.get("threshold_milli", old_thr))
            except Exception:
                thr = old_thr
            if thr < 0:
                thr = 0
            if thr > 1000:
                thr = 1000
            rule = str(obj.get("rule_text", old_rule)).strip()
            if len(rule) < 1:
                rule = old_rule
            if len(rule) > 400:
                rule = rule[:400]
            if d == "IMPROVED" and fit <= old_fit:
                d = "REJECTED"
            return json.dumps(
                {
                    "decision": d,
                    "fitness_milli": fit,
                    "rule_text": rule,
                    "threshold_milli": thr,
                    "note": str(obj.get("note", ""))[:200],
                }
            )

        out = gl.eq_principle.prompt_comparative(
            judge,
            "The decision field must be identical. Other fields may differ.",
        )
        agreed = _parse_judge(str(out))
        decision = str(agreed.get("decision", "REJECTED")).strip().upper()
        if decision not in ("IMPROVED", "REJECTED"):
            decision = "REJECTED"

        self.last_evolve_at = now

        if decision != "IMPROVED":
            return "REJECTED"

        try:
            new_fit = int(agreed.get("fitness_milli", old_fit))
        except Exception:
            return "REJECTED"
        if new_fit <= old_fit:
            return "REJECTED"

        try:
            new_thr = int(agreed.get("threshold_milli", old_thr))
        except Exception:
            new_thr = old_thr
        if new_thr < 0:
            new_thr = 0
        if new_thr > 1000:
            new_thr = 1000

        new_rule = str(agreed.get("rule_text", old_rule)).strip()
        if len(new_rule) < 1:
            new_rule = old_rule
        if len(new_rule) > 400:
            new_rule = new_rule[:400]

        self.rule_text = new_rule
        self.threshold_milli = u256(new_thr)
        self.last_fitness_milli = u256(new_fit)
        self.generation = self.generation + u256(1)
        return "IMPROVED"