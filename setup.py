import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='magSonify',  
    version='0.1',
    packages=[
        'magSonify',
        'magSonify/sonificationMethods',
        'magSonify/sonificationMethods/wavelets',
        'magSonify/devCaching'
    ] ,
    author="Marek Cottingham",
    author_email="mcottingham@outlook.com",
    description="Package for the sonification of space magnetosphere data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheMuonNeutrino/magSonify",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy',
        'scipy',
        'ai.cdas',
        'audiotsm',
        'SoundFile',
    ],
    extras_require={
        'bufferingTest': ['sounddevice'],
    }
 )
