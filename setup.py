import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pymanifest',
    version='1.1',
    packages=['pymanifest'],
    author="Clay Brooks",
    author_email="clay_brooks@outlook.com",
    description="File list utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/claybrooks/pymanifest",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Operating System :: OS Independent",
    ],
)