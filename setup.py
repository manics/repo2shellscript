import setuptools

setuptools.setup(
    name="repo2shellscript",
    # https://github.com/jupyter/repo2docker/pull/848 was merged!
    install_requires=[
        "dockerfile-parse",
        "jupyter-repo2docker>=2022.02.0",
        "importlib_resources;python_version<'3.7'",
    ],
    python_requires=">=3.7",
    author="Simon Li",
    url="https://github.com/manics/repo2shellscript",
    description="Repo2docker shell-script extension",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    use_scm_version={"write_to": "repo2shellscript/_version.py"},
    setup_requires=["setuptools_scm"],
    license="BSD",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        "repo2docker.engines": ["shellscript = repo2shellscript:ShellScriptEngine"]
    },
)
