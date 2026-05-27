import argparse
import os


def get_configs_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs")


def main():
    parser = argparse.ArgumentParser(description="NeMo Guardrails Server")
    parser.add_argument("--dev", action="store_true", help="Auto-reload configs")
    parser.add_argument("--port", type=int, default=8080, help="Listen port (default: 8080)")
    args = parser.parse_args()

    from dotenv import load_dotenv
    load_dotenv()

    config_path = get_configs_path()

    from nemoguardrails.server import api

    api.app.rails_config_path = os.path.expanduser(config_path.rstrip(os.path.sep))
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
