"""Tests for Slurm job-log path discovery."""

import os
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("USER_NAME", "test-user")

from hpc_server_tools.job_submission.job_log import get_job_log_path  # noqa: E402


class GetJobLogPathTest(unittest.TestCase):
    """Test parsing of the paths reported by ``scontrol show job``."""

    @patch("hpc_server_tools.job_submission.job_log.subprocess.run")
    def test_resolves_stdout_and_stderr_paths(self, run_mock) -> None:
        run_mock.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="JobId=42 StdOut=/scratch/logs/job_42.out StdErr=/scratch/logs/job_42.err",
        )

        self.assertEqual(
            get_job_log_path("42", output=True), Path("/scratch/logs/job_42.out")
        )
        self.assertEqual(
            get_job_log_path("42", output=False), Path("/scratch/logs/job_42.err")
        )

    @patch("hpc_server_tools.job_submission.job_log.subprocess.run")
    def test_returns_none_when_interactive_job_has_no_registered_log(
        self, run_mock
    ) -> None:
        run_mock.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="JobId=43 JobName=DevSession BatchFlag=0 Command=bash",
        )

        self.assertIsNone(get_job_log_path("43", output=True))
        self.assertIsNone(get_job_log_path("43", output=False))


if __name__ == "__main__":
    unittest.main()
