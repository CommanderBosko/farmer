---
name: secret-scan
description: Triggers when the user says "secret scan", "scan for secrets", "check for leaked secrets", "any secrets in the repo", or "pre-public check". Read-only scan of the working tree and full git history for plaintext secrets, tuned to this project's no-dedicated-scheme (game-bot repo, no credentials) setup.
model: haiku
version: 0.1.0
---

# Secret Scan

A read-only guard that scans the **working tree and full git history** for plaintext
secrets before a push or before changing repo visibility.

## Arguments

None.

## What it knows about this project

- **Secret-management scheme:** None. This is a procedural Python bot for the game "The Farmer Was Replaced"; it has no API keys, credentials or encrypted secrets, and no sops / git-crypt / .env scheme. The scan is therefore generic: baseline key/token patterns plus a .gitignore coverage check.
- **Encrypted/managed secret locations:** None. No encrypted or managed-secret directory exists, so the encrypted-secret integrity pass is a no-op.
- **Paths excluded from pattern matching:** Only this skill's own directory, `.claude/skills/secret-scan/` (its docs contain example patterns). Everything else, including the other project skills, is scanned.
- **Known intentional non-secrets (don't flag these):** The git author name/email in commit metadata; the Steam app id 2060160 and the game's Proton save-folder paths (`~/.local/share/Steam/...`) that appear in docs and skills; game constants in `main.py`/`config.py`. Nothing else in the repo is intentionally secret-shaped.
- **Full git-history scan:** Enabled. Every commit is scanned (small repo: ~76 commits, ~3 MB `.git`).

## Instructions

1. Run `scripts/secret-scan.sh`. It performs four passes:
   - **Working tree** — high-signal patterns (private-key blocks, password hashes,
     GitHub/AWS/Slack tokens) across tracked files, excluding the
     configured paths.
   - **Encrypted-secret integrity** — a no-op for this project (no encrypted-secret scheme is configured); it prints a skip line.
   - **Git history** — the same high-signal patterns across *all commits* (catches
     secrets that were committed then removed but still live in history). Prints
     `commit:path` hits. History scanning is enabled for this project.
   - **.gitignore coverage** — informational check that common secret-file extensions
     are ignored.

2. Report the result. If **clean**, say so plainly. If there are findings, present each
   with its location and the right remediation:
   - **Plaintext secret in the working tree** → remove the literal from the file, rotate the credential, and keep real values out of the repo (for example an untracked, gitignored local file); then re-run to check history.
   - **Unencrypted managed-secret file** → N/A. No managed-secret location is configured for this project.
   - **Secret found in history** (but not the tree) → it was removed but persists in past
     commits. Removing it now is **not** enough for a public repo — rewrite history with
     `git filter-repo --replace-text` (replace the literal with a redaction marker), then
     force-push, then realign other clones (`git fetch && git reset --hard origin/main`).
     Consider rotating the leaked credential regardless.

3. The history pass scans every commit, so on a large repo it can take a little time — tell
   the user it's working if it pauses.

## Notes

- Purely read-only; never modifies files or git state.
- Pattern-based, so it's a strong guard, not a proof of absence. Treat a clean result as
  "no high-signal leaks found," and still apply judgment for project-specific secrets.
- To add a new secret pattern, edit `EXTRA_PATTERNS` in `scripts/secret-scan.sh`.

## Script

```
scripts/secret-scan.sh
```
