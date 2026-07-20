from setuptools import find_packages, setup
from typing import List


def get_requirements() -> List[str]:
    """Return the list of requirements from requirements.txt."""
    requirement_list: List[str] = []
    try:
        with open("requirements.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                requirement = line.strip()
                # skip empty lines, comments, and the editable-install line
                if requirement and not requirement.startswith("#") and requirement != "-e .":
                    requirement_list.append(requirement)
    except FileNotFoundError:
        print("requirements.txt file not found")
    return requirement_list


setup(
    name="NetworkSecurity",
    version="0.0.1",
    author="Megha Deopa",
    author_email="megha.deopa13@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements(),
)