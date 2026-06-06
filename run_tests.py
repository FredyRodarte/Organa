import subprocess

def run():
    print("Running tests...")
    result = subprocess.run(
        ['.venv/Scripts/python.exe', 'manage.py', 'test', 'apps.tasks'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    with open('test_output.txt', 'w', encoding='utf-8') as f:
        f.write("STDOUT:\n")
        f.write(result.stdout)
        f.write("\nSTDERR:\n")
        f.write(result.stderr)
        f.write(f"\nExit code: {result.returncode}\n")
    print(f"Finished. Exit code: {result.returncode}")

if __name__ == '__main__':
    run()
