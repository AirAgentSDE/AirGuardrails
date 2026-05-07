import argparse
import os
import subprocess
import sys
from dotenv import load_dotenv


load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="NeMo Guardrails Server")
    parser.add_argument(
        "--dev", action="store_true", help="Development mode (--verbose + --auto-reload)"
    )
    args = parser.parse_args()

    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs")
    cmd = [
        sys.executable, "-m", "nemoguardrails", "server",
        "--config", config_path,
        "--disable-chat-ui",
        "--port", "8080",
    ]
    if args.dev:
        cmd += ["--verbose", "--auto-reload"]

    print(f"Starting NeMo Guardrails server (dev={args.dev})...")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
