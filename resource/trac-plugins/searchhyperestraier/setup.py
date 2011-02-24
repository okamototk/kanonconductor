from setuptools import find_packages, setup

setup(
    name='TracHyperestraierPlugin', version='0.1',
    packages=find_packages(exclude=['*.tests*']),
    entry_points = """
        [trac.plugins]
        searchhyperestraier.searchhyperestraier = searchhyperestraier.searchhyperestraier
    """,
)

