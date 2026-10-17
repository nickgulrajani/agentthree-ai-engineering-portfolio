"""Suite shape and determinism."""

from agentthree_agent_eval.simulate import AgentConfig, simulate_task
from agentthree_agent_eval.tasks import TASKS, build_tasks


def test_suite_has_forty_tasks():
    assert len(TASKS) == 40
    assert len(build_tasks()) == 40


def test_categories_cover_adversarial_and_refund():
    cats = {t.category for t in TASKS}
    assert {"status", "refund", "billing", "trouble", "adv"} <= cats
    assert any(t.trajectory == () for t in TASKS if t.category == "adv")


def test_simulate_is_deterministic_for_seed():
    cfg = AgentConfig(model="medium", plan="plan", desc="detailed")
    task = TASKS[0]
    a = simulate_task(cfg, task, seed=7, trial=0)
    b = simulate_task(cfg, task, seed=7, trial=0)
    assert a.ok == b.ok
    assert a.latency == b.latency
    assert a.cost == b.cost
    assert [s.tool for s in a.steps] == [s.tool for s in b.steps]
