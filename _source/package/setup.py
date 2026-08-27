import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ImportMPCR",
    version="0.0.1",
    author="MPCR Lab",
    author_email="mpcrlab@gmail.com",
    description="Import everything used in the MPCR lab.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mpcrlab/importmpcr",
    install_requires=[],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
