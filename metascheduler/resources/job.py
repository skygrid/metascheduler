import json
from datetime import datetime

import gevent

from flask import request
from api import MSJobResource

import requests

from metascheduler.models import Job, JobStatus

from flask import current_app


def do_callback(job, timeout):
    if job.callback:
        requests.post(
                job.callback,
                data=json.dumps(job.to_dict()),
                headers={'content-type': 'application/json'},
                timeout=timeout,
        )


class JobResource(MSJobResource):
    def get(self, job_id):
        return Job.objects.get(pk=job_id).to_dict()

    def delete(self, job_id):
        job = Job.objects.get(pk=job_id)
        job.delete()
        return {"result": "deleted"}


class JobStatusResource(MSJobResource):
    def get(self, job_id):
        return {"status": Job.objects.get(pk=job_id).status}

    def post(self, job_id):
        update_dict = request.json
        new_status = update_dict.get('status')

        # 'pulled' can be set only internaly
        assert new_status in JobStatus.valid_statuses - {JobStatus.pulled}

        job = Job.objects.get(pk=job_id)
        job.status = new_status
        job.last_update = datetime.now()
        job.save()

        if job.callback:
            gevent.spawn(
                do_callback,
                job,
                current_app.config["CALLBACK_TIMEOUT"]
            ).start()

        return {'updated_status': job.status}


class JobOutputResource(MSJobResource):
    def get(self, job_id):
        return {
            'output': Job.objects.get(pk=job_id).output
        }

    def post(self, job_id):
        update_dict = request.json
        new_output = update_dict.get('output')

        job = Job.objects.get(pk=job_id)
        job.output = new_output
        job.save()

        return {'updated_output': job.output}


class JobDebugResource(MSJobResource):
    def get(self, job_id):
        return {
            'debug': Job.objects.get(pk=job_id).debug
        }

    def post(self, job_id):
        update_dict = request.json

        job = Job.objects.get(pk=job_id)
        job.debug = update_dict
        job.save()

        if job.callback:
            gevent.spawn(
                do_callback,
                job,
                current_app.config["CALLBACK_TIMEOUT"]
            ).start()

        return job.to_dict()
