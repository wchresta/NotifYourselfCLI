import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="notifyourself",
    version="0.1.0",

    author="Wanja Chresta",
    author_email="wanja.hs@chrummibei.ch",
    description="Send a notification to your mobile device",
    entry_points={
        'console_scripts': [ 'notifyourself=notifyourself.notifyourself:main' ]
    },
    install_requires=['requests>=2.0'],
    license='LICENSE',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wchresta/NotifYourselfCLI",
    project_urls={
        "Source Code": "https://github.com/wchresta/NotifYourselfCLI",
        "Issues": "https://github.com/wchresta/NotifYourselfCLI/issues",
    },
    packages=setuptools.find_packages(),
    python_requires='>=2',
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
)
