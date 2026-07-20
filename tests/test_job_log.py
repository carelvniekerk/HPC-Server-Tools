"""Tests for Slurm job-log path discovery."""

import os
import subprocess
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

os.environ.setdefault("USER_NAME", "test-user")

from hpc_server_tools.job_submission.job_log import (  # noqa: E402
    get_job_log_path,
    get_job_log_path_or_exit,
    get_jobs,
    get_jobs_or_exit,
    parse_scontrol_metadata,
    SQUEUE_FIELD_SEPARATOR,
)


class GetJobsTest(unittest.TestCase):
    """Test the stable ``squeue`` format with a wider fixed-width job name."""

    @patch("hpc_server_tools.job_submission.job_log.subprocess.run")
    def test_preserves_long_job_names(self, run_mock) -> None:
        run_mock.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=(
                f"33641305_200{SQUEUE_FIELD_SEPARATOR}deepmath-4b-s66750-68750-chunk256"
                f"{SQUEUE_FIELD_SEPARATOR}trust03{SQUEUE_FIELD_SEPARATOR}R\n"
                f"33636517{SQUEUE_FIELD_SEPARATOR}DevSession{SQUEUE_FIELD_SEPARATOR}trust03"
                f"{SQUEUE_FIELD_SEPARATOR}R\n"
            ),
        )

        jobs = get_jobs("trust03")

        self.assertEqual(jobs[0]["name"], "deepmath-4b-s66750-68750-chunk256")
        self.assertEqual(jobs[1]["name"], "DevSession")
        run_mock.assert_called_once_with(
            [
                "squeue",
                "--user",
                "trust03",
                "--noheader",
                f"--format=%i{SQUEUE_FIELD_SEPARATOR}%.40j{SQUEUE_FIELD_SEPARATOR}%u{SQUEUE_FIELD_SEPARATOR}%t",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    @patch("hpc_server_tools.job_submission.job_log.subprocess.run")
    def test_preserves_pipe_characters_in_job_names(self, run_mock) -> None:
        """Do not treat printable job-name characters as field delimiters."""
        run_mock.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=(
                f"42{SQUEUE_FIELD_SEPARATOR}train|debug{SQUEUE_FIELD_SEPARATOR}trust03"
                f"{SQUEUE_FIELD_SEPARATOR}R\n"
            ),
        )

        jobs = get_jobs("trust03")

        self.assertEqual(jobs[0]["name"], "train|debug")

    @patch("hpc_server_tools.job_submission.job_log.get_jobs")
    def test_cli_reports_squeue_failure_without_traceback(self, get_jobs_mock) -> None:
        """Turn scheduler query failures into an actionable CLI message."""
        get_jobs_mock.side_effect = subprocess.CalledProcessError(1, ["squeue"])
        output = StringIO()
        console = Console(file=output, color_system=None)

        with self.assertRaises(SystemExit) as exit_context:
            get_jobs_or_exit("trust03", console=console)

        self.assertEqual(exit_context.exception.code, 1)
        self.assertIn(
            "Could not query active Slurm jobs for trust03", output.getvalue()
        )
        self.assertIn("squeue command may be unavailable", output.getvalue())


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

    @patch("hpc_server_tools.job_submission.job_log.subprocess.run")
    def test_resolves_relative_paths_against_slurm_work_dir(self, run_mock) -> None:
        run_mock.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=(
                "JobId=45 WorkDir=/scratch/project "
                "StdOut=logs/slurm-45.out StdErr=slurm-45.err"
            ),
        )

        self.assertEqual(
            get_job_log_path("45", output=True),
            Path("/scratch/project/logs/slurm-45.out"),
        )
        self.assertEqual(
            get_job_log_path("45", output=False),
            Path("/scratch/project/slurm-45.err"),
        )

    @patch("hpc_server_tools.job_submission.job_log.subprocess.run")
    def test_preserves_whitespace_in_work_dir_and_log_paths(self, run_mock) -> None:
        """Resolve field boundaries without splitting path values on spaces."""
        run_mock.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=(
                "JobId=47 WorkDir=/scratch/project with spaces "
                "StdOut=logs/training output.log StdErr=logs/training errors.log NumNodes=1"
            ),
        )

        self.assertEqual(
            get_job_log_path("47", output=True),
            Path("/scratch/project with spaces/logs/training output.log"),
        )
        self.assertEqual(
            get_job_log_path("47", output=False),
            Path("/scratch/project with spaces/logs/training errors.log"),
        )

    def test_metadata_parser_preserves_equals_signs_inside_values(self) -> None:
        """Only field markers preceded by whitespace delimit metadata values."""
        metadata = parse_scontrol_metadata(
            "JobId=48 WorkDir=/scratch/key=value StdOut=job output.log NumNodes=1"
        )

        self.assertEqual(metadata["WorkDir"], "/scratch/key=value")
        self.assertEqual(metadata["StdOut"], "job output.log")

    @patch("hpc_server_tools.job_submission.job_log.subprocess.run")
    def test_treats_dev_null_as_no_registered_log(self, run_mock) -> None:
        run_mock.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="JobId=46 WorkDir=/scratch/project StdOut=/dev/null StdErr=/dev/null",
        )

        self.assertIsNone(get_job_log_path("46", output=True))
        self.assertIsNone(get_job_log_path("46", output=False))

    @patch("hpc_server_tools.job_submission.job_log.get_job_log_path")
    def test_cli_reports_transient_scontrol_failure_without_traceback(
        self, get_path_mock
    ) -> None:
        get_path_mock.side_effect = subprocess.CalledProcessError(1, ["scontrol"])
        output = StringIO()
        console = Console(file=output, color_system=None)

        with self.assertRaises(SystemExit) as exit_context:
            get_job_log_path_or_exit("44", output=True, console=console)

        self.assertEqual(exit_context.exception.code, 1)
        self.assertIn(
            "Could not query Slurm log metadata for job 44", output.getvalue()
        )
        self.assertIn("job may have finished", output.getvalue())


if __name__ == "__main__":
    unittest.main()
