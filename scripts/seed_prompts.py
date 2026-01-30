import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from apps.orchestrator.core.prompt_registry import PromptRegistry


def main():
    registry = PromptRegistry()
    prompts = registry.list()
    print(f"Seeded prompts: {len(prompts)}")
    for p in prompts:
        print(f"- {p.type}:{p.version}")


if __name__ == "__main__":
    main()
