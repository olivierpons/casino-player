#!/usr/bin/env python3
"""
Rebuild script for casino-player module
This script automates the process of cleaning, building, and installing the module
"""

import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from typing import Tuple


class Colors:
    """ANSI color codes for terminal output"""

    HEADER = "\033[95m"
    OK_BLUE = "\033[94m"
    OK_GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    END_COLOR = "\033[0m"
    BOLD = "\033[1m"


def print_header(message: str) -> None:
    """Print a formatted header message"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {message} ==={Colors.END_COLOR}")


def print_success(message: str) -> None:
    """Print a success message"""
    print(f"{Colors.OK_GREEN}✓ {message}{Colors.END_COLOR}")


def print_warning(message: str) -> None:
    """Print a warning message"""
    print(f"{Colors.WARNING}! {message}{Colors.END_COLOR}")


def print_error(message: str) -> None:
    """Print an error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.END_COLOR}")


def run_command(command: str, description: str) -> Tuple[int, str, str]:
    """
    Run a shell command and return its status and output

    Args:
        command: Command to execute
        description: Description of the command for logging

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    print_header(description)

    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr


def clean_build_files() -> None:
    """Remove all build artifacts and temporary files"""
    print_header("Cleaning up old build files")

    # Directories to remove
    dirs_to_remove = [
        "build",
        "dist",
        "casino_player.egg-info",
        "__pycache__",
        "cmake-build-debug",
    ]

    # Find and remove build directories
    for directory in dirs_to_remove:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                print_success(f"Removed directory: {directory}/")
            except Exception as e:
                print_error(f"Error removing {directory}: {str(e)}")

    # Remove .so files (Unix) or .pyd files (Windows)
    extensions = [".so"] if platform.system() != "Windows" else [".pyd"]
    for ext in extensions:
        for file in os.listdir("."):
            if file.endswith(ext):
                try:
                    os.remove(file)
                    print_success(f"Removed file: {file}")
                except Exception as e:
                    print_error(f"Error removing {file}: {str(e)}")


def check_python_version() -> None:
    """Verify Python version meets minimum requirements"""
    print_header("Checking Python version")

    version = sys.version_info
    min_version = (3, 7)

    if version < min_version:
        print_error(
            f"Python {version[0]}.{version[1]} detected. Version {min_version[0]}.{min_version[1]} or higher is required."
        )
        sys.exit(1)
    else:
        print_success(f"Using Python {version[0]}.{version[1]}.{version[2]}")


def build_cmake() -> None:
    """Configure and build with CMake"""
    print_header("Building with CMake")

    # Créer et configurer le build
    cmake_commands = [
        ("cmake -B cmake-build-debug -DCMAKE_BUILD_TYPE=Debug .", "Configuring CMake"),
        ("cmake --build cmake-build-debug --config Debug", "Building with CMake"),
    ]

    for command, description in cmake_commands:
        return_code, stdout, stderr = run_command(command, description)
        if return_code != 0:
            print_error(f"Error during {description}")
            print_error(f"Command output:\n{stdout}")
            print_error(f"Error output:\n{stderr}")
            sys.exit(1)
        else:
            print_success(description + " completed")


def build_and_install() -> None:
    """Build and install the package"""
    commands = [
        ("python3 -m pip install --upgrade pip", "Upgrading pip"),
        ("python3 -m pip install --upgrade build wheel", "Installing build tools"),
        ("python3 setup.py install", "Installing package"),
    ]

    for command, description in commands:
        return_code, stdout, stderr = run_command(command, description)

        if return_code != 0:
            print_error(f"Error during {description}")
            print_error(f"Command output:\n{stdout}")
            print_error(f"Error output:\n{stderr}")
            sys.exit(1)
        else:
            print_success(description + " completed")


def run_tests() -> None:
    """Run the test suite"""
    if os.path.exists("test_memory.py"):
        print_header("Running tests")
        return_code, stdout, stderr = run_command("python3 test_memory.py", "Testing")

        if return_code != 0:
            print_error("Tests failed")
            print_error(f"Test output:\n{stdout}")
            print_error(f"Error output:\n{stderr}")
            sys.exit(1)
        else:
            print_success("All tests passed")
    else:
        print_warning("No test file found (test_memory.py)")


def copy_stub_file() -> None:
    """Copy the stub file to the installation directory"""
    print_header("Installing documentation stub")

    venv_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv")
    site_packages = None

    for root, dirs, files in os.walk(venv_dir):
        if root.endswith("site-packages"):
            site_packages = root
            break

    if site_packages:
        for item in os.listdir(site_packages):
            if "casino_player" in item:
                target_dir = os.path.join(site_packages, item)
                if item.endswith(".egg"):
                    target_dir = os.path.join(target_dir, "casino_player")

                try:
                    shutil.copy2("casino_player.pyi", target_dir)
                    print_success(f"Documentation stub copied to {target_dir}")
                    return
                except Exception as e:
                    print_error(f"Failed to copy stub file: {str(e)}")
                    return

    print_error("Could not find installation directory")


def main() -> None:
    """Main execution function"""
    start_time = datetime.now()

    print_header(
        f"Starting build process at {start_time.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    try:
        # Run all build steps
        check_python_version()
        clean_build_files()
        build_cmake()
        build_and_install()
        copy_stub_file()
        run_tests()

        # Calculate and display execution time
        end_time = datetime.now()
        duration = end_time - start_time
        print_header(
            f"Build process completed successfully in {duration.total_seconds():.2f} seconds"
        )

    except KeyboardInterrupt:
        print_warning("\nBuild process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
