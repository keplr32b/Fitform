# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""
FitForm — mutation + selection on a bounded genome (Lifeform track).
propose → challenge → finalize; recheck STABLE|DRIFT; EXTINCT after repeated REJECTED.
"""

from genlayer import *
import json
import time

try:
    _UserError = gl.vm.UserError
except Exception:
    _UserError = Exception

COOLDOWN_SECS = 60
CHALLENGE_SECS = 300
MAX_FAILURES = 5
DRIFT_MARGIN = 50
OPEN_THRESHOLD = 700


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


def _parse_json(raw: str) -> dict:
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


def _norm_mode(m: str) -> str:
    x = (m or "").strip().upper()
    if x in ("CLOSED", "OWNER_ONLY", "OPEN"):
        return x
    return "CLOSED"


def _clamp_milli(v: int) -> int:
    if v < 0:
        return 0
    if v > 1000:
        return 1000
    return v


def _genome_fp(mode: str, thr: int, note: str) -> str:
    return mode + "|" + str(thr) + "|" + (note or "")[:80]


class FitForm(gl.Contract):
    owner: Address
    goal_text: str
    signal_url: str

    rule_mode: str
    threshold_milli: u256
    rule_note: str

    generation: u256
    committed_fitness_milli: u256
    parent_genome_hash: str
    last_propose_at: u256

    pending_active: bool
    pending_rule_mode: str
    pending_threshold_milli: u256
    pending_rule_note: str
    pending_fitness_milli: u256
    challenge_open_until: u256

    failed_propose_count: u256
    extinct: bool

    allowed_hosts: TreeMap[str, bool]
    history: DynArray[str]

    def __init__(
        self,
        goal_text: str,
        signal_url: str,
        rule_mode: str,
        threshold_milli: u256,
        rule_note: str,
    ):
        self.owner = gl.message.sender_address
        gt = (goal_text or "").strip()
        su = (signal_url or "").strip()
        require(len(gt) >= 8, "goal too short")
        require(su.startswith("https://"), "signal must be https")
        self.goal_text = gt
        self.signal_url = su
        self.rule_mode = _norm_mode(rule_mode)
        self.threshold_milli = threshold_milli
        self.rule_note = (rule_note or "").strip()[:400]
        self.generation = u256(0)
        self.committed_fitness_milli = u256(0)
        self.parent_genome_hash = ""
        self.last_propose_at = u256(0)
        self.pending_active = False
        self.pending_rule_mode = "CLOSED"
        self.pending_threshold_milli = u256(0)
        self.pending_rule_note = ""
        self.pending_fitness_milli = u256(0)
        self.challenge_open_until = u256(0)
        self.failed_propose_count = u256(0)
        self.extinct = False
        self.allowed_hosts = TreeMap()
        self.history = DynArray()

    def _only_owner(self) -> None:
        require(gl.message.sender_address == self.owner, "owner only")

    def _not_extinct(self) -> None:
        require(self.extinct is False, "extinct")

    def _history_tail(self) -> str:
        n = len(self.history)
        if n == 0:
            return "(no history)"
        parts = []
        start = 0
        if n > 3:
            start = n - 3
        for i in range(start, n):
            parts.append(str(self.history[i]))
        return "\n".join(parts)

    @gl.public.write
    def allow_host(self, host: str) -> None:
        self._only_owner()
        h = (host or "").strip().lower()
        require(len(h) > 0 and "." in h and "@" not in h, "bad host")
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
    def get_committed_fitness(self) -> u256:
        return self.committed_fitness_milli

    @gl.public.view
    def is_extinct(self) -> bool:
        return self.extinct

    @gl.public.view
    def is_pending(self) -> bool:
        return self.pending_active

    @gl.public.view
    def get_genome(self) -> str:
        return json.dumps(
            {
                "rule_mode": self.rule_mode,
                "threshold_milli": int(self.threshold_milli),
                "rule_note": self.rule_note,
                "generation": int(self.generation),
                "committed_fitness_milli": int(self.committed_fitness_milli),
                "parent_genome_hash": self.parent_genome_hash,
                "extinct": self.extinct,
            }
        )

    @gl.public.view
    def get_pending(self) -> str:
        if not self.pending_active:
            return json.dumps({"active": False})
        return json.dumps(
            {
                "active": True,
                "rule_mode": self.pending_rule_mode,
                "threshold_milli": int(self.pending_threshold_milli),
                "rule_note": self.pending_rule_note,
                "fitness_milli": int(self.pending_fitness_milli),
                "challenge_open_until": int(self.challenge_open_until),
            }
        )

    @gl.public.view
    def allows(self, action: str) -> bool:
        if self.extinct:
            return False
        a = (action or "").strip().lower()
        if a != "withdraw":
            return False
        mode = _norm_mode(self.rule_mode)
        if mode == "CLOSED":
            return False
        if mode == "OWNER_ONLY":
            return False
        if mode == "OPEN":
            return self.threshold_milli < u256(OPEN_THRESHOLD)
        return False

    @gl.public.write
    def propose_evolve(self) -> str:
        self._not_extinct()
        require(self.pending_active is False, "pending active")
        now = _now()
        if self.last_propose_at > u256(0):
            require(now >= self.last_propose_at + u256(COOLDOWN_SECS), "cooldown")

        url = self.signal_url
        host = _host_of(url)
        require(self.is_host_allowed(host), "host not allowed: " + host)

        goal = self.goal_text
        live_mode = self.rule_mode
        live_thr = int(self.threshold_milli)
        live_note = self.rule_note
        live_fit = int(self.committed_fitness_milli)
        hist = self._history_tail()

        def judge() -> str:
            body = gl.nondet.web.render(url, mode="text")
            if body is None or len(str(body).strip()) < 20:
                return json.dumps(
                    {
                        "decision": "REJECTED",
                        "rule_mode": live_mode,
                        "threshold_milli": live_thr,
                        "rule_note": live_note,
                        "fitness_milli": live_fit,
                        "note": "empty signal",
                    }
                )
            prompt = f"""
