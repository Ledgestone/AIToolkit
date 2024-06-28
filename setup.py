from setuptools import setup, find_packages

setup(
    name='ai_toolkit',
    version='2.5.0',
    author='Andrew Hellrigel',
    author_email='andrew.hellrigel@ledgestone.com',
    description='A simplified interface for interacting with LLMs',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'openai',
        'anthropic',
        'requests',
        'promptlayer',
    ],
)
