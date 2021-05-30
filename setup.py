from setuptools import setup
from setuptools import find_namespace_packages

# load the README file.
with open(file="README.md", mode="r") as fh:
    long_description = fh.read()

setup(

    name='telbot3D',

    version='0.0.1',

    description='A trading robot built for Python that uses the Alpaca Trading API.',

    long_description=long_description,

    long_description_content_type="text/markdown",

    url='https://github.com/Mosiramakata/telbot3D',

    install_requires=[
        'alpaca-trade-api>=1.2.1',
    ],

    keywords='finance, alpaca, api, trading robot',

    include_package_data=True,

    python_requires='>=3.9',

    classifiers=[

        # I can say what phase of development my library is in.
        'Development Status :: 3 - Alpha',


        # Here I'll note that package was written in English.
        'Natural Language :: English',

        # Here I'll note that any operating system can use it.
        'Operating System :: OS Independent',

        # Here I'll specify the version of Python it uses.
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',

        # Here are the topics that my library covers.
        'Topic :: Database',
        'Topic :: Education',
        'Topic :: Office/Business'

    ]
)