from setuptools import setup, find_packages

setup(
    name="email_extractor",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0", 
        "fake-useragent>=1.1.0",
        "lxml>=4.9.0"
    ],
    author="Your Name",
    description="A comprehensive email extraction tool with anti-bot protection",
    python_requires=">=3.7",
)