import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stadincijfers", 
    version="0.2.2",
    author="Kay Warrie, Sofie Cromheeke",
    author_email="kaywarrie@gmail.com, sofie.cromheeke@gmail.com",
    description="A python package to make data from stadincijfers easily available for data scientists. ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/warrieka/stadincijfers.py",
    packages=["stadincijfers"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[ 'pandas' ],
    python_requires='>=2.7',
)
