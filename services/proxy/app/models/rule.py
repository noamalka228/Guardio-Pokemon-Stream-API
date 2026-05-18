from dataclasses import dataclass

@dataclass
class Rule:
    """
    Dataclass representing a rule object.
    Matches the fields from the protobuf schema.
    """
    url: str
    reason: str
    match: List[str]
