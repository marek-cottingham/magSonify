import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='pyMagnetoSonify',  
    version='0.1',
    scripts=['pyMagnetoSonify'] ,
    author="Marek Cottingham",
    author_email="mcottingham@outlook.com",
    description="Package for the sonification of space magnetosphere data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheMuonNeutrino/pyMagnetoSonify",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
 )
