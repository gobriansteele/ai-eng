import argparse
import json
from pathlib import Path


def load_tasks():
    return json.loads(Path(__file__).with_name("tasks.json").read_text())


def select_tasks(tasks, status):
    if status == "all":
        return tasks
    return [task for task in tasks if task["status"] == "open"]


def main():
    parser = argparse.ArgumentParser(description="List local taskboard tasks")
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list")
    listing.add_argument("--status", choices=("open", "done", "all"), default="open")
    args = parser.parse_args()
    for task in select_tasks(load_tasks(), args.status):
        print(f"{task['id']}\t{task['status']}\t{task['title']}")


if __name__ == "__main__":
    main()