You propose a bounded policy genome under a SEALED GOAL using a LIVE SIGNAL.
Selection pressure: only propose PENDING if fitness strictly improves.

SEALED GOAL:
{goal}

LIVE GENOME:
rule_mode: {live_mode}  (CLOSED|OWNER_ONLY|OPEN)
threshold_milli: {live_thr}
rule_note: {live_note}
committed_fitness_milli: {live_fit}

RECENT HISTORY:
{hist}

LIVE SIGNAL (truncated):
{str(body)[:5500]}

Return ONLY JSON:
- decision: "PENDING" or "REJECTED"
- rule_mode: CLOSED|OWNER_ONLY|OPEN
- threshold_milli: 0-1000
- rule_note: short string
- fitness_milli: 0-1000
- note: short reason

Rules:
- PENDING only if fitness_milli > {live_fit} and genome is goal-consistent with the signal.
- If official GenLayer docs clearly support clearer protocol policy, prefer PENDING with higher fitness and rule_mode OPEN with threshold_milli between 400 and 650 when appropriate.
- If signal is weak or unrelated, REJECTED and fitness_milli <= {live_fit}.
"""
            raw = gl.nondet.exec_prompt(prompt)
            obj = _parse_json(str(raw))
            d = str(obj.get("decision", "")).strip().upper()
            if d not in ("PENDING", "REJECTED"):
                d = "REJECTED"
            mode = _norm_mode(str(obj.get("rule_mode", live_mode)))
            try:
                thr = _clamp_milli(int(obj.get("threshold_milli", live_thr)))
            except Exception:
                thr = live_thr
            try:
                fit = _clamp_milli(int(obj.get("fitness_milli", live_fit)))
            except Exception:
                fit = live_fit
            note = str(obj.get("rule_note", live_note)).strip()[:400]
            if d == "PENDING" and fit <= live_fit:
                d = "REJECTED"
            return json.dumps(
                {
                    "decision": d,
                    "rule_mode": mode,
                    "threshold_milli": thr,
                    "rule_note": note,
                    "fitness_milli": fit,
                    "note": str(obj.get("note", ""))[:200],
                }
            )

        out = gl.eq_principle.prompt_comparative(
            judge,
            "The decision field must be identical. Other fields may differ.",
        )
        agreed = _parse_json(str(out))
        decision = str(agreed.get("decision", "REJECTED")).strip().upper()
        if decision not in ("PENDING", "REJECTED"):
            decision = "REJECTED"

        self.last_propose_at = now

        if decision != "PENDING":
            self.failed_propose_count = self.failed_propose_count + u256(1)
            if self.failed_propose_count >= u256(MAX_FAILURES):
                self.extinct = True
            return "REJECTED"

        try:
            fit = _clamp_milli(int(agreed.get("fitness_milli", live_fit)))
        except Exception:
            self.failed_propose_count = self.failed_propose_count + u256(1)
            return "REJECTED"
        if fit <= live_fit:
            self.failed_propose_count = self.failed_propose_count + u256(1)
            if self.failed_propose_count >= u256(MAX_FAILURES):
                self.extinct = True
            return "REJECTED"

        try:
            thr = _clamp_milli(int(agreed.get("threshold_milli", live_thr)))
        except Exception:
            thr = live_thr
        mode = _norm_mode(str(agreed.get("rule_mode", live_mode)))
        note = str(agreed.get("rule_note", live_note)).strip()[:400]

        self.pending_active = True
        self.pending_rule_mode = mode
        self.pending_threshold_milli = u256(thr)
        self.pending_rule_note = note
        self.pending_fitness_milli = u256(fit)
        self.challenge_open_until = now + u256(CHALLENGE_SECS)
        return "PENDING"

    @gl.public.write
    def challenge(self) -> str:
        self._not_extinct()
        require(self.pending_active is True, "no pending")
        now = _now()
        require(now < self.challenge_open_until, "challenge window closed")

        url = self.signal_url
        host = _host_of(url)
        require(self.is_host_allowed(host), "host not allowed: " + host)

        goal = self.goal_text
        p_mode = self.pending_rule_mode
        p_thr = int(self.pending_threshold_milli)
        p_note = self.pending_rule_note
        p_fit = int(self.pending_fitness_milli)
        live_fit = int(self.committed_fitness_milli)

        def judge() -> str:
            body = gl.nondet.web.render(url, mode="text")
            prompt = f"""
