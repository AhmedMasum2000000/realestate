"""Shared test doubles."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rep.ssh import Result, SshRunner  # noqa: E402


class RecordingRunner(SshRunner):
    """An SshRunner that records commands instead of connecting anywhere."""

    def __init__(self, **kwargs):
        super().__init__(host="192.0.2.1", user="u", dry_run=True, **kwargs)
        self.commands: list[str] = []

    def run(self, command: str, *, cwd: str = "") -> Result:
        full = f"cd {cwd} && {command}" if cwd else command
        self.commands.append(full)
        return Result(command=full, exit_code=0, stdout="", stderr="")
