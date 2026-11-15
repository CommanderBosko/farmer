#!/usr/bin/env python3
"""One-way repo -> game sync for The Farmer Was Replaced (host-side helper, not game code).

Why this exists: the game saves code files atomically (File.Replace). When a Save0/*.py
file was a symlink out to this repo, that swap crossed two bind mounts inside the Proton
container (/home/bosko vs compatdata/2060160) and failed with "Not same device", so the
game showed "Failed to write to the save files of Save0". Save0 now holds REAL files and
this script copies repo -> Save0 whenever a repo file changes.

Tracked set: every Save0/*.py (except __builtins__.py) that is a regular file and has a
same-named file next to this script. Copies are written in place so the in-game File
Watcher sees a normal content change.

Usage:
  python3 sync_save.py                   watch forever (run by the systemd user service)
  python3 sync_save.py --once            sync every tracked file once, then exit
  python3 sync_save.py --add A.py [B.py] put repo files into Save0 as real files (also
                                         converts a leftover symlink). A brand-new file
                                         still needs a save reload before the game lists it.
  --repo DIR / --save0 DIR               override paths (testing)
"""
import os
import sys
import time

DEFAULT_SAVE0 = os.path.expanduser(
    "~/.local/share/Steam/steamapps/compatdata/2060160/pfx/drive_c/users/steamuser/"
    "AppData/LocalLow/TheFarmerWasReplaced/TheFarmerWasReplaced/Saves/Save0"
)
DEFAULT_REPO = os.path.dirname(os.path.abspath(__file__))
SKIP = ("__builtins__.py",)
POLL_SECONDS = 0.5


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def sig(path):
    st = os.stat(path)
    return (st.st_mtime_ns, st.st_size)


def read_bytes(path):
    f = open(path, "rb")
    data = f.read()
    f.close()
    return data


def copy_in_place(src, dst):
    """Copy src over dst without replacing the inode. Returns True if bytes changed."""
    data = read_bytes(src)
    if os.path.isfile(dst) and not os.path.islink(dst) and read_bytes(dst) == data:
        return False
    f = open(dst, "wb")
    f.write(data)
    f.close()
    return True


def tracked(repo, save0, warned):
    names = []
    for n in sorted(os.listdir(save0)):
        if not n.endswith(".py") or n in SKIP:
            continue
        if not os.path.isfile(os.path.join(repo, n)):
            continue
        if os.path.islink(os.path.join(save0, n)):
            if n not in warned:
                warned.add(n)
                log("WARN " + n + " in Save0 is still a symlink (game cannot save it) - run: sync_save.py --add " + n)
            continue
        names.append(n)
    return names


def add_files(repo, save0, names):
    status = 0
    for n in names:
        src = os.path.join(repo, n)
        dst = os.path.join(save0, n)
        if not n.endswith(".py") or n in SKIP or os.path.basename(n) != n:
            log("SKIP " + n + " (not a plain repo .py name)")
            status = 1
            continue
        if not os.path.isfile(src):
            log("MISSING " + src)
            status = 1
            continue
        was_link = os.path.islink(dst)
        if was_link:
            os.remove(dst)
        copy_in_place(src, dst)
        if was_link:
            log("converted symlink -> real file: " + n)
        else:
            log("added " + n)
    return status


def sync_once(repo, save0):
    warned = set()
    changed = 0
    for n in tracked(repo, save0, warned):
        if copy_in_place(os.path.join(repo, n), os.path.join(save0, n)):
            log("synced " + n)
            changed += 1
    log("done, " + str(changed) + " file(s) updated")
    return 0


def watch(repo, save0):
    log("watching " + repo + " -> " + save0)
    seen = {}    # name -> repo signature at the previous poll
    done = {}    # name -> repo signature last synced (or already identical)
    warned = set()
    while True:
        for n in tracked(repo, save0, warned):
            src = os.path.join(repo, n)
            dst = os.path.join(save0, n)
            try:
                s = sig(src)
                if n not in seen:
                    seen[n] = s
                    # First sight: only copy if the repo copy is newer than Save0's.
                    if s[0] > os.stat(dst).st_mtime_ns and copy_in_place(src, dst):
                        log("synced " + n + " (startup, repo newer)")
                    done[n] = s
                elif s != seen[n]:
                    seen[n] = s          # still changing; wait one more poll
                elif done.get(n) != s:
                    if copy_in_place(src, dst):
                        log("synced " + n)
                    done[n] = s
            except OSError as e:
                log("ERROR " + n + ": " + str(e) + " (will retry)")
        time.sleep(POLL_SECONDS)


def main(argv):
    repo = DEFAULT_REPO
    save0 = DEFAULT_SAVE0
    mode = "watch"
    names = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--repo":
            i += 1
            repo = argv[i]
        elif a == "--save0":
            i += 1
            save0 = argv[i]
        elif a == "--once":
            mode = "once"
        elif a == "--add":
            mode = "add"
        elif mode == "add":
            names.append(a)
        else:
            log("unknown argument: " + a)
            return 2
        i += 1
    if not os.path.isdir(save0):
        log("Save0 not found: " + save0)
        return 1
    if mode == "add":
        if len(names) == 0:
            log("--add needs at least one file name")
            return 2
        return add_files(repo, save0, names)
    if mode == "once":
        return sync_once(repo, save0)
    watch(repo, save0)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
