You are patching one component of an existing problem. Do **not** regenerate the whole problem.

## Expected parameters

| Parameter | Required | Description |
|---|---|---|
| `name` | yes | Folder under `problems/` |
| `component` | yes | `statement`, `tutorial`, `validator`, `checker`, `interactor`, `acc`, `acc_java`, `acc_alt`, `brute`, `wa`, `generator` |
| `issue` | yes | Paste the `verify.sh` section, Polygon warning, or invocation log |

Arguments:

$ARGUMENTS

---

Read `guidelines.md` and the current file for that component. Spawn **only** the matching sub-agent with the existing source plus the issue as feedback. Write the new file. Then run:

```bash
./verify.sh problems/<name>
```

If originality was the failure, do not "fix" the statement wording to dodge the search — stop and ask for a new idea (unless difficulty is Ace or Div2-A).
