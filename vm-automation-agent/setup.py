"""
Setup script for VM Automation Agent
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README if it exists
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="vm-automation-agent",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Automated VM startup and PostgreSQL database seeding agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/vm-automation-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "psycopg2-binary>=2.9.0",  # PostgreSQL adapter
        "click>=8.0.0",  # CLI framework
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-cov>=3.0',
            'black>=22.0',
            'flake8>=4.0',
        ],
        'windows': [
            'pywin32>=304',  # Windows-specific notifications
        ],
        'linux': [
            'dbus-python>=1.2.0',  # D-Bus for systemd integration
            'PyGObject>=3.40.0',  # GLib bindings
        ],
    },
    entry_points={
        'console_scripts': [
            'vm-agent=vm_agent.cli:main',
        ],
    },
    include_package_data=True,
)