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

Example:

    $ repo2docker --engine shellscript --user-name test --user-id 1001 --no-run https://github.com/binder-examples/conda

    Picked Git content provider.
    Cloning into '/tmp/repo2dockerp0kyqxx3'...
    Using CondaBuildPack builder
    Output directory: /home/test/repo2shellscript-output/r2dhttps-3a-2f-2fgithub-2ecom-2fbinder-2dexamples-2fconda5778653
    Build script: /home/test/repo2shellscript-output/r2dhttps-3a-2f-2fgithub-2ecom-2fbinder-2dexamples-2fconda5778653/repo2shellscript-build.bash
    Start script: /home/test/repo2shellscript-output/r2dhttps-3a-2f-2fgithub-2ecom-2fbinder-2dexamples-2fconda5778653/repo2shellscript-start.bash
    Systemd service: /home/test/repo2shellscript-output/r2dhttps-3a-2f-2fgithub-2ecom-2fbinder-2dexamples-2fconda5778653/repo2shellscript.service
    User: test

- Output directory: should contain everything required to build the environment, e.g. you could copy this to a Ubuntu 18.04 virtual machine
- Build script: a bash script that will build the environment, must be run as `root`
- Start script: a bash script that should be used to start the environment
- Systemd service: an alternative to the start script
- Packer template: a Vagrant VirtualBox template for building a VM
- User: The user that should be used to run the start script
- Jupyter token: A generated token baked into the scripts


### Example of using the output

This uses a plain `ubuntu:18.04` Docker container as the base environment 🙂:

    docker run -it --name repo2shellscript -p 8888:8888 \
        -v /home/test/repo2shellscript-output/r2dhttps-3a-2f-2fgithub-2ecom-2fbinder-2dexamples-2fconda5778653:/src:ro \
        ubuntu:18.04
    cd /src
    ./repo2shellscript-build.bash
    sudo -u <USER> ./repo2shellscript-start.bash


### Systemd service:

If you use a Ubuntu:18.04 virtual machine your can use Systemd to start jupyter notebook:

    cp repo2shellscript.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl start repo2shellscript

Connect to http://IP:8888.
You will need to enter the auto-generated `Jupyter token` from above.
If you have lost the output you can find the token in `repo2shellscript-start.bash` or `repo2shellscript.service`.
Alternatively set a fixed token in the configuration file.


Alternatively set a fixed token in the configuration file.


### Configuration file

For convenience you may wish to set a fixed token instead of checking the startup logs for the generated token.
Create a repo2docker configuration file, such as `repo2docker_config.py` with

```py
c.ShellScriptEngine.jupyter_token = 'secret123'
```

and run

    repo2docker --config repo2docker_config.py ...
