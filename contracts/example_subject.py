# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *

try:
    _UserError = gl.vm.UserError
except Exception:
    _UserError = Exception


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise _UserError(msg)


class ExampleSubject(gl.Contract):
    fitform_addr: Address
    acts: u256

    def __init__(self, fitform_addr: str):
        # Studio may pass address as hex string
        addr = (fitform_addr or "").strip()
        require(len(addr) > 0, "fitform_addr required")
        if not addr.startswith("0x") and not addr.startswith("0X"):
            addr = "0x" + addr
        self.fitform_addr = Address(addr)
        self.acts = u256(0)

    def _require_allowed(self, action: str) -> None:
        ff = gl.get_contract_at(self.fitform_addr)
        ok = ff.view().allows(action)
        require(ok is True, "action not allowed by FitForm")

    @gl.public.write
    def act(self) -> str:
        self._require_allowed("withdraw")
        self.acts = self.acts + u256(1)
        return "ok"

    @gl.public.view
    def get_acts(self) -> u256:
        return self.acts

    @gl.public.view
    def status(self) -> str:
        ff = gl.get_contract_at(self.fitform_addr)
        if ff.view().allows("withdraw"):
            return "OPEN"
        return "RESTRICTED"