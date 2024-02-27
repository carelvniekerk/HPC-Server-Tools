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
"""Return the number of running jobs for a user on the HPC cluster"""

import os


def get_jobs(username: str) -> list[dict[str, str]]:
    """Get a list of jobs for a user on the HPC cluster"""
    jobs = os.popen(f'qstat -u {username}').read().split('\n')[5:-1]
    jobs = [job.split() for job in jobs]

    jobs = [{'job_num': idx, 'jobid': job[0], 'name': job[3], 'user': job[2], 'status': job[9]}
            for idx, job in enumerate(jobs)]

    return jobs


if __name__ == '__main__':
    jobs = get_jobs(os.environ.get("USER_NAME"))
    jobs = [job for job in jobs if job['status'] == 'R' and 'DevSession' not in job['name']]

    print(len(jobs))
