# Copyright (c) 2026 Uno Kim / AMEVA Foundation. All rights reserved.
# SPDX-License-Identifier: Apache-2.0 OR Commercial-License
from setuptools import setup, find_packages

setup(
    name="amv-aichain",
    version="2.0.2",
    description="Ultra-lightweight Zero-Dependency AI chaining & agent framework for Termux, Android and Edge computing.",
    long_description=open("README.md", encoding="utf-8").read() if open("README.md", encoding="utf-8") else "",
    long_description_content_type="text/markdown",
    author="UnoKim",
    author_email="uno-km@users.noreply.github.com",
    url="https://github.com/uno-km/amv-aichain",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "amv-runtime>=2.9.0",
    ],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Android",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
