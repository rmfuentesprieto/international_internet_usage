from dataclasses import dataclass


@dataclass
class InternationalUsage:
    Country: str
    Year: int
    UsagePercentage: float
    Source: str
