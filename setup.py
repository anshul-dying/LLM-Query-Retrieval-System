from setuptools import find_packages, setup
from typing import List

HYPEN_E_DOT = '-e .'

def get_requirements(path: str) -> List[str]:
    requirements = []
    with open(path) as file:
        requirements = file.readlines()
        requirements = [req.replace('\n', '') for req in requirements]
        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)
    return requirements

setup(
    name='llm_query_retrieval',
    version='0.0.1',
    author='AnshulK',
    author_email='anshulkhaire3303dll@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt'),
    description='LLM-powered query-retrieval system for insurance policy documents',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)