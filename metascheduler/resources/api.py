import gevent
from flask import jsonify, current_app
from flask_restful import Resource
from metascheduler.models import Queue
import traceback


def api_decorator(f):
    def decorated(*args, **kwargs):
        try:
            result = f(*args, **kwargs)
            if not result:
                result = {}
            return jsonify(success=True, **result)
        except Exception, e:
            if current_app.config['DEBUG']:
                return jsonify(
                    success=False,
                    exception=str(e),
                    traceback=traceback.format_exc()
                )
            else:
                return jsonify(success=False)

    return decorated


class MetaschedulerResource(Resource):
    method_decorators = [api_decorator]


def queue_exists(job_type):
    return len(Queue.objects(job_type=job_type)) == 1


def queue_exists_decorator(f):
    def decorated(job_type, *args, **kwargs):
        if queue_exists(job_type):
            return f(job_type, *args, **kwargs)
        else:
            raise Exception('Queue does not exist')

    return decorated


class ExistingQueueResource(Resource):
    method_decorators = [queue_exists_decorator, api_decorator]


def parse_jobid(f):
    def decorated(job_id, *args, **kwargs):
        if ',' in job_id:
            jobs = {
              job_id: gevent.spawn(
                    f,
                    job_id,
                    *args,
                    **kwargs
                ) for job_id in job_id.split(',')
            }
            return {
                job_id: gevent_job.get() for job_id, gevent_job in jobs.items()
            }
        else:
            return f(job_id, *args, **kwargs)

    return decorated


class MSJobResource(Resource):
    method_decorators = [parse_jobid, api_decorator]
