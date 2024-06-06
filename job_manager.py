
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime
from threading import Lock

from utils.logging import logger


@dataclass
class Event:
    timestamp: datetime
    data: str


@dataclass
class Job:
    status: str
    events: List[Event]
    result: str


jobs_lock = Lock()
jobs: Dict[str, "Job"] = {}


def append_event(job_id: str, event_data: str):
    with jobs_lock:
        if job_id not in jobs:
            # print(f"Start job: {job_id}")
            logger.info("Job %s started", job_id)
            jobs[job_id] = Job(
                status="STARTED",
                events=[],
                result=""
            )
        else:
            # print("Appending event for job")
            logger.info("appending event for job %s : %s", job_id, event_data)

        jobs[job_id].events.append(
            Event(
                timestamp=datetime.now(),
                data=event_data
            )
        )

