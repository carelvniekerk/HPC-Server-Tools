"""Resource overrides must depend on presence, not equality to defaults."""

import os
import sys
import unittest
from dataclasses import replace
from unittest.mock import patch

from hpc_server_tools.job_submission.vm_configuration import get_vm_config, parse_args
from hpc_server_tools.vm_templates import INTERACTIVE_DEFAULTS, JOB_DEFAULTS, TEMPLATES


class ResourceOverrideTests(unittest.TestCase):
    def test_generated_scheduler_preamble_uses_explicit_resources(self):
        # Import only the renderer; never invoke the scheduler or write a job.
        with patch.dict(os.environ, {"USER_NAME": "test-user"}):
            from hpc_server_tools.job_submission.submit_job import build_preamble
        cfg = self.resolve(
            "--template=CPU",
            "--ncpus=2",
            "--memory=16",
            "--ngpus=0",
            "--walltime=00:15:00",
        )
        with patch("subprocess.run") as run_mock:
            preamble = build_preamble(cfg, "issue-1-test")
        run_mock.assert_not_called()
        if "#PBS" in preamble:
            self.assertIn("#PBS -l select=1:ncpus=2:mem=16gb", preamble)
            self.assertIn("#PBS -l walltime=00:15:00", preamble)
            self.assertNotIn(":ngpus=", preamble)
        else:
            self.assertIn("#SBATCH --cpus-per-task=2", preamble)
            self.assertIn("#SBATCH --mem=16gb", preamble)
            self.assertIn("#SBATCH -t 00:15:00", preamble)
            self.assertNotIn("--gres=", preamble)

    def resolve(self, *options: str, interactive: bool = False):
        argv = (
            ["qi-setup"] if interactive else ["submit_job", "--job_script", "script.py"]
        )
        with patch.object(sys, "argv", [*argv, *options]):
            return get_vm_config(
                parse_args(is_interactive=interactive), is_interactive=interactive
            )

    def test_explicit_default_valued_cpu_and_memory_are_honored(self):
        for interactive in (False, True):
            with self.subTest(interactive=interactive):
                cfg = self.resolve(
                    "--template",
                    "CPU",
                    "--ncpus",
                    "2",
                    "--memory",
                    "16",
                    "--ngpus",
                    "0",
                    "--walltime",
                    "00:15:00",
                    interactive=interactive,
                )
                self.assertEqual(
                    (cfg.num_cpus, cfg.memory, cfg.num_gpus, cfg.walltime),
                    (2, 16, 0, "00:15:00"),
                )

    def test_omitted_options_keep_template_values_without_mutation(self):
        before = replace(TEMPLATES["CPU"])
        self.resolve("--template", "CPU", "--ncpus=2", "--memory=16")
        self.assertEqual(self.resolve("--template", "CPU"), before)
        self.assertEqual(TEMPLATES["CPU"], before)

    def test_nondefault_values_and_partial_overrides(self):
        cfg = self.resolve("--template=CPU", "--ncpus=3", "--memory=17")
        self.assertEqual((cfg.num_cpus, cfg.memory), (3, 17))
        cfg = self.resolve("--template=CPU", "--ncpus=2")
        self.assertEqual((cfg.num_cpus, cfg.memory), (2, TEMPLATES["CPU"].memory))

    def test_explicit_default_gpu_count_and_zero_are_both_honored(self):
        self.assertEqual(self.resolve("--template=CPU", "--ngpus=1").num_gpus, 1)
        self.assertEqual(self.resolve("--template=CPU", "--ngpus=0").num_gpus, 0)

    def test_unknown_template_uses_mode_defaults(self):
        for interactive, defaults in (
            (False, JOB_DEFAULTS),
            (True, INTERACTIVE_DEFAULTS),
        ):
            with self.subTest(interactive=interactive):
                self.assertEqual(
                    self.resolve("--template=custom", interactive=interactive), defaults
                )
                cfg = self.resolve(
                    "--template=custom",
                    "--ngpus=0",
                    "--memory=17",
                    interactive=interactive,
                )
                self.assertEqual(cfg, replace(defaults, num_gpus=0, memory=17))

    def test_all_explicit_fields_override_template_even_when_equal_to_defaults(self):
        # Use another existing template with contrasting enum/resource fields.
        template = replace(TEMPLATES["A100_80GB"], walltime="01:00:00")
        for interactive, defaults in (
            (False, JOB_DEFAULTS),
            (True, INTERACTIVE_DEFAULTS),
        ):
            with (
                self.subTest(interactive=interactive),
                patch.dict(TEMPLATES, TEST=template),
            ):
                cfg = self.resolve(
                    "--template=TEST",
                    f"--queue={defaults.queue.value}",
                    f"--ncpus={defaults.num_cpus}",
                    f"--memory={defaults.memory}",
                    f"--ngpus={defaults.num_gpus}",
                    f"--accelerator_model={defaults.accelerator_model.value}",
                    f"--architecture={defaults.architecture.value}",
                    f"--walltime={defaults.walltime}",
                    interactive=interactive,
                )
                self.assertEqual(cfg, defaults)


if __name__ == "__main__":
    unittest.main()
