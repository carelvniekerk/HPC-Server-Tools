"""Regression tests for the Noctua2 resource display."""

import os
import subprocess
import unittest
from unittest.mock import patch

os.environ.setdefault("USER_NAME", "test-user")

from hpc_server_tools.resource_stats.resource_check import (  # noqa: E402
    format_gpu_request,
    get_empty_jobs_row,
    get_node_status,
    get_schedulable_memory_gib,
    is_node_schedulable,
    parse_squeue_job_fields,
    SQUEUE_FIELD_SEPARATOR,
)


class ResourceCheckTests(unittest.TestCase):
    """Cover scheduler states and table placeholders."""

    def test_empty_current_user_row_places_message_in_name_column(self) -> None:
        """Keep the placeholder out of the partition column."""
        row = get_empty_jobs_row(project_jobs=False)

        self.assertEqual(row[1], "-")
        self.assertEqual(row[2], "No active jobs")

    def test_empty_project_row_places_message_in_name_column(self) -> None:
        """Account for the additional user column in project mode."""
        row = get_empty_jobs_row(project_jobs=True)

        self.assertEqual(row[2], "-")
        self.assertEqual(row[3], "No active jobs")

    def test_not_responding_node_is_not_schedulable(self) -> None:
        """Match the complete state flag emitted by Slurm."""
        self.assertFalse(is_node_schedulable({"state": "IDLE+NOT_RESPONDING"}))

    def test_scheduler_memory_headroom_uses_real_minus_allocated_memory(self) -> None:
        """Report what Slurm can admit rather than momentary Linux FreeMem."""
        status = {
            "state": "MIXED",
            "resources_available.mem": "485000mb",
            "resources_assigned.mem": "53248mb",
        }

        self.assertEqual(get_schedulable_memory_gib(status), 421)

    def test_unavailable_node_has_no_schedulable_memory_headroom(self) -> None:
        """Fail closed for RAM as well as CPUs and GPUs."""
        status = {
            "state": "IDLE+DRAIN",
            "resources_available.mem": "485000mb",
            "resources_assigned.mem": "0mb",
        }

        self.assertEqual(get_schedulable_memory_gib(status), 0)

    def test_only_plain_idle_and_mixed_states_are_schedulable(self) -> None:
        """Fail closed for unavailable base states and compound flags."""
        self.assertTrue(is_node_schedulable({"state": "IDLE"}))
        self.assertTrue(is_node_schedulable({"state": "MIXED"}))
        self.assertFalse(is_node_schedulable({"state": "FUTURE"}))
        self.assertFalse(is_node_schedulable({"state": "IDLE+INVALID_REG"}))

    def test_formats_squeue_gres_gpu_requests(self) -> None:
        """Parse the GRES syntax emitted by the squeue percent-b field."""
        self.assertEqual(format_gpu_request("gpu:4"), "4")
        self.assertEqual(format_gpu_request("gpu:a100:4"), "4 a100")

    def test_formats_tres_gpu_requests(self) -> None:
        """Also accept colon and equals forms used by Slurm TRES fields."""
        self.assertEqual(format_gpu_request("gres/gpu:4"), "4")
        self.assertEqual(format_gpu_request("gres/gpu=4"), "4")
        self.assertEqual(format_gpu_request("gres/gpu:a100:4"), "4 a100")
        self.assertEqual(format_gpu_request("gres/gpu:a100=4"), "4 a100")

    def test_formats_multiple_gpu_resource_types(self) -> None:
        """Retain each typed GPU request in mixed resource lists."""
        self.assertEqual(
            format_gpu_request("gpu:a100:2,gpu:h100:1"),
            "2 a100, 1 h100",
        )

    def test_preserves_pipe_characters_in_job_names(self) -> None:
        """Do not shift scheduler fields when a printable pipe occurs in a name."""
        separator = SQUEUE_FIELD_SEPARATOR
        fields = parse_squeue_job_fields(
            separator.join(
                (
                    "42",
                    "trust03",
                    "gpu",
                    "train|seed1",
                    "R",
                    "1:00",
                    "2-00:00:00",
                    "1",
                    "2",
                    "52G",
                    "gpu:a100:4",
                    "n2gpu1208",
                )
            )
        )

        self.assertEqual(fields[3], "train|seed1")
        self.assertEqual(fields[4], "R")
        self.assertEqual(fields[5], "1:00")
        self.assertEqual(fields[6], "2-00:00:00")
        self.assertEqual(fields[9], "52G")
        self.assertEqual(fields[10], "gpu:a100:4")

    @patch("hpc_server_tools.resource_stats.resource_check.subprocess.run")
    def test_missing_node_state_falls_back_to_unschedulable_unknown(
        self, run_mock
    ) -> None:
        """Do not crash or count capacity when scontrol omits State."""
        run_mock.return_value = subprocess.CompletedProcess(
            args=["scontrol", "show", "node", "n2gpu1201"],
            returncode=0,
            stdout=(
                b"NodeName=n2gpu1201\n"
                b"   RealMemory=485000 AllocMem=0 FreeMem=480000\n"
                b"   CfgTRES=cpu=128,mem=485000M,billing=128,gres/gpu=4,gres/gpu:a100=4\n"
                b"   AllocTRES=\n"
            ),
        )

        status = get_node_status("n2gpu1201")

        self.assertEqual(status["state"], "UNKNOWN")
        self.assertEqual(status["resources_available.mem"], "485000mb")
        self.assertEqual(status["resources_assigned.mem"], "0mb")
        self.assertFalse(is_node_schedulable(status))

    @patch("hpc_server_tools.resource_stats.resource_check.subprocess.run")
    def test_truncated_node_status_returns_empty_record(self, run_mock) -> None:
        """Fail closed when a required scontrol field is unavailable."""
        run_mock.return_value = subprocess.CompletedProcess(
            args=["scontrol", "show", "node", "n2gpu1201"],
            returncode=0,
            stdout=b"NodeName=n2gpu1201 State=IDLE\n",
        )

        self.assertEqual(get_node_status("n2gpu1201"), {})


if __name__ == "__main__":
    unittest.main()
