from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Web Scraper do serwisu Librus Synergia'

setup(
    name="librus_scraper",
    version=VERSION,
    description=DESCRIPTION,
    author="Piotr Ginał",
    packages=["librus_scraper"],
    install_requires=[
        "beautifulsoup4",
        "requests",
    ],
    keywords='scraper librus librus-synergia'
)
