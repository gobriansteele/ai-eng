# Taskboard sample

This is an isolated standard-library command-line task list. Python 3.11+ is the
only requirement. Data lives in `tasks.json`; commands read it without writes.

Run from this repository:

```sh
python3 tasks.py list
python3 tasks.py list --status done
python3 -m unittest -v
```

The CLI lists ID, status and title, with `open`, `done` and `all` status selectors.
Read `tasks.py`, `tasks.json` and `test_tasks.py` for the current behavior.
Do not change this baseline during investigation. Temporary probes/tests belong
in the factory runtime evidence directory and must identify the examined revision.
There are no integrations, credentials, network calls or dependency installs.
