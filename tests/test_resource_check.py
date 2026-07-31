"""Regression tests for the Noctua2 resource display."""

import os
import subprocess
import unittest
from io import StringIO
from unittest.mock import patch

from rich.console import Console

original_user_name = os.environ.get("USER_NAME")
os.environ["USER_NAME"] = "test-user"

from hpc_server_tools.resource_stats.resource_check import (  # noqa: E402
    SACCT_FIELD_SEPARATOR,
    SACCT_FIELDS,
    SQUEUE_FIELD_SEPARATOR,
    display_gpu_node_summary,
    display_jobs,
    display_recent_jobs,
    format_allocated_memory,
    format_day_count,
    format_gpu_request,
    get_empty_jobs_row,
    get_node_status,
    get_schedulable_memory_gib,
    is_node_schedulable,
    parse_private_data_categories,
    parse_sacct_job_fields,
    parse_squeue_job_fields,
)

if original_user_name is None:
    del os.environ["USER_NAME"]
else:
    os.environ["USER_NAME"] = original_user_name


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

    @patch("hpc_server_tools.resource_stats.resource_check.subprocess.run")
    def test_malformed_squeue_output_still_displays_empty_placeholder(
        self, run_mock
    ) -> None:
        """Base the placeholder on parsed rows rather than raw output."""
        run_mock.return_value = subprocess.CompletedProcess(
            args=["squeue"],
            returncode=0,
            stdout="malformed scheduler output\n",
        )
        output = StringIO()
        test_console = Console(
            file=output,
            color_system=None,
            force_terminal=False,
            width=180,
        )

        with patch(
            "hpc_server_tools.resource_stats.resource_check.console", test_console
        ):
            display_jobs(user_name="test-user")

        self.assertIn("No active jobs", output.getvalue())

    @patch("hpc_server_tools.resource_stats.resource_check.subprocess.run")
    def test_scheduler_brackets_render_as_literal_text(self, run_mock) -> None:
        """Do not interpret job names or node lists as Rich markup."""
        separator = SQUEUE_FIELD_SEPARATOR
        run_mock.return_value = subprocess.CompletedProcess(
            args=["squeue"],
            returncode=0,
            stdout=separator.join(
                (
                    "42",
                    "test-user",
                    "gpu",
                    "train[seed1]",
                    "R",
                    "1:00",
                    "2-00:00:00",
                    "2",
                    "32",
                    "208G",
                    "gpu:a100:8",
                    "n2gpu[1201-1202]",
                )
            ),
        )
        output = StringIO()
        test_console = Console(
            file=output,
            color_system=None,
            force_terminal=False,
            width=220,
        )

        with patch(
            "hpc_server_tools.resource_stats.resource_check.console", test_console
        ):
            display_jobs(user_name="test-user")

        rendered = output.getvalue()
        self.assertIn("train[seed1]", rendered)
        self.assertIn("n2gpu[1201-1202]", rendered)

    def test_compressed_hostlist_renders_without_rich_markup_error(self) -> None:
        """Treat Slurm-style brackets as literal text in placement tables."""
        statuses = [
            {
                "node_name": node_name,
                "state": "IDLE",
                "resources_available.ngpus": "4",
                "resources_assigned.ngpus": "0",
                "resources_available.mem": "485000mb",
                "resources_assigned.mem": "0mb",
            }
            for node_name in ("n2gpu1201", "n2gpu1202")
        ]
        output = StringIO()
        test_console = Console(
            file=output,
            color_system=None,
            force_terminal=False,
            width=180,
        )

        with patch(
            "hpc_server_tools.resource_stats.resource_check.console", test_console
        ):
            display_gpu_node_summary("A100", statuses)

        self.assertIn("n2gpu[1201-1202]", output.getvalue())

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

    def test_prefers_typed_gpu_tres_over_duplicate_generic_total(self) -> None:
        """Do not display AllocTRES generic and typed GPU counts twice."""
        self.assertEqual(
            format_gpu_request(
                "cpu=16,mem=208G,node=1,billing=54,gres/gpu=4,gres/gpu:a100=4"
            ),
            "4 a100",
        )

    def test_formats_allocated_memory_from_tres(self) -> None:
        """Expose the allocation's total memory rather than sampled usage."""
        self.assertEqual(
            format_allocated_memory("cpu=16,mem=208G,gres/gpu:a100=4"),
            "208G",
        )
        self.assertEqual(format_allocated_memory("cpu=16"), "-")

    def test_formats_singular_and_plural_day_counts(self) -> None:
        """Keep recent-allocation titles grammatical."""
        self.assertEqual(format_day_count(1), "1 day")
        self.assertEqual(format_day_count(7), "7 days")

    def test_parses_private_data_categories(self) -> None:
        """Recognize the live Slurm privacy setting despite aligned whitespace."""
        config = (
            "AccountingStorageType   = accounting_storage/slurmdbd\n"
            "PrivateData             = accounts,jobs,reservations,usage,users\n"
        )

        self.assertEqual(
            parse_private_data_categories(config),
            frozenset({"accounts", "jobs", "reservations", "usage", "users"}),
        )

    def test_parses_none_private_data_as_empty(self) -> None:
        """Treat an explicitly public scheduler configuration as unrestricted."""
        self.assertEqual(
            parse_private_data_categories("PrivateData = none\n"),
            frozenset(),
        )

    def test_preserves_pipe_characters_in_sacct_job_names(self) -> None:
        """Use a non-printable delimiter for historical allocation records."""
        values = list(SACCT_FIELDS)
        values[2] = "train|seed1"

        fields = parse_sacct_job_fields(SACCT_FIELD_SEPARATOR.join(values))

        self.assertEqual(fields[2], "train|seed1")
        self.assertEqual(fields[3], "State")

    @patch("hpc_server_tools.resource_stats.resource_check.subprocess.run")
    def test_displays_ended_allocation_hardware_and_omits_running_jobs(
        self, run_mock
    ) -> None:
        """Render exact allocation hardware and omit unfinished records."""
        separator = SACCT_FIELD_SEPARATOR
        ended_job = separator.join(
            (
                "33848217",
                "gpu",
                "grpo-4b-gen16-acc50",
                "FAILED",
                "2026-07-31T14:58:39",
                "03:43:05",
                "08:00:00",
                "1",
                "16",
                "billing=54,cpu=16,gres/gpu:a100=4,gres/gpu=4,mem=208G,node=1",
                "n2gpu1220",
                "1:0",
            )
        )
        running_job = separator.join(
            (
                "33852639",
                "gpu",
                "grpo-4b-gen16-accuracy-fixed",
                "RUNNING",
                "Unknown",
                "02:00:00",
                "5-00:00:00",
                "1",
                "16",
                "billing=54,cpu=16,gres/gpu:a100=4,gres/gpu=4,mem=208G,node=1",
                "n2gpu1229",
                "0:0",
            )
        )
        run_mock.return_value = subprocess.CompletedProcess(
            args=["sacct"],
            returncode=0,
            stdout=f"{ended_job}\n{running_job}\n",
        )
        output = StringIO()
        test_console = Console(
            file=output,
            color_system=None,
            force_terminal=False,
            width=240,
        )

        with patch(
            "hpc_server_tools.resource_stats.resource_check.console", test_console
        ):
            display_recent_jobs(user_name="trust03", recent_days=1)

        rendered = output.getvalue()
        self.assertIn("past 1 day", rendered)
        self.assertIn("33848217", rendered)
        self.assertIn("208G", rendered)
        self.assertIn("4 a100", rendered)
        self.assertIn("n2gpu1220", rendered)
        self.assertNotIn("33852639", rendered)
        command = run_mock.call_args.args[0]
        self.assertIn("--allocations", command)
        self.assertIn("now-1days", command)

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
