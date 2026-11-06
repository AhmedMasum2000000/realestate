"""SSH transport for running commands on the cPanel server.

Prefers paramiko (portable, clear errors); falls back to the system `ssh`
binary when paramiko is not installed. Both paths return the same Result, so
callers never branch on which one is in use.
"""

from __future__ import annotations

import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

try:  # pragma: no cover - import-time branch
    import paramiko

    HAVE_PARAMIKO = True
except ImportError:  # pragma: no cover
    paramiko = None  # type: ignore[assignment]
    HAVE_PARAMIKO = False


class SshError(Exception):
    """Could not connect, or the transport itself failed."""


@dataclass
class Result:
    command: str
    exit_code: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.exit_code == 0

    def check(self) -> "Result":
        if not self.ok:
            detail = (self.stderr or self.stdout).strip()
            raise SshError(f"exit {self.exit_code}: {self.command}\n{detail[:800]}")
        return self


@dataclass
class SshRunner:
    host: str
    user: str
    port: int = 22
    key_path: str = ""
    password: str = ""
    dry_run: bool = True
    timeout: int = 180

    _client: object | None = None

    # -- lifecycle ----------------------------------------------------------

    def connect(self) -> None:
        if self.dry_run or not HAVE_PARAMIKO or self._client is not None:
            return
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        kwargs: dict[str, object] = {
            "hostname": self.host,
            "port": self.port,
            "username": self.user,
            "timeout": 30,
        }
        if self.key_path:
            expanded = str(Path(self.key_path).expanduser())
            if not Path(expanded).exists():
                raise SshError(f"SSH_KEY_PATH points at {expanded}, which does not exist")
            kwargs["key_filename"] = expanded
        elif self.password:
            kwargs["password"] = self.password
        else:
            raise SshError("set either SSH_KEY_PATH or SSH_PASSWORD in config/.env")

        try:
            client.connect(**kwargs)  # type: ignore[arg-type]
        except Exception as exc:  # paramiko raises a wide family
            raise SshError(f"cannot SSH to {self.user}@{self.host}:{self.port} -- {exc}") from exc
        self._client = client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()  # type: ignore[attr-defined]
            self._client = None

    def __enter__(self) -> "SshRunner":
        self.connect()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    # -- execution ----------------------------------------------------------

    def run(self, command: str, *, cwd: str = "") -> Result:
        """Run `command` on the server. In dry-run, log it and return success."""
        full = f"cd {shlex.quote(cwd)} && {command}" if cwd else command

        if self.dry_run:
            return Result(command=full, exit_code=0, stdout="", stderr="")

        if HAVE_PARAMIKO:
            return self._run_paramiko(full)
        return self._run_binary(full)

    def _run_paramiko(self, command: str) -> Result:
        self.connect()
        assert self._client is not None
        _stdin, stdout, stderr = self._client.exec_command(  # type: ignore[attr-defined]
            command, timeout=self.timeout
        )
        out = stdout.read().decode("utf-8", "replace")
        err = stderr.read().decode("utf-8", "replace")
        code = stdout.channel.recv_exit_status()
        return Result(command=command, exit_code=code, stdout=out, stderr=err)

    def _run_binary(self, command: str) -> Result:
        argv = ["ssh", "-p", str(self.port), "-o", "BatchMode=yes"]
        if self.key_path:
            argv += ["-i", str(Path(self.key_path).expanduser())]
        argv += [f"{self.user}@{self.host}", command]
        try:
            proc = subprocess.run(
                argv, capture_output=True, text=True, timeout=self.timeout
            )
        except FileNotFoundError as exc:
            raise SshError(
                "neither paramiko nor an `ssh` binary is available. "
                "Run: pip install -r requirements.txt"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise SshError(f"command timed out after {self.timeout}s: {command}") from exc
        return Result(
            command=command,
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )

    # -- helpers ------------------------------------------------------------

    def exists(self, remote_path: str) -> bool:
        if self.dry_run:
            return False
        return self.run(f"test -e {shlex.quote(remote_path)}").ok

    def upload(self, local: Path, remote: str) -> None:
        if self.dry_run:
            return
        if HAVE_PARAMIKO:
            self.connect()
            assert self._client is not None
            sftp = self._client.open_sftp()  # type: ignore[attr-defined]
            try:
                sftp.put(str(local), remote)
            finally:
                sftp.close()
            return
        argv = ["scp", "-P", str(self.port)]
        if self.key_path:
            argv += ["-i", str(Path(self.key_path).expanduser())]
        argv += [str(local), f"{self.user}@{self.host}:{remote}"]
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=self.timeout)
        if proc.returncode != 0:
            raise SshError(f"scp failed: {proc.stderr.strip()[:400]}")
