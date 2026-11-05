import json
from pathlib import Path


def export_rows(tasks):
    return [
        {"id": task["id"], "title": task["title"], "status": task["status"]}
        for task in tasks
    ]


if __name__ == "__main__":
    tasks = json.loads(Path(__file__).with_name("tasks.json").read_text())
    print(json.dumps(export_rows(tasks)))
