"""PAE Core prototype: explicit semantic interpretation -> mutable, inspectable task tree.

No LLM, persistence, tool execution, or authorization service is claimed here.
Python 3.10+; standard library only.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Literal
import json

Status = Literal["pending", "blocked", "ready", "running", "done", "failed"]
Source = Literal["user", "model", "tool", "inferred", "unknown"]
STATES = {"pending", "blocked", "ready", "running", "done", "failed"}

@dataclass
class SemanticUnit:
    id: str
    goal: str
    source: Source
    evidence: str = ""
    unknowns: list[str] = field(default_factory=list)

@dataclass
class Task:
    id: str
    unit_id: str
    title: str
    depends_on: list[str] = field(default_factory=list)
    required_capabilities: list[str] = field(default_factory=list)
    acceptance: str = ""
    status: Status = "pending"
    approval_required: bool = False
    approved: bool = False
    result: str | None = None

@dataclass
class TaskTree:
    objective: str
    units: dict[str, SemanticUnit] = field(default_factory=dict)
    tasks: dict[str, Task] = field(default_factory=dict)
    revision: int = 0
    events: list[dict] = field(default_factory=list)

    def add_unit(self, unit: SemanticUnit) -> None:
        if not unit.id or not unit.goal or unit.id in self.units:
            raise ValueError("Unit needs unique nonempty id and goal")
        if unit.source not in ("user", "model", "tool", "inferred", "unknown"):
            raise ValueError("Invalid provenance")
        self.units[unit.id] = unit
        self._record("add_unit", unit.id)

    def add_task(self, task: Task) -> None:
        if not task.id or not task.title or task.id in self.tasks:
            raise ValueError("Task needs unique nonempty id and title")
        if task.unit_id not in self.units:
            raise ValueError("Task needs existing semantic unit")
        if not task.acceptance:
            raise ValueError("Task needs a checkable acceptance criterion")
        if task.status != "pending" or task.approved or task.result is not None:
            raise ValueError("New task must start pending, unapproved, without result")
        if len(set(task.depends_on)) != len(task.depends_on):
            raise ValueError("Duplicate dependencies")
        if any(dep not in self.tasks for dep in task.depends_on):
            raise ValueError("Dependencies must exist when task is added")
        self.tasks[task.id] = task
        try:
            self._validate_graph()
        except ValueError:
            del self.tasks[task.id]
            raise
        self._record("add_task", task.id)

    def _validate_graph(self) -> None:
        visited, active = set(), set()
        def walk(task_id: str) -> None:
            if task_id in active:
                raise ValueError("Dependency cycle")
            if task_id in visited:
                return
            active.add(task_id)
            for dep in self.tasks[task_id].depends_on:
                if dep not in self.tasks:
                    raise ValueError("Missing dependency")
                walk(dep)
            active.remove(task_id)
            visited.add(task_id)
        for task_id in self.tasks:
            walk(task_id)

    def revise_dependencies(self, task_id: str, dependencies: list[str]) -> None:
        task = self.tasks[task_id]
        if task.status in ("running", "done"):
            raise ValueError("Cannot rewire running or completed task")
        if len(set(dependencies)) != len(dependencies):
            raise ValueError("Duplicate dependencies")
        old = task.depends_on[:]
        task.depends_on = dependencies[:]
        try:
            self._validate_graph()
        except ValueError:
            task.depends_on = old
            raise
        self._record("revise_dependencies", task_id)

    def ready(self) -> list[str]:
        """Return eligible tasks; approval and missing knowledge gate eligibility."""
        result = []
        for task in self.tasks.values():
            unit = self.units[task.unit_id]
            if task.status not in ("pending", "blocked", "ready"):
                continue
            if unit.unknowns or (task.approval_required and not task.approved):
                continue
            if all(self.tasks[dep].status == "done" for dep in task.depends_on):
                result.append(task.id)
        return result

    def approve(self, task_id: str) -> None:
        task = self.tasks[task_id]
        if task.status in ("running", "done"):
            raise ValueError("Approval must precede execution")
        task.approved = True
        self._record("approve", task_id)

    def start(self, task_id: str) -> None:
        if task_id not in self.ready():
            raise ValueError("Task not eligible: dependencies, unknowns or approval")
        self.tasks[task_id].status = "running"
        self._record("start", task_id)

    def finish(self, task_id: str, *, verified: bool, result: str) -> None:
        task = self.tasks[task_id]
        if task.status != "running" or not result.strip():
            raise ValueError("Only running tasks can finish with a recorded result")
        task.status = "done" if verified else "failed"
        task.result = result
        self._record("verified" if verified else "failed", task_id)

    def retry(self, task_id: str) -> None:
        task = self.tasks[task_id]
        if task.status != "failed":
            raise ValueError("Only failed tasks can be retried")
        task.status, task.result = "pending", None
        self._record("retry", task_id)

    def resolve_unknown(self, unit_id: str, unknown: str, evidence: str) -> None:
        unit = self.units[unit_id]
        if unknown not in unit.unknowns or not evidence.strip():
            raise ValueError("Unknown and supporting evidence required")
        unit.unknowns.remove(unknown)
        unit.evidence += ("\n" if unit.evidence else "") + evidence
        self._record("resolve_unknown", unit_id)

    def snapshot(self) -> str:
        return json.dumps({
            "objective": self.objective,
            "revision": self.revision,
            "units": [asdict(u) for u in self.units.values()],
            "tasks": [asdict(t) for t in self.tasks.values()],
            "ready": self.ready(),
            "events": self.events,
        }, ensure_ascii=False, indent=2)

    def _record(self, event: str, item_id: str) -> None:
        self.revision += 1
        self.events.append({"revision": self.revision, "event": event, "item": item_id})


def build_from_interpretation(objective: str, spec: dict) -> TaskTree:
    """Convert validated, explicitly supplied semantic structure into a TaskTree.

    The spec may come from a human or later from a Qwen adapter. This function
    does NOT claim to understand free text or treat model output as verified facts.
    """
    if not objective.strip() or not isinstance(spec, dict):
        raise ValueError("Objective and interpretation required")
    tree = TaskTree(objective=objective)
    for unit in spec.get("units", []):
        tree.add_unit(SemanticUnit(**unit))
    for task in spec.get("tasks", []):
        tree.add_task(Task(**task))
    return tree
