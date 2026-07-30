import subprocess
import sys
import os

def main():
    # Pass through all stdio to npx
    proc = subprocess.Popen(
        ["C:\\nvm4w\\nodejs\\npx.cmd", "-y", "@modelcontextprotocol/server-github"],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
        env=os.environ.copy()
    )
    proc.wait()

if __name__ == "__main__":
    main()
