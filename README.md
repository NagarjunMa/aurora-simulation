# Aurora Genesis Path Simulation

A small FastAPI live coding assignment that compares independent paths from
the same initial state. Each step updates energy, strain, and momentum using
the environment's demand, recovery, and opportunity values.

## Run locally

Requirements: Python 3.12 or newer and [uv](https://docs.astral.sh/uv/getting-started/installation/).
Run these commands from the repository root:

```sh
uv sync --locked
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/docs** for the interactive API demo.
Check **http://127.0.0.1:8000/health** for server health. Stop the server with
Ctrl+C. No API keys, environment variables, database, or external services are
needed. `uv sync` installs the project and test dependencies into `.venv`.

## Demo

In `/docs`, expand `POST /simulate`, click **Try it out**, paste the contents of
[`examples/simulation.json`](examples/simulation.json), and click **Execute**.
Or, with the server running:

```sh
curl -sS http://127.0.0.1:8000/simulate \
  -H 'Content-Type: application/json' \
  --data-binary @examples/simulation.json
```

The response contains a `trajectory` array and a `final_state` for each named
path. Array index 0 is the initial state; later indices correspond to steps.
The sample's `balanced` path finishes at:

```json
{"energy": 52, "strain": 18, "momentum": 12}
```

Every path starts independently from the same initial state. An empty step
list returns just that initial state. At least one named path is required.

## Simulation rules

For each step, with `clamp` bounding a value to 0–100:

```text
energy   = clamp(previous_energy - demand + recovery)
strain   = clamp(previous_strain + demand - recovery)
momentum = clamp(previous_momentum + opportunity - (strain // 10))
```

Momentum uses the newly calculated strain. Initial state values must be
integers from 0–100, and environment values must be integers from 0–10.
Invalid requests return HTTP 422 with validation details.

## Checks

```sh
uv run pytest -q
```

The tests cover health/docs, exact multi-step results, independent paths,
empty step lists, clamping, repeated requests, and invalid input.

## Project layout

```text
main.py                    FastAPI endpoints
src/workspace/model.py     Domain dataclasses
src/workspace/evaluate.py  Simulation rules and path evaluation
src/workspace/models.py    API request and response schemas
tests/                     API regression tests
examples/simulation.json   Ready-to-use demo request
```

## Sharing on GitHub

Include the source, tests, example, `pyproject.toml`, `uv.lock`, `.python-version`,
and documentation. The lockfile lets teammates install the same dependency
versions. `.gitignore` excludes the local environment, caches, logs, and `.env`
files. Review `git status --short` before committing.

This is an in-memory assignment demo: it does not persist results or provide
authentication. The server binds to localhost by default.
