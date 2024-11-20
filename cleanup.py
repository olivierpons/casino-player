#!/usr/bin/env python3
"""
Safe cleanup script for Python/CMake project
Removes build artifacts and caches while preserving virtual environments
"""

import os
import shutil
import subprocess
from pathlib import Path


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {message} ==={Colors.ENDC}")


def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_warning(message):
    print(f"{Colors.WARNING}! {message}{Colors.ENDC}")


def remove_directory(path):
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
        print_success(f"Removed directory: {path}")


def remove_file(path):
    if path.exists() and path.is_file():
        os.remove(path)
        print_success(f"Removed file: {path}")


def clean_project():
    root_dir = Path(__file__).parent

    print_header("Cleaning Python artifacts")
    # Python build artifacts - SANS les environnements virtuels !
    directories_to_remove = [
        root_dir / "build",
        root_dir / "dist",
        root_dir / "casino_player.egg-info",
        root_dir / "__pycache__",
        root_dir / ".pytest_cache",
        root_dir / ".mypy_cache",
        root_dir / ".coverage",
    ]

    print_header("Cleaning CMake artifacts")
    # CMake build directories
    cmake_dirs = [
        root_dir / "cmake-build-debug",
        root_dir / "cmake-build-release",
        root_dir / "CMakeFiles",
        root_dir / "_deps",
    ]
    directories_to_remove.extend(cmake_dirs)

    # Remove directories (sauf .venv!)
    for directory in directories_to_remove:
        remove_directory(directory)

    print_header("Cleaning temporary and generated files")
    # File patterns to remove
    patterns_to_remove = [
        "*.so",
        "*.pyd",
        "*.pyc",
        "*.pyo",
        "*.o",
        "*.obj",
        "*.exp",
        "*.lib",
        "CMakeCache.txt",
        "Makefile",
    ]

    for pattern in patterns_to_remove:
        for file_path in root_dir.rglob(pattern):
            # Protection supplémentaire : ne jamais toucher aux fichiers dans .venv
            if ".venv" not in str(file_path):
                remove_file(file_path)

    print_header("Cleaning pip cache")
    subprocess.run(["python3", "-m", "pip", "cache", "purge"], check=True)

    print_warning("Virtual environment (.venv) has been preserved!")
    print_header("Project cleaned successfully!")


if __name__ == "__main__":
    try:
        clean_project()
    except Exception as e:
        print(f"{Colors.FAIL}Error during cleanup: {str(e)}{Colors.ENDC}")
