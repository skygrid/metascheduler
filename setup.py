from setuptools import setup, find_packages

setup(
    name='skygrid-metascheduler',
    version='0.5.2',
    url='https://github.com/skygrid/metascheduler',
    author='Alexander Baranov',
    author_email='sashab1@yandex-team.ru',
    packages=['metascheduler', 'metascheduler.resources'],
    description='Metascheduler',
    install_requires=[
        "Flask>=0.10.1",
        "Flask-RESTful>=0.2.12",
        "Jinja2>=2.7.3",
        "MarkupSafe==0.23",
        "WTForms==2.0.1",
        "aniso8601==0.83",
        "argparse==1.2.1",
        "flask-mongoengine>=0.7.1",
        "itsdangerous==0.24",
        "mongoengine==0.13.0",
        "pymongo==3.4.0",
        "pytz==2014.4",
        "requests>=2.3.0",
        "six>=1.7.3",
        "wsgiref>=0.1.2",
        "flask-cors",
        "gevent",
    ],
    tests_require=[
        "nose==1.3.4",
        "nose-testconfig==0.9",
    ],
)
