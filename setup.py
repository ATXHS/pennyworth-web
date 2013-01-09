from setuptools import setup, find_packages
setup(
    name = "pennyweb",
    version = '0.1',
    packages = find_packages(),
    #install_requires = ["xmleater >= 0.1", "oauth >= 1.0"],

    description = "Web app for hackerspace membership stuff.",

    entry_points = {
        'console_scripts': [
            'manage-pennyweb = pennyweb.manage:main'
        ]
    }
)
