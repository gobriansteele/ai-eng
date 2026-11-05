import unittest

from tasks import load_tasks, select_tasks


class TaskSelectionTests(unittest.TestCase):
    def test_default_open_selection(self):
        self.assertEqual([task["id"] for task in select_tasks(load_tasks(), "open")], [1])

    def test_completed_selection(self):
        self.assertEqual([task["id"] for task in select_tasks(load_tasks(), "done")], [2])

    def test_all_selection(self):
        self.assertEqual(len(select_tasks(load_tasks(), "all")), 2)


if __name__ == "__main__":
    unittest.main()
