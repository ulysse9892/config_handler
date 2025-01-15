from setuptools import setup, find_packages

setup(
    name="config_handler",
    version="0.1.0",
    description="A tool to handle config files in yml format with specific keywords",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ultra112",
    author_email="ulysse.mendezbrid@gmail.com",
    url="https://github.com/ulysse9892/config_handler",
    packages=find_packages(),
    install_requires=[
        "PyYAML==6.0.1",
        "python-dotenv==1.0.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
