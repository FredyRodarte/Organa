import subprocess

def main():
    print("Running tasks tests inside python script...")
    result = subprocess.run(
        [r'C:\Users\PC\.gemini\antigravity\scratch\organa\.venv\Scripts\python.exe', 'manage.py', 'test', 'apps.tasks'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    log_path = r'C:\Users\PC\.gemini\antigravity\scratch\organa\test_run_log.txt'
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write("--- STDOUT ---\n")
        f.write(result.stdout or '')
        f.write("\n--- STDERR ---\n")
        f.write(result.stderr or '')
        f.write(f"\n--- Exit code ---\n")
        f.write(str(result.returncode))
    
    print(f"Log written to {log_path}. Exit code: {result.returncode}")

if __name__ == '__main__':
    main()
