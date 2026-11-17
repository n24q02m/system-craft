#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify System Craft executable labs under labs/ cleanly across Windows and Linux."""
import argparse
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABS = os.path.join(ROOT, "labs")


def _run_py(name, args=None, use_temp_cwd=False):
    path = os.path.join(LABS, name)
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    if use_temp_cwd:
        with tempfile.TemporaryDirectory() as td:
            r = subprocess.run(
                [sys.executable, path, *(args or [])],
                cwd=td,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=90,
            )
    else:
        r = subprocess.run(
            [sys.executable, path, *(args or [])],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=90,
        )
    if r.returncode != 0:
        raise RuntimeError(f"{name} failed (exit {r.returncode}):\n{r.stdout}\n{r.stderr}")
    return r.stdout


def _check_c_labs(full=False):
    gcc = shutil.which("gcc")
    if not gcc or sys.platform == "win32":
        return "skipped (POSIX gcc optional on Windows; tested in Linux devcontainer/CI)"
    with tempfile.TemporaryDirectory() as td:
        for src in ("prog.c", "prog2.c", "prog3.c", os.path.join("d1", "prog3.c"), os.path.join("d2", "prog3.c")):
            out_bin = os.path.join(td, src.replace(os.sep, "_") + ".out")
            env = dict(os.environ, SOURCE_DATE_EPOCH="1700000000")
            subprocess.run(
                [gcc, os.path.join(LABS, src), "-O2", f"-ffile-prefix-map={LABS}=.", "-o", out_bin],
                check=True,
                env=env,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if full:
                subprocess.run([out_bin], check=True, capture_output=True, text=True, encoding="utf-8", errors="replace")
        for src in ("fs.c", "fs2.c"):
            out_bin = os.path.join(td, src + ".out")
            subprocess.run(
                [gcc, "-O2", "-pthread", os.path.join(LABS, src), "-o", out_bin],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
    return "compiled 7 C labs cleanly with gcc"


def verify(full=False):
    results = []

    # 1. Mathematical & cross-runtime Python labs (fast, cross-platform)
    out_cost = _run_py("cost.py")
    assert "KV cache / token (fp16)" in out_cost and "H100-SXM" in out_cost
    results.append("cost.py: PASS")

    out_sz1 = _run_py("size.py")
    assert "L = λW" in out_sz1
    results.append("size.py: PASS")

    out_sz2 = _run_py("size2.py")
    assert "Little: L = λW" in out_sz2
    results.append("size2.py: PASS")

    if shutil.which("node"):
        out_svc1 = _run_py("svc.py", use_temp_cwd=True)
        assert "khong co" in out_svc1, f"Unexpected roundtrip diff in svc.py:\n{out_svc1}"
        out_svc2 = _run_py("svc2.py", use_temp_cwd=True)
        assert "id_don (int64 > 2^53)" in out_svc2
        results.append("svc.py & svc2.py (Node roundtrip): PASS")
    else:
        for fn in ("svc.py", "svc2.py"):
            py_compile.compile(os.path.join(LABS, fn), doraise=True)
        results.append("svc.py & svc2.py: syntax PASS (node not on PATH)")

    # 2. Timing loop labs
    if full:
        out_j1 = _run_py("jitter.py")
        assert "deadline sched:" in out_j1
        out_j2 = _run_py("jitter2.py")
        assert "4 CPU hog" in out_j2
        results.append("jitter.py & jitter2.py (live timing): PASS")
    else:
        for fn in ("jitter.py", "jitter2.py"):
            py_compile.compile(os.path.join(LABS, fn), doraise=True)
        results.append("jitter.py & jitter2.py: compile check PASS (--fast)")

    # 3. C labs (gcc + pthreads on POSIX)
    c_status = _check_c_labs(full=full)
    results.append(f"C labs: {c_status}")
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fast", action="store_true", help="Run fast cross-platform labs & compile checks")
    ap.add_argument("--full", action="store_true", help="Include multi-second timing loops & C binaries")
    args = ap.parse_args()
    res = verify(full=args.full and not args.fast)
    for line in res:
        print(" -", line)
    print("LABS VERIFY: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
