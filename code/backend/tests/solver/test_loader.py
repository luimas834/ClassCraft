"""Tests for loading solver problems from JSON fixtures."""

from pathlib import Path

from solver.loader_json import load_problem

FIXTURES = Path(__file__).parent.parent / "fixtures"
IUT_DATA = Path(__file__).parents[2] / "app" / "seed_data" / "iut_cse.json"


def test_iut_dataset_loads_with_expected_counts():
    problem, placements = load_problem(IUT_DATA)

    assert len(problem.cards) == 307
    assert len(problem.teachers) == 58
    assert len(problem.rooms) == 31
    assert len(problem.classes) == 27

    assert sum(card.fixed_day is not None for card in problem.cards) == 18
    assert sum(len(card.weeks) == 1 for card in problem.cards) == 42
    assert len({item.entity_id for item in problem.time_off}) == 16
    assert len(placements) == 307


def test_tiny_fixture_loads():
    problem, placements = load_problem(FIXTURES / "tiny.json")

    assert len(problem.days) == 2
    assert len(problem.teachers) == 2
    assert len(problem.rooms) == 2
    assert len(problem.classes) == 1
    assert len(problem.cards) == 5
    assert len(placements) == 5
    assert len(problem.time_off) == 2


def test_impossible_fixture_loads():
    problem, placements = load_problem(FIXTURES / "impossible.json")

    assert len(problem.classes) == 2
    assert len(problem.cards) == 5
    assert len(placements) == 0
    assert len(problem.time_off) == 1


def test_medium_fixture_loads():
    problem, placements = load_problem(FIXTURES / "medium.json")

    expected_classes = {
        "CSE1-S1",
        "CSE1-S2",
        "SWE1",
        "CSE3-S1",
        "CSE3-S2",
        "SWE3",
    }

    assert {item.id for item in problem.classes} == expected_classes
    assert len(problem.cards) == 114
    assert len(placements) == 114
    assert all(
        audience.class_id in expected_classes
        for card in problem.cards
        for audience in card.audiences
    )


def test_tiny_fixture_matches_hand_checked_expected_placements():
    problem, placements = load_problem(FIXTURES / "tiny.json")

    actual = {
        (p.card_id, p.day, p.start_period, p.room)
        for p in placements
    }

    expected = {
        ("C1", "Mon", 1, "R1"),
        ("C2", "Mon", 3, "L1"),
        ("C3", "Tue", 1, "R1"),
        ("C4", "Tue", 2, "L1"),
        ("C5", "Tue", 3, "R1"),
    }

    assert actual == expected

    fixed_cards = {
        card.id for card in problem.cards if card.fixed_day is not None
    }
    assert fixed_cards == {"C1", "C3"}
