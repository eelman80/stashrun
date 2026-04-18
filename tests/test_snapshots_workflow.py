import pytest
from unittest.mock import patch
from stashrun.snapshots_workflow import (
    create_workflow, delete_workflow, get_workflow,
    list_workflows, add_step, remove_step, run_workflow,
)


@pytest.fixture(autouse=True)
def isolated_stash_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("STASHRUN_DIR", str(tmp_path))
    return tmp_path


def test_create_workflow_new():
    assert create_workflow("deploy", ["snap1", "snap2"]) is True
    wf = get_workflow("deploy")
    assert wf is not None
    assert wf["steps"] == ["snap1", "snap2"]


def test_create_workflow_duplicate():
    create_workflow("deploy", [])
    assert create_workflow("deploy", ["snap1"]) is False


def test_delete_workflow_existing():
    create_workflow("wf", [])
    assert delete_workflow("wf") is True
    assert get_workflow("wf") is None


def test_delete_workflow_missing():
    assert delete_workflow("ghost") is False


def test_list_workflows_empty():
    assert list_workflows() == []


def test_list_workflows_multiple():
    create_workflow("a", [])
    create_workflow("b", [])
    assert set(list_workflows()) == {"a", "b"}


def test_add_step_success():
    create_workflow("wf", [])
    assert add_step("wf", "snap1") is True
    assert get_workflow("wf")["steps"] == ["snap1"]


def test_add_step_missing_workflow():
    assert add_step("ghost", "snap1") is False


def test_remove_step_success():
    create_workflow("wf", ["a", "b", "c"])
    assert remove_step("wf", 1) is True
    assert get_workflow("wf")["steps"] == ["a", "c"]


def test_remove_step_out_of_range():
    create_workflow("wf", ["a"])
    assert remove_step("wf", 5) is False


def test_remove_step_missing_workflow():
    assert remove_step("ghost", 0) is False


def test_run_workflow_all_present():
    create_workflow("wf", ["snap1", "snap2"])
    with patch("stashrun.snapshots_workflow.get_snapshot", return_value={"K": "V"}), \
         patch("stashrun.snapshots_workflow.restore_snapshot") as mock_restore:
        applied, missing = run_workflow("wf")
    assert applied == 2
    assert missing == []
    assert mock_restore.call_count == 2


def test_run_workflow_some_missing():
    create_workflow("wf", ["snap1", "missing_snap"])
    def fake_get(name):
        return {"K": "V"} if name == "snap1" else None
    with patch("stashrun.snapshots_workflow.get_snapshot", side_effect=fake_get), \
         patch("stashrun.snapshots_workflow.restore_snapshot"):
        applied, missing = run_workflow("wf")
    assert applied == 1
    assert missing == ["missing_snap"]


def test_run_workflow_not_found():
    applied, missing = run_workflow("nonexistent")
    assert applied == 0
    assert missing == []
