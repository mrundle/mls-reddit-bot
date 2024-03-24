import os
from setuptools import setup

# for README.md
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "mls_reddit_bot",
    version = "1.0.0",
    author = "Matt Rundle",
    author_email = "m.n.rundle@gmail.com",
    description = ("Reddit bot for curating Reddit r/MLS gameday match threads "
                   "via MLS and ESPN APIs"),
    license = "GPLv3",
    keywords = "reddit mls bot",
    url = "https://github.com/mrundle/mls-reddit-bot",
    packages=["mls_reddit_bot", "tests"],
    long_description=read("README.md"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'praw',
        'dateutils',
        'pytz',
    ],
    # for creating lambda layer zip; https://pypi.org/project/lambda-setuptools/#description
    setup_requires=['lambda_setuptools'],
    #lambda_function="mls_reddit_bot.main:main",

    ## tests
    tests_require=['pytest']
)