You challenge a PENDING genome under the SEALED GOAL and LIVE SIGNAL.

SEALED GOAL:
{goal}

PENDING GENOME:
rule_mode={p_mode} threshold_milli={p_thr} fitness_milli={p_fit}
note={p_note}
committed_fitness_milli={live_fit}

SIGNAL (truncated):
{str(body)[:5000] if body is not None else ""}

Return ONLY JSON:
- decision: "REVERT" or "UPHOLD"
- note: short reason

REVERT if pending is unsupported, unsafe, or fitness unjustified.
UPHOLD if pending remains justified.
"""
            raw = gl.nondet.exec_prompt(prompt)
            obj = _parse_json(str(raw))
            d = str(obj.get("decision", "")).strip().upper()
            if d not in ("REVERT", "UPHOLD"):
                d = "REVERT"
            return json.dumps({"decision": d, "note": str(obj.get("note", ""))[:200]})

        out = gl.eq_principle.prompt_comparative(
            judge,
            "The decision field must be identical.",
        )
        agreed = _parse_json(str(out))
        decision = str(agreed.get("decision", "REVERT")).strip().upper()
        if decision not in ("REVERT", "UPHOLD"):
            decision = "REVERT"

        if decision == "REVERT":
            self.pending_active = False
            self.pending_rule_mode = "CLOSED"
            self.pending_threshold_milli = u256(0)
            self.pending_rule_note = ""
            self.pending_fitness_milli = u256(0)
            self.challenge_open_until = u256(0)
            return "REVERT"
        return "UPHOLD"

    @gl.public.write
    def finalize_evolve(self) -> str:
        self._not_extinct()
        require(self.pending_active is True, "no pending")
        now = _now()
        require(now >= self.challenge_open_until, "challenge window open")

        prev_fp = _genome_fp(
            self.rule_mode, int(self.threshold_milli), self.rule_note
        )

        self.rule_mode = _norm_mode(self.pending_rule_mode)
        self.threshold_milli = self.pending_threshold_milli
        self.rule_note = self.pending_rule_note
        self.committed_fitness_milli = self.pending_fitness_milli
        self.parent_genome_hash = prev_fp
        self.generation = self.generation + u256(1)
        self.failed_propose_count = u256(0)

        rec = json.dumps(
            {
                "generation": int(self.generation),
                "rule_mode": self.rule_mode,
                "threshold_milli": int(self.threshold_milli),
                "fitness_milli": int(self.committed_fitness_milli),
                "rule_note": self.rule_note[:120],
                "parent_genome_hash": prev_fp[:120],
            }
        )
        self.history.append(rec)

        self.pending_active = False
        self.pending_rule_mode = "CLOSED"
        self.pending_threshold_milli = u256(0)
        self.pending_rule_note = ""
        self.pending_fitness_milli = u256(0)
        self.challenge_open_until = u256(0)
        return "COMMIT"

    @gl.public.write
    def recheck(self) -> str:
        self._not_extinct()
        url = self.signal_url
        host = _host_of(url)
        require(self.is_host_allowed(host), "host not allowed: " + host)

        goal = self.goal_text
        mode = self.rule_mode
        thr = int(self.threshold_milli)
        note = self.rule_note
        committed = int(self.committed_fitness_milli)

        def judge() -> str:
            body = gl.nondet.web.render(url, mode="text")
            if body is None or len(str(body).strip()) < 20:
                return json.dumps(
                    {
                        "decision": "DRIFT",
                        "live_fitness_milli": 0,
                        "note": "empty signal",
                    }
                )
            prompt = f"""
