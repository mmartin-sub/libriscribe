from setuptools import setup, find_packages

setup(
    name="libriscribe",
    version="0.2.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "typer",
        "openai",
        "python-dotenv",
        "pydantic",
        "pydantic-settings",
        "beautifulsoup4",
        "requests",
        "markdown",
        "fpdf",
        "tenacity",
    ],
    entry_points={
        "console_scripts": [
            "libriscribe=libriscribe.main:app",  # Updated entry point
        ],
    },
)