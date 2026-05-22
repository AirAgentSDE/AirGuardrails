import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="NeMo Guardrails Server")
    parser.add_argument("--dev", action="store_true", help="Auto-reload configs")
    parser.add_argument("--port", type=int, default=8080, help="Listen port (default: 8080)")
    args = parser.parse_args()

    if not (1 <= args.port <= 65535):
        parser.error(f"Invalid port: {args.port} (must be 1-65535)")

    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configs")
    if not os.path.isdir(config_path):
        print(f"Config directory not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    from dotenv import load_dotenv
    load_dotenv()

    from nemoguardrails.server import api

    api.app.rails_config_path = config_path
    api.app.disable_chat_ui = True

    if args.dev:
        import logging
        logging.getLogger().setLevel(logging.INFO)
        api.app.auto_reload = True

    import uvicorn
    print(f"Starting NeMo Guardrails server on port {args.port}...")
    print(f"Config path: {config_path}")
    uvicorn.run(api.app, port=args.port, log_level="info", host="0.0.0.0")


if __name__ == "__main__":
    main()
