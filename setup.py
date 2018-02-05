"""Setup for agnosticcontentxblock XBlock."""

import os
from setuptools import setup


def find_package_data(pkg, data_paths):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for data_path in data_paths:
        package_dir = pkg.replace(".", "/")
        for dirname, _, files in os.walk(package_dir + "/" + data_path):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), package_dir))
    return {pkg: data}


package_data = {}  # pylint: disable=invalid-name
package_data.update(find_package_data("agnosticcontentxblock", ["static", "public", "templates"]))

setup(
    name='agnostic-content-xblock',
    version='0.5',
    description='Agnostic Content XBlock', # TODO: write a better description.
    license='AGPLv3',
    include_package_data=True,
    packages=[
        'agnosticcontentxblock',
    ],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'agnosticcontentxblock = agnosticcontentxblock.block:AgnosticContentXBlock',
        ]
    },
    package_data=package_data,
)
