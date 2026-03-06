import sys
import os
import subprocess

def run_command(command):
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        return e

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    vmo_file = os.path.join(base_dir, "todo_plugin.vmo")
    vim_file = os.path.join(base_dir, "todo_plugin.vim")
    vimmo_script = os.path.join(base_dir, "..", "vimmo.py")

    print(f"Compiling {vmo_file} ... ", end="", flush=True)
    
    # 1. Compile
    compile_cmd = [sys.executable, vimmo_script, "compile", vmo_file, "-o", vim_file]
    res = run_command(compile_cmd)
    
    if res.returncode != 0:
        print("FAIL")
        print(res.stderr)
        sys.exit(1)
    
    print("OK")

    # 2. Verify with Vim
    print(f"Verifying {vim_file} with Vim ... ", end="", flush=True)
    
    # We load the script and call a few functions to ensure runtime correctness
    # We use -V1 for verbose output to catch hidden errors
    vim_cmd = [
        "vim", "-es", "-V1",
        "-c", f"try | source {vim_file} | catch | echo v:exception | cquit 1 | endtry",
        "-c", "q"
    ]
    
    res = run_command(vim_cmd)
    
    if res.returncode != 0:
        print("FAIL")
        print(f"Exit Code: {res.returncode}")
        print(f"Stdout: {res.stdout.strip()}")
        print(f"Stderr: {res.stderr.strip()}")
        sys.exit(1)
    
    print("OK")
    print("\n--- Output Preview ---")
    print(res.stderr) # vim -es writes output to stderr usually, or stdout depending on version

if __name__ == "__main__":
    main()
