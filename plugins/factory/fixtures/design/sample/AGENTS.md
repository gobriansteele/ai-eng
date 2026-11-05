# Owner-report sample

Synthetic two-component file handoff; Python 3.11+ and the standard library only.
The two commands are maintained and released separately. There is no network,
credential, shared service or dependency install. Read `architecture.md` for the
current inter-component contract and its ownership constraints.

From this repository, using an observed compatible Python executable:

```sh
python3 export_tasks.py
python3 export_tasks.py | python3 report_import.py
python3 report_import.py < legacy-export.json
```

Preserve this baseline during investigation and design. Read and run only the
copied disposable checkout, not installed fixtures. Temporary probes and outputs
belong in factory runtime evidence; do not implement the feature or edit sample
files. Record the examined Git revision/tree and actual executable/version.
