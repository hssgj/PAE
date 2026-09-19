import unittest
from semantic_task_tree import TaskTree, SemanticUnit, Task, build_from_interpretation

class TaskTreeTests(unittest.TestCase):
    def setUp(self):
        self.tree = TaskTree("Publish a verified project record")
        self.tree.add_unit(SemanticUnit("u1", "Read project context", "user"))
        self.tree.add_unit(SemanticUnit("u2", "Publish record", "user"))
        self.tree.add_task(Task("read", "u1", "Read", acceptance="Source reviewed"))
        self.tree.add_task(Task("publish", "u2", "Publish", depends_on=["read"],
                                acceptance="Remote record exists",
                                approval_required=True))

    def test_dependencies_and_approval(self):
        self.assertEqual(self.tree.ready(), ["read"])
        self.tree.start("read")
        self.tree.finish("read", verified=True, result="Reviewed document A")
        self.assertEqual(self.tree.ready(), [])
        self.tree.approve("publish")
        self.assertEqual(self.tree.ready(), ["publish"])

    def test_failure_then_retry(self):
        self.tree.start("read")
        self.tree.finish("read", verified=False, result="Source unavailable")
        self.assertEqual(self.tree.tasks["read"].status, "failed")
        self.tree.retry("read")
        self.assertEqual(self.tree.ready(), ["read"])

    def test_unknown_blocks(self):
        self.tree.units["u1"].unknowns.append("Which document?")
        self.assertEqual(self.tree.ready(), [])
        self.tree.resolve_unknown("u1", "Which document?", "User provided source A")
        self.assertEqual(self.tree.ready(), ["read"])

    def test_cycle_rejected_without_corrupting_tree(self):
        with self.assertRaises(ValueError):
            self.tree.revise_dependencies("read", ["publish"])
        self.assertEqual(self.tree.tasks["read"].depends_on, [])

    def test_missing_dependency_rejected(self):
        with self.assertRaises(ValueError):
            self.tree.add_task(Task("bad", "u1", "Bad", ["absent"], acceptance="Done"))
        self.assertNotIn("bad", self.tree.tasks)

    def test_model_interpretation_does_not_execute(self):
        tree = build_from_interpretation("Write summary", {
            "units": [{"id": "u", "goal": "Draft summary", "source": "model"}],
            "tasks": [{"id": "t", "unit_id": "u", "title": "Draft",
                       "acceptance": "Draft available"}]
        })
        self.assertEqual(tree.ready(), ["t"])
        self.assertEqual(tree.tasks["t"].status, "pending")
        self.assertIn('"revision"', tree.snapshot())

if __name__ == "__main__":
    unittest.main()
