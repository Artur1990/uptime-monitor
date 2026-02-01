import argparse
from app.config import Target
from app.storage import load_from_yaml, save_to_yaml


def add_target(name: str, url: str) -> None:
    settings = load_from_yaml()

    for t in settings.targets:
        if t.name == name or t.url == url:
            print("Target already exists")
            return

    settings.targets.append(Target(name=name, url=url))
    save_to_yaml(settings)
    print(f"Added target: {name} -> {url}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Uptime Monitor management CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Add new target")
    add.add_argument("--name", required=True)
    add.add_argument("--url", required=True)

    args = parser.parse_args()

    if args.command == "add":
        add_target(args.name, args.url)


if __name__ == "__main__":
    main()
