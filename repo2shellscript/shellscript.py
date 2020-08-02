# Create a shell script instead of building a Docker image
from dockerfile_parse import DockerfileParser
import json
import os
import shlex
from shutil import copytree
from string import Template
import tarfile
from traitlets import Unicode
from uuid import uuid4

from repo2docker.engine import (
    ContainerEngine,
    Image,
)


def _expand_env(s, *args):
    # repo2docker uses PATH when expanding PATH
    env = {"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"}
    for e in reversed(args):
        env.update(e)
    return Template(s).substitute(env)


def _sudo_user(user, bash, env):
    if user == "root":
        return bash
    envkeys = ",".join(env.keys())
    quoted = shlex.quote(bash)
    sudo = f"sudo -u {user} --preserve-env={envkeys} bash -c {quoted}"
    return sudo


# https://github.com/docker-library/buildpack-deps/tree/f84f6184d79f2cb7ab94c365ac4f47915e7ca2a8/ubuntu/bionic
# With the addition of
# - sudo since it makes it easier to switch USER
BUILDPACK_BIONIC = """\
apt-get -qq update

# buildpack-deps:bionic-curl
# buildpack-deps:bionic-scm
# buildpack-deps:bionic
# + sudo

apt-get -qq install --yes --no-install-recommends \
    ca-certificates \
    curl \
    netbase \
    wget \
    \
    gnupg \
    dirmngr \
    \
    bzr \
    git \
    mercurial \
    openssh-client \
    subversion \
    procps \
    \
    autoconf \
    automake \
    bzip2 \
    dpkg-dev \
    file \
    g++ \
    gcc \
    imagemagick \
    libbz2-dev \
    libc6-dev \
    libcurl4-openssl-dev \
    libdb-dev \
    libevent-dev \
    libffi-dev \
    libgdbm-dev \
    libglib2.0-dev \
    libgmp-dev \
    libjpeg-dev \
    libkrb5-dev \
    liblzma-dev \
    libmagickcore-dev \
    libmagickwand-dev \
    libmaxminddb-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libpng-dev \
    libpq-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libtool \
    libwebp-dev \
    libxml2-dev \
    libxslt-dev \
    libyaml-dev \
    make \
    patch \
    unzip \
    xz-utils \
    zlib1g-dev \
    \
    sudo

if apt-cache show 'default-libmysqlclient-dev' 2>/dev/null | grep -q '^Version:'; then
    echo 'default-libmysqlclient-dev'
else
    echo 'libmysqlclient-dev'
fi
rm -rf /var/lib/apt/lists/*
"""


def _docker_copy(copy):
    # Since this is run inside the environment we need to ensure path is absolute.
    # Also need to deal with copying the contents of directories to match Docker.
    paths = shlex.split(copy)
    # Don't quote dest because it may contain envvars
    dest = paths[-1]
    statement = ""
    for n in range(len(paths) - 1):
        # Strip / because source paths should never be absolute,
        # and we'll check if a path is a file or dir during the copy
        p = os.path.join(
            '"${_REPO2SHELLSCRIPT_SRCDIR}"', shlex.quote(paths[n].strip("/"))
        )
        statement += f"if [ -d {p} ]; then cp -a {p}/* {dest}; else cp {p} {dest}; fi\n"
    return statement


