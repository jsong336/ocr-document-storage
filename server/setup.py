from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name="chak.io",
    version="0.0.0",
    description="chak.io server",
    long_description=long_description,
    author="Jeongwon Song",
    author_email="jeongwon412@gmail.com",
    packages=["chak"],  # same as name
    python_requires=">=3.10.0",
    install_requires=[
        "fastapi",
        "fastapi[uvicorn]",
        "uvicorn[standard]",
        "pydantic-settings",
        "pydantic[email]",
        "pymongo[srv]",
    ],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "faker",
        ]
    },
)
