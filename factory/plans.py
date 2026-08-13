from dataclasses import dataclass


@dataclass(frozen=True)
class Plan:
    name: str
    days: int
    max_bots: int


PLANS = {
    "free": Plan(
        name="مجاني",
        days=7,
        max_bots=1,
    ),
    "monthly": Plan(
        name="شهري",
        days=30,
        max_bots=5,
    ),
    "premium": Plan(
        name="مميز",
        days=90,
        max_bots=20,
    ),
}


def get_plan(name: str) -> Plan | None:
    return PLANS.get(name)
