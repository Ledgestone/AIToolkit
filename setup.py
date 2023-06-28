from setuptools import setup

setup(
    name='AIToolkit',
    version='0.0.1',
    author='Andrew Hellrigel',
    author_email='andrew.hellrigel@ledgestone.com',
    description='A simplified interface for interacting with LLMs',
    packages=['ai_toolkit'],
    python_requires='>=3.6',
    install_requires=[
        'openai',
    ],
)
