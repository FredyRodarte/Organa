import subprocess

def run():
    print("Running RBAC tests...")
    result = subprocess.run(
        ['.venv/Scripts/python.exe', 'manage.py', 'test', 'apps.authentication.tests_rbac'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
    print(f"Finished. Exit code: {result.returncode}")

if __name__ == '__main__':
    run()
