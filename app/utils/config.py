import yaml
from pathlib import Path


def load_config(env: str = "dev") -> dict:
    base_path = Path(__file__).resolve().parents[2] / "config"

    with open(base_path / "base.yaml") as f:
        base = yaml.safe_load(f)

    with open(base_path / f"{env}.yaml") as f:
        env_cfg = yaml.safe_load(f)

    return {**base, **env_cfg}
