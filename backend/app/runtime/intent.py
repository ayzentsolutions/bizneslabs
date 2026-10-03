from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Intent:
    name: str
    arguments: dict
    confidence: float

class IntentRouter:
    """Conservative deterministic router used before an LLM tool planner.

    It extracts only fields needed by explicitly registered tools.
    """
    INVENTORY = re.compile(r"(?P<color>white|black|red|blue|silver|grey|gray)?\s*(?P<model>creta|venue|verna)(?:\s+(?P<variant>sx|s\(o\)|s))?", re.I)
    def route(self, text: str) -> Intent:
        lower=text.lower()
        match=self.INVENTORY.search(lower)
        if match and any(x in lower for x in ("available","availability","stock","price","in stock")):
            args={k:v for k,v in match.groupdict().items() if v}
            return Intent("check_inventory",args,0.94)
        if any(x in lower for x in ("test drive","test-drive","testdrive")):
            return Intent("check_appointment_slots",{},0.91)
        if any(x in lower for x in ("call me","callback","salesperson")):
            return Intent("create_lead",{},0.82)
        return Intent("knowledge_answer",{},0.60)
