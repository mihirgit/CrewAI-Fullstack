import json
from datetime import datetime
from threading import Thread
from uuid import uuid4

from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from dotenv import load_dotenv

from crew import CompanyResearchCrew
from job_manager import append_event, jobs_lock, jobs, Event
from utils.logging import logger

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


def kickoff_crew(job_id: str, companies: list[str], positions: list[str]):
    # print(f"Running crew for {job_id}, with companies: {companies} and positions: {positions}")
    logger.info(f"Crew for job {job_id} is starting")

    # Setup CREW here
    results = None
    try:
        company_research_crew = CompanyResearchCrew(job_id)
        company_research_crew.setup_crew(
            companies, positions)
        results = company_research_crew.kickoff()

        logger.info(f"Crew for job {job_id} is complete", results)

    except Exception as e:
        # print(f"CREW FAILED! {str(e)}")
        logger.error(f"Error in kickoff_crew for job {job_id}: {e} exception")
        append_event(job_id, f"An error occurred: {e}")
        with jobs_lock:
            jobs[job_id].status = "ERROR"
            jobs[job_id].result = str(e)

    with jobs_lock:
        jobs[job_id].status = "COMPLETED"
        jobs[job_id].result = results
        jobs[job_id].events.append(Event(
            data="CREW COMPLETED",
            timestamp=datetime.now()
        ))


@app.route('/api/crew', methods=['POST'])
def run_crew():
    logger.info("Received request to run crew")

    # Validation
    data = request.json
    if not data or 'companies' not in data or 'positions' not in data:
        abort(400, description='Invalid request with missing data!')

    job_id = str(uuid4())
    companies = data['companies']
    positions = data['positions']

    # run the crew
    thread = Thread(target=kickoff_crew, args=(job_id, companies, positions))
    thread.start()

    return jsonify({"job_id": job_id}), 202


@app.route('/api/crew/<job_id>', methods=['GET'])
def get_status(job_id):
    # Lock the job
    with jobs_lock:
        job = jobs.get(job_id)
        if job is None:
            abort(404, description="Job not found!")

    # Parse the JSON data
    try:
        result_json = json.loads(job.result)
    except json.JSONDecodeError:
        # if parsing fails, set result_json to original job.results string
        result_json = job.result

    # Return everything
    return jsonify({
        'job_id': job_id,
        'status': job.status,
        'result': result_json,
        'events': [
            {"timestamp": event.timestamp.isoformat(),
             "data": event.data} for event in job.events
        ]
    })


if __name__ == '__main__':
    app.run(debug=True, port=3001)
