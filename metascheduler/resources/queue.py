import json
from datetime import datetime
from flask import request
from metascheduler.models import Queue, Job, JobStatus
from api import MetaschedulerResource, ExistingQueueResource, queue_exists


def queue_length(queue_name):
    return Job.objects(job_type=queue_name, status=JobStatus.pending).count()


class QueueManagementResource(MetaschedulerResource):
    def get(self):
        jsoned_queues = []

        queues = Queue.objects().all()

        for queue in queues:
            q_dict = queue.to_dict()
            q_dict['length'] = queue_length(queue.job_type)

            jsoned_queues.append(q_dict)

        return {'queues': jsoned_queues}

    def put(self):
        queue_dict = json.loads(request.data)
        queue_name = queue_dict['job_type']

        if len(Queue.objects(job_type=queue_name)) > 0:
            raise Exception('Queue with same job_type already exists')

        queue = Queue(**queue_dict)
        queue.save()

        return {'queue': queue.to_dict()}


class QueueResource(ExistingQueueResource):
    def get(self, job_type):
        cpu_avail = int(request.args.get("cpu_available", 1))

        pulled_job = Job._get_collection().find_and_modify(
            query={
                'job_type': job_type,
                'status': JobStatus.pending,
                'descriptor.container.cpu_needed': {'$lte': cpu_avail}
            },
            sort={'last_update': 1},
            update={
                '$set': {
                    'status': JobStatus.pulled,
                    'debug': {
                        'pulled_by': str(request.remote_addr)
                    }
                }
            },
            fields={'job_type': False, 'last_update': False},
            new=True
        )
        if not pulled_job:
            return

        pulled_job['job_id'] = str(pulled_job['_id'])
        del pulled_job['_id']

        return {'job': pulled_job}

    def post(self, job_type):
        descriptor = request.json.get('descriptor')
        assert descriptor

        callback = request.json.get('callback')
        replicate = request.json.get('multiply') or 1

        if replicate == 1:
            job = Job(
                job_type=job_type,
                descriptor=descriptor,
                callback=callback,
            ).save()
            return {'job': job.to_dict()}
        else:
            now = datetime.now()
            return {
                "job_ids": [
                    str(r) for r in Job._get_collection().insert([{
                        "job_type": job_type,
                        "status": JobStatus.pending,
                        "last_update": now,
                        "descriptor": descriptor,
                        "callback": callback,
                    } for _ in xrange(replicate)]
                    )
                ]
            }

    def delete(self, job_type):
        queue = Queue.objects.get(job_type=job_type)
        queue.delete()

        Job.objects(job_type=job_type).delete()


class QueueInfoResource(MetaschedulerResource):
    def get(self, job_type):
        if not queue_exists(job_type):
            return {'exists': False}

        return {'length': queue_length(job_type), 'exists': True}
