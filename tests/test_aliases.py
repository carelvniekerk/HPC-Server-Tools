"""Regression tests for shell allocation helpers."""

import os
import subprocess
import unittest
from pathlib import Path


class InteractiveAllocationAliasTests(unittest.TestCase):
    """Verify the exact resource shape passed to Slurm."""

    def test_qi_gpu_scales_memory_with_gpu_count(self) -> None:
        """Keep 52 GiB of host RAM per requested A100."""
        repository = Path(__file__).resolve().parents[1]
        environment = {
            **os.environ,
            "HPC_TOOLS_PATH": "/tmp/hpc_server_tools",
            "HPC_USER_ROOT": "/tmp",
            "USER_NAME": "test-user",
        }
        shell = r"""
srun() {
    printf '%s\n' "$@"
}
source scripts/aliases
qi-gpu "$1"
"""

        for gpu_count, memory_gib in ((1, 52), (2, 104), (4, 208)):
            with self.subTest(gpu_count=gpu_count):
                result = subprocess.run(
                    ["bash", "-c", shell, "qi-gpu-test", str(gpu_count)],
                    cwd=repository,
                    env=environment,
                    check=True,
                    capture_output=True,
                    text=True,
                )

                arguments = result.stdout.splitlines()
                self.assertIn(f"--mem={memory_gib}G", arguments)
                self.assertIn(f"--gres=gpu:a100:{gpu_count}", arguments)
                self.assertIn("--nodes=1", arguments)


if __name__ == "__main__":
    unittest.main()
