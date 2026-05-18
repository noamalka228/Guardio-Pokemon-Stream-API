from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class Pokemon:
    """
    Dataclass representing a Pokemon object.
    Matches the fields from the protobuf schema.
    """
    number: int
    name: str
    type_one: str
    type_two: str
    total: int
    hit_points: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int
    generation: int
    legendary: bool

    @classmethod
    def from_proto(cls, proto_obj: Any) -> "Pokemon":
        """
        Creates a Pokemon dataclass instance from a Protobuf Pokemon object.
        """
        return cls(
            number=proto_obj.number,
            name=proto_obj.name,
            type_one=proto_obj.type_one,
            type_two=proto_obj.type_two,
            total=proto_obj.total,
            hit_points=proto_obj.hit_points,
            attack=proto_obj.attack,
            defense=proto_obj.defense,
            special_attack=proto_obj.special_attack,
            special_defense=proto_obj.special_defense,
            speed=proto_obj.speed,
            generation=proto_obj.generation,
            legendary=proto_obj.legendary
        )

    def to_dict(self) -> dict:
        """
        Converts the Pokemon dataclass instance to a standard dictionary.
        """
        return asdict(self)
