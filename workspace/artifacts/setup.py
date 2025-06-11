#!/usr/bin/env python3
"""
Setup script для KittyCore 2.0
"""

from setuptools import setup, find_packages

setup(
    name="kittycore",
    version="2.0.0",
    description="Простая платформа для создания AI агентов",
    long_description="KittyCore - Философия: Агент за 5 минут, сложность - по желанию",
    author="KittyCyber",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "httpx>=0.25.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "flake8>=4.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 