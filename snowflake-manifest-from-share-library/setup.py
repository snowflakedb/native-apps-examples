#!/usr/bin/env python3
"""
Setup script for Snowflake Manifest from Share.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
current_dir = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(current_dir, 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = "A Python library to create declarative application manifests from secure data shares."

# Read requirements
requirements_path = os.path.join(current_dir, 'requirements.txt')
with open(requirements_path, 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Read dev requirements
dev_requirements_path = os.path.join(current_dir, 'requirements-dev.txt')
dev_requirements = []
if os.path.exists(dev_requirements_path):
    with open(dev_requirements_path, 'r', encoding='utf-8') as f:
        dev_requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='snowflake-manifest-from-share',
    version='0.1.0',
    author='Mohammed Shamil',
    author_email='s.mohammedshamil@snowflake.com',
    description='Create declarative application manifest from secure data share',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/snowflake-manifest-from-share',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration',
    ],
    python_requires='>=3.6',
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
        'test': dev_requirements,
    },
    entry_points={
        'console_scripts': [
            'snowflake-manifest-from-share=snowflake_manifest_from_share.cli:main',
        ],
    },
    keywords='snowflake data-share manifest application declarative',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/snowflake-manifest-from-share/issues',
        'Source': 'https://github.com/yourusername/snowflake-manifest-from-share',
    },
)