Score how well the LIVE GENOME still fits the SEALED GOAL given SIGNAL.

GOAL: {goal}
GENOME: mode={mode} threshold={thr} note={note}
committed_fitness_milli={committed}

SIGNAL (truncated):
{str(body)[:5000]}

Return ONLY JSON:
- decision: "STABLE" or "DRIFT"
- live_fitness_milli: 0-1000
- note: short

DRIFT if the signal no longer supports the genome (live fitness meaningfully below committed).
STABLE otherwise.
"""
            raw = gl.nondet.exec_prompt(prompt)
            obj = _parse_json(str(raw))
            try:
                live = _clamp_milli(int(obj.get("live_fitness_milli", committed)))
            except Exception:
                live = committed
            d = str(obj.get("decision", "")).strip().upper()
            if live + DRIFT_MARGIN < committed:
                d = "DRIFT"
            elif d not in ("STABLE", "DRIFT"):
                d = "STABLE"
            return json.dumps(
                {
                    "decision": d,
                    "live_fitness_milli": live,
                    "note": str(obj.get("note", ""))[:200],
                }
            )

        out = gl.eq_principle.prompt_comparative(
            judge,
            "The decision field must be identical.",
        )
        agreed = _parse_json(str(out))
        decision = str(agreed.get("decision", "STABLE")).strip().upper()
        if decision not in ("STABLE", "DRIFT"):
            try:
                live = int(agreed.get("live_fitness_milli", committed))
            except Exception:
                live = committed
            if live + DRIFT_MARGIN < committed:
                decision = "DRIFT"
            else:
                decision = "STABLE"
        return decision