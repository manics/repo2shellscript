# repo2shellscript

[![Build Status](https://travis-ci.com/manics/repo2shellscript.svg?branch=master)](https://travis-ci.com/manics/repo2shellscript)

`repo2shellscript` is a plugin for [repo2docker](http://repo2docker.readthedocs.io) that outputs a directory with a shell-script and required files.
It does not build a container image, instead you should take the output and use it to build some other execution environment.


## Installation

This plugin is still in development and relies on [unreleased features of repo2docker](https://github.com/jupyter/repo2docker/pull/848).

    pip install -U git+https://github.com/manics/repo2docker.git@abstractengine
    pip install -U git+https://github.com/manics/repo2shellscript.git@master


## Running

Simply include `--engine shellscript` in the arguments to `repo2docker`:

    repo2docker --engine shellscript --no-run repository/to/build

Since this does not build anything you must pass `--no-run`.
