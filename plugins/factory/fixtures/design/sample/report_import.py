import json
import sys


def render_report(rows):
    for row in rows:
        if set(row) != {"id", "title", "status"}:
            raise ValueError("Unsupported task feed row fields")
    return "\n".join(f"{row['id']}\t{row['title']}\t{row['status']}" for row in rows)


if __name__ == "__main__":
    print(render_report(json.load(sys.stdin)))
