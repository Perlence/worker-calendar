from setuptools import setup

setup(
    name='Savory Perlence',
    version='1.0',
    description='Various web applications.',
    author='Sviatoslav Abakumov',
    author_email='dust.harvesting@gmail.com',
    entry_points={
        'console_scripts': [
           'startapp = wsgi.app:start',
           'debugapp = wsgi.app:debug',
        ],
    },
    install_requires=[
        'flask>=0.10.1',
        'gunicorn',
        'icalendar',
    ],
)
