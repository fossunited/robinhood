from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in robinhood/__init__.py
from robinhood import __version__ as version

setup(
	name="robinhood",
	version=version,
	description="The Robin Hood Army is a volunteer-based Zero funds organization that works to get surplus food from restaurants to the less fortunate sections of society in cities across India and 14 other countries.",
	author="zerodha",
	author_email="shridhar.p@zerodha.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
