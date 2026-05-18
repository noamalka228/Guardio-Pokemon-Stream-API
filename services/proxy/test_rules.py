import unittest
from unittest.mock import MagicMock
import sys
import os

# Set up path so we can import app modules correctly
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))
sys.path.append(os.path.dirname(__file__))

from app.core.utils import evaluate_condition, evaluate_rules
from app.models.pokemon import Pokemon


class TestPokemonRuleEngine(unittest.TestCase):

    def setUp(self):
        # Sample Pokemon to test against
        self.pikachu = Pokemon(
            number=25,
            name="Pikachu",
            type_one="Electric",
            type_two="",
            total=320,
            hit_points=35,
            attack=55,
            defense=40,
            special_attack=50,
            special_defense=50,
            speed=90,
            generation=1,
            legendary=False
        )

        self.mewtwo = Pokemon(
            number=150,
            name="Mewtwo",
            type_one="Psychic",
            type_two="",
            total=680,
            hit_points=106,
            attack=110,
            defense=90,
            special_attack=154,
            special_defense=90,
            speed=130,
            generation=1,
            legendary=True
        )

    def test_evaluate_condition_boolean(self):
        # Mewtwo is legendary
        self.assertTrue(evaluate_condition(self.mewtwo, "legendary==true"))
        self.assertTrue(evaluate_condition(self.mewtwo, "legendary == true"))
        self.assertFalse(evaluate_condition(self.mewtwo, "legendary==false"))

        # Pikachu is not legendary
        self.assertFalse(evaluate_condition(self.pikachu, "legendary==true"))
        self.assertTrue(evaluate_condition(self.pikachu, "legendary==false"))

    def test_evaluate_condition_numeric(self):
        # Speed checks
        self.assertTrue(evaluate_condition(self.mewtwo, "speed>100"))
        self.assertFalse(evaluate_condition(self.pikachu, "speed>100"))
        self.assertTrue(evaluate_condition(self.pikachu, "speed<100"))
        self.assertTrue(evaluate_condition(self.pikachu, "speed<=90"))
        self.assertTrue(evaluate_condition(self.pikachu, "speed>=90"))

        # HP check
        self.assertTrue(evaluate_condition(self.pikachu, "hit_points==35"))
        self.assertTrue(evaluate_condition(self.pikachu, "hit_points!=20"))

    def test_evaluate_condition_string(self):
        self.assertTrue(evaluate_condition(self.pikachu, "type_one==Electric"))
        self.assertTrue(evaluate_condition(self.pikachu, "type_two!=word"))
        self.assertFalse(evaluate_condition(self.pikachu, "type_one==Fire"))

    def test_evaluate_condition_missing_attribute(self):
        # Attribute that doesn't exist on DummyPokemon
        self.assertFalse(evaluate_condition(self.pikachu, "unknown_field==value"))

    def test_evaluate_rules_and_logic(self):
        rules = [
            {
                "url": "http://destination-service:8001/receive",
                "reason": "legendary pokemon detected",
                "match": ["legendary==true"]
            },
            {
                "url": "http://destination-service:8001/receive",
                "reason": "high speed pokemon",
                "match": ["speed>100"]
            },
            {
                "url": "http://destination-service:8001/receive",
                "reason": "awesome pokemon",
                "match": [
                    "hit_points==35",
                    "type_two!=word",
                    "special_defense > 10",
                    "generation< 20"
                ]
            }
        ]

        # Mewtwo should match legendary and high speed (2 rules)
        mewtwo_matches = evaluate_rules(self.mewtwo, rules)
        self.assertEqual(len(mewtwo_matches), 2)
        reasons = [r["reason"] for r in mewtwo_matches]
        self.assertIn("legendary pokemon detected", reasons)
        self.assertIn("high speed pokemon", reasons)

        # Pikachu should match awesome pokemon (1 rule)
        pikachu_matches = evaluate_rules(self.pikachu, rules)
        self.assertEqual(len(pikachu_matches), 1)
        self.assertEqual(pikachu_matches[0]["reason"], "awesome pokemon")


if __name__ == "__main__":
    unittest.main()
