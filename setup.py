from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="webpty",
    version="2.0.1",
    author="Satheesh Kumar",
    author_email="mail@satheesh.dev",
    description="A simple web-based application to access system shell via a browser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/satheesh1997/webpty",
    license="License :: OSI Approved :: MIT License",
    include_package_data=True,
    packages=["webpty"],
    keywords=[
        "xterm",
        "browser terminal",
        "webpty",
        "online shell",
        "online terminal",
        "tornado"
    ],
    entry_points={"console_scripts": ["webpty=webpty.server:main"]},
    zip_safe=False,
    python_requires=">=3.6",
    install_requires=["tornado>=6.1"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
