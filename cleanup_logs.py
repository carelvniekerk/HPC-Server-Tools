# coding=utf-8
# --------------------------------------------------------------------------------
# Project: User tools for HPC
# Author: Carel van Niekerk
# Year: 2024
# Group: Dialogue Systems and Machine Learning Group
# Institution: Heinrich Heine University Düsseldorf
# --------------------------------------------------------------------------------
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
"""Cleanup logs from the job_logs directory"""

import os

LOGS_PATH = f"/gpfs/project/{os.environ.get('USER_NAME')}/job_logs/"


if __name__ == '__main__':
    files = os.listdir(LOGS_PATH)
    # Temp files
    temps = [file for file in files if '_' in file]

    # Completed jobs
    files = [file for file in files if '.OU' in file]
    job_ids = [file.replace('.OU', '') for file in files]

    # Files to remove (temp files and completed jobs)
    files = [file for job in job_ids for file in [f"{job}.ER", f"{job}.OU", f"{job}.sh"]] + temps
    files = [os.path.join(LOGS, file) for file in files]

    cmd = "rm " + " ".join(files) if files else ""
    os.system(cmd)
