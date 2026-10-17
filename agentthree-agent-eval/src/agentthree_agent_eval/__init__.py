"""Offline agent evaluation: seeded simulator, scorecard, regression gate."""

from .gate import GateResult, evaluate_gate
from .metrics import Scorecard, run_suite
from .simulate import AgentConfig, simulate_task
from .tasks import TASKS, build_tasks

__all__ = [
    "AgentConfig",
    "GateResult",
    "Scorecard",
    "TASKS",
    "build_tasks",
    "evaluate_gate",
    "run_suite",
    "simulate_task",
]

__version__ = "0.1.0"
