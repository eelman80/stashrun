# stashrun

> A CLI tool to snapshot and restore environment variables across project contexts.

---

## Installation

```bash
pip install stashrun
```

Or install from source:

```bash
git clone https://github.com/yourname/stashrun.git && cd stashrun && pip install .
```

---

## Usage

Snapshot your current environment variables into a named stash:

```bash
stashrun save myproject
```

Restore a previously saved snapshot:

```bash
stashrun load myproject
```

List all saved stashes:

```bash
stashrun list
```

Delete a stash:

```bash
stashrun drop myproject
```

Show the contents of a stash without loading it:

```bash
stashrun show myproject
```

Stashes are stored locally in `~/.stashrun/` as encrypted JSON files, scoped by name so you can switch between project contexts without losing your environment state.

---

## Example Workflow

```bash
# Working on Project A
export DATABASE_URL=postgres://localhost/project_a
stashrun save project-a

# Switch to Project B
stashrun load project-b

# Come back later
stashrun load project-a
```

---

## License

MIT © [yourname](https://github.com/yourname)
