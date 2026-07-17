from Server import AutomationManager


def test_add_rule(tmp_path):

    rules_file = tmp_path / "automation.json"

    manager = AutomationManager(
        rules_file=rules_file
    )

    manager.add_schedule_rule(
        "Test",
        "20:00",
        lambda: None
    )

    assert len(manager.rules) == 1