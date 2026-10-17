"""Policy-as-code: every authorization decision is evaluated by OPA against policy/."""

import json
import shutil
import subprocess

from . import POLICY_DIR


class PolicyError(RuntimeError):
    pass


class OPA:
    def __init__(self, policy_dir=POLICY_DIR, binary: str | None = None):
        self.policy_dir = str(policy_dir)
        self.binary = binary or shutil.which("opa")
        if not self.binary:
            raise PolicyError(
                "OPA binary not found. Install then retry:\n"
                "  macOS:  brew install opa\n"
                "  Linux:  curl -L -o opa "
                "https://openpolicyagent.org/downloads/latest/opa_linux_amd64_static "
                "&& chmod +x opa && sudo mv opa /usr/local/bin/opa\n"
                "  Docs:   https://www.openpolicyagent.org/docs/latest/#running-opa"
            )

    def decide(self, package: str, input_doc: dict) -> dict:
        proc = subprocess.run(
            [self.binary, "eval", "--format", "json", "--data", self.policy_dir,
             "--stdin-input", f"data.agentthree.{package}.decision"],
            input=json.dumps(input_doc), capture_output=True, text=True, timeout=30,
        )
        if proc.returncode != 0:
            raise PolicyError(proc.stderr.strip())
        result = json.loads(proc.stdout).get("result")
        if not result:
            # Fail closed: an undefined decision is a deny.
            return {"allow": False, "reasons": ["policy returned no decision"]}
        return result[0]["expressions"][0]["value"]
