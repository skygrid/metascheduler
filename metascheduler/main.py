from gevent import monkey
from mongoengine import connect
from flask import Flask
from flask_cors import CORS
from flask_restful import Api

import resources


app = Flask(__name__)
app.config.from_envvar('METASCHEDULER_CONFIG')
cors = CORS(app)

mongo_host = app.config.get('DB_HOST') or 'localhost'

if app.config['DB_USE_AUTH']:
    connect(
        app.config['DB'],
        username=app.config['DB_USERNAME'],
        password=app.config['DB_PASSWORD'],
        host=mongo_host
    )
else:
    connect(
        app.config['DB'],
        host=mongo_host
    )


# Route all resources

api = Api(app)

api.add_resource(resources.StatusResource, '/status')
api.add_resource(resources.JobResource, '/jobs/<string:job_id>')
api.add_resource(resources.JobStatusResource, '/jobs/<string:job_id>/status')
api.add_resource(resources.JobOutputResource, '/jobs/<string:job_id>/output')

if app.config['DEBUG']:
    api.add_resource(resources.JobDebugResource, '/jobs/<string:job_id>/debug')


api.add_resource(resources.QueueManagementResource, '/queues')
api.add_resource(resources.QueueResource, '/queues/<string:job_type>')
api.add_resource(resources.QueueInfoResource, '/queues/<string:job_type>/info')

monkey.patch_all()  # if not started by gunicorn


if __name__ == "__main__":
    app.run()
