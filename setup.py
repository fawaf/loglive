from setuptools import setup

setup(
    name="loglive",
    version="0.0.1",
    description="Live log-viewer powered by Tornado, ZeroMQ, and websockets",
    author="Kenny Do",
    author_email="kedo@ocf.berkeley.edu",
    license="MIT License",
    packages=["loglive"],
    install_requires=[
        "pyinotify>=0.9.4",
        "pyzmq>=13.1.0",
        "tornado>=0.1.2",
    ],
    include_package_data=True
    )