def dockerfile_to_bash(dockerfile, buildargs):
    """
    Convert a Dockerfile to a bash script

    dockerfile: A Dockerfile, or a directory containing a Dockerfile
    buildargs: Dict of build arguments
    return: Dictionary with fields:
        'bash': array of bash statements
        'env': dict of runtime environment variables
        'start': start command
        'user': user to run start command
    """
    bash = []
    cmd = ""
    entrypoint = ""
    # Runtime environment
    runtimeenv = {}
    # Build and runtime environment
    currentenv = {}
    parser = DockerfileParser(dockerfile)
    user = "root"

    for d in parser.structure:
        statement = ""
        instruction = d["instruction"]
        for line in d["content"].splitlines():
            if instruction == "COMMENT":
                statement += f"{line}\n"
            else:
                statement += f"# {line}\n"
        if instruction in ("EXPOSE", "COMMENT", "LABEL"):
            pass
        elif instruction == "FROM":
            if d["value"] != "buildpack-deps:bionic":
                raise NotImplementedError(f"Base image {d['value']} no supported")
            statement += BUILDPACK_BIONIC
        elif instruction == "ARG":
            argname = d["value"].split("=", 1)[0]
            try:
                argvalue = shlex.quote(buildargs[d["value"]])
            except KeyError:
                if "=" in d["value"]:
                    argvalue = d["value"].split("=", 1)[1]
                else:
                    raise
            # Expand because this may eventually end up as a runtime env
            argvalue = _expand_env(argvalue, currentenv)
            currentenv[argname] = argvalue
            statement += f"export {argname}={argvalue}\n"
        elif instruction == "CMD":
            cmd = " ".join(shlex.quote(p) for p in json.loads(d["value"]))
        elif instruction == "COPY":
            statement += _docker_copy(d["value"])
        elif instruction == "ENTRYPOINT":
            entrypoint = " ".join(shlex.quote(p) for p in json.loads(d["value"]))
        elif instruction == "ENV":
            # repodocker is inconsistent in how it uses ENV
            try:
                k, v = d["value"].split("=", 1)
            except ValueError:
                k, v = d["value"].split(" ", 1)
            argvalue = _expand_env(v, currentenv)
            currentenv[k] = argvalue
            statement += f"export {k}={argvalue}\n"
            runtimeenv[k] = argvalue
        elif instruction == "RUN":
            run = _sudo_user(user, d["value"], currentenv)
            statement += f"{run}\n"
        elif instruction == "USER":
            user = d["value"]
        elif instruction == "WORKDIR":
            statement += f"cd {d['value']}\n"
        else:
            raise NotImplementedError(
                f"Unexpected Dockerfile instruction: {instruction} {d}"
            )
        bash.append(statement)

    if not cmd or not entrypoint:
        # Default should be to use the parent image CMD or ENTRYPOINT
        raise NotImplementedError("CMD and ENTRYPOINT are required")

    r = {
        "bash": bash,
        "env": runtimeenv,
        "start": f"{entrypoint} {cmd}",
        # Expand ${NB_USER}
        "user": _expand_env(user, currentenv),
    }
    return r


class ShellScriptEngine(ContainerEngine):
    """
    ShellScript container engine
    """

    def __init__(self, *, parent):
        super().__init__(parent=parent)

    output_directory = Unicode(
        os.path.join(os.getcwd(), "repo2shellscript-output"),
        config=True,
        allow_none=False,
        help="""
        Parent directory for output.

        Default is $CWD/repo2shellscript-output
        """,
    )

    def build(
        self,
        *,
        buildargs=None,
        cache_from=None,
        container_limits=None,
        tag="",
        custom_context=False,
        dockerfile="",
        fileobj=None,
        path="",
        **kwargs
    ):

        buildargs = buildargs or {}

        if not tag:
            tag = str(uuid4())
        # TODO: Delete existing directory

        if kwargs:
            raise ValueError("Additional kwargs not supported")

        builddir = os.path.join(self.output_directory, tag)
        os.makedirs(builddir)
        if fileobj:
            tarf = tarfile.open(fileobj=fileobj)
            tarf.extractall(builddir)
        else:
            copytree(path, builddir)

        if dockerfile:
            dockerfile = os.path.join(builddir, dockerfile)
        else:
            dockerfile = os.path.join(builddir)

        r = dockerfile_to_bash(dockerfile, buildargs)
        build_file = os.path.join(builddir, "repo2shellscript-build.bash")
        start_file = os.path.join(builddir, "repo2shellscript-start.bash")

        with open(build_file, "w") as f:
            # Set _REPO2SHELLSCRIPT_SRCDIR so that we can reference the source dir
            # in the script
            f.write(
                f"""\
#!/usr/bin/env bash
set -eux
_REPO2SHELLSCRIPT_SRCDIR=$(cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd)

"""
            )
            f.write("\n".join(r["bash"]))
            f.write("\n")
        os.chmod(build_file, 0o755)

        with open(start_file, "w") as f:
            f.write(
                f"""\
#!/usr/bin/env bash
set -eux
if [ $(id -un) != {r['user']} ]; then
    echo ERROR: Must be run as user {r['user']}
    exit 1
fi
"""
            )
            for k, v in r["env"].items():
                f.write(f"export {k}={v}\n")
            f.write(f"exec {r['start']}\n")
        os.chmod(start_file, 0o755)

        yield f"Output directory: {builddir}\n"
        yield f"Build script: {build_file}\n"
        yield f"Start script: {start_file}\n"
        yield f"User: {r['user']}\n"

    def images(self):
        if not os.path.isdir(self.output_directory):
            return []
        dirs = os.listdir(self.output_directory)
        images = [(d if ":" in d else f"{d}:latest") for d in dirs]
        return [Image(tags=[tag]) for tag in images]

    def inspect_image(self, image):
        assert os.path.exists(os.path.join(self.output_directory, image))
        return Image(tags=[image])

    def push(self, image_spec):
        raise NotImplementedError("push() is not supported")

    def run(
        self,
        image_spec,
        *,
        command=None,
        environment=None,
        ports=None,
        publish_all_ports=False,
        remove=False,
        volumes=None,
        **kwargs
    ):
        raise NotImplementedError("run() is not supported")
