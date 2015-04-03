from setuptools import setup

setup(
    name='worker-calendar',
    version='1.0',
    description='Worker calendar.',
    author='Sviatoslav Abakumov',
    author_email='dust.harvesting@gmail.com',
    py_modules=['worker'],
    install_requires=[
        'flask',
        'icalendar',
    ],
)
