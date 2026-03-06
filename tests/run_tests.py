import sys
import os
import subprocess
import glob


def run_command(command, cwd=None):
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
        )
        return result
    except Exception as e:
        print(f"Error running command {command}: {e}")
        return None


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Adjust paths for monorepo
    core_dir = os.path.join(base_dir, "..", "packages", "vimmo-core")
    vimmo_script = os.path.join(core_dir, "src", "vimmo", "vimmo.py")
    cases_dir = os.path.join(core_dir, "tests", "cases")

    vmo_files = sorted(glob.glob(os.path.join(cases_dir, "*.vmo")))

    if not vmo_files:
        print(f"No .vmo files found in {cases_dir}")
        sys.exit(1)

    print(f"Found {len(vmo_files)} test cases.")

    failed_tests = []

    # Update PYTHONPATH so 'import vimmo' works
    env = os.environ.copy()
    env["PYTHONPATH"] = (
        os.path.join(core_dir, "src") + os.pathsep + env.get("PYTHONPATH", "")
    )

    for vmo_file in vmo_files:
        base_name = os.path.basename(vmo_file)
        vim_file = vmo_file.replace(".vmo", ".vim")

        print(f"Running test: {base_name} ... ", end="", flush=True)

        # 1. Compile
        compile_cmd = [
            sys.executable,
            vimmo_script,
            "compile",
            vmo_file,
            "-o",
            vim_file,
        ]
        compile_result = subprocess.run(
            compile_cmd, env=env, capture_output=True, text=True
        )

        if compile_result.returncode != 0:
            print("FAIL (Compilation Error)")
            print(compile_result.stderr)
            failed_tests.append(base_name)
            continue

        # 2. Run with Vim
        vim_cmd = [
            "vim",
            "-es",
            "-V1",
            "-c",
            f"try | source {vim_file} | catch | echo v:exception | cquit 1 | endtry",
            "-c",
            "q",
        ]

        vim_result = run_command(vim_cmd, cwd=cases_dir)

        if vim_result and vim_result.returncode != 0:
            print("FAIL (Vim Runtime Error)")
            print(f"  Exit Code: {vim_result.returncode}")
            print(f"  Stderr: {vim_result.stderr.strip()}")
            failed_tests.append(base_name)
        else:
            print("PASS")

    print("-" * 40)
    if failed_tests:
        print(f"❌ {len(failed_tests)} tests failed.")
        sys.exit(1)
    else:
        print("✅ All tests passed.")


if __name__ == "__main__":
    main()
