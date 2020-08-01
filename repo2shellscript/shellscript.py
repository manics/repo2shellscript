# Create a shell script instead of building a Docker image
from dockerfile_parse import DockerfileParser
import json
import os
import shlex
from shutil import copytree
import tarfile
from traitlets import Unicode
from uuid import uuid4

from repo2docker.engine import (
    ContainerEngine,
    Image,
)


# class ShellScriptError(Exception):
#     def __init__(self, error, output=None):
#         self.e = error
#         self.output = output

#     def __str__(self):
#         s = "ShellScriptError\n  {}".format(self.e)
#         if self.output is not None:
#             s += "\n  {}".format("".join(self.output))
#         return s


def dockerfile_to_bash(dockerfile, buildargs):
    """
    Convert a Dockerfile to a bash script

    dockerfile: A Dockerfile, or a directory containing a Dockerfile
    buildargs: Dict of build arguments
    return: Dictionary with fields:
        'bash': array of bash statements
        'start': start command
        'env': dict of runtime environment variables
    """
    bash = []
    cmd = ""
    entrypoint = ""
    env = {}
    parser = DockerfileParser(dockerfile)

    for d in parser.structure:
        statement = ""
        instruction = d["instruction"]
        for line in d["content"].splitlines():
            if instruction == "COMMENT":
                statement += f"{line}\n"
            else:
                statement += f"# {line}\n"
        if instruction in ("EXPOSE", "FROM", "COMMENT", "LABEL"):
            pass
        elif instruction == "ARG":
            try:
                argvalue = shlex.quote(buildargs[d["value"]])
            except KeyError:
                if "=" in d["value"]:
                    argvalue = d["value"]
                else:
                    raise
            statement += f"export {d['value']}={argvalue}\n"
        elif instruction == "CMD":
            cmd = " ".join(shlex.quote(p) for p in json.loads(d["value"]))
        elif instruction == "COPY":
            copy = [shlex.quote(p) for p in shlex.split(d["value"])]
            statement += f"cp {copy}\n"
        elif instruction == "ENTRYPOINT":
            entrypoint = " ".join(shlex.quote(p) for p in json.loads(d["value"]))
        elif instruction == "ENV":
            statement += f"export {d['value']}\n"
            # repodocker is inconsistent in how it uses ENV
            try:
                k, v = d["value"].split("=", 1)
            except ValueError:
                k, v = d["value"].split(" ", 1)
            env[k] = v
        elif instruction == "RUN":
            statement += f"{d['value']}\n"
        elif instruction == "USER":
            # assert False, d
            print(f"TODO: {d}")
            bash.append(f"TODO: {d}")
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
        "start": f"{entrypoint} {cmd}",
        "env": env,
    }
    return r


class ShellScriptEngine(ContainerEngine):
    """
    Podman container engine
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
            f.write("#!/usr/bin/env bash\nset -eux\n\n")
            f.write("\n".join(r["bash"]))
            f.write("\n")

        with open(start_file, "w") as f:
            f.write("#!/usr/bin/env bash\nset -eux\n\n")
            for k, v in r["env"].items():
                f.write(f"export {k}={v}\n")
            f.write(f"exec {r['start']}\n")

        yield f"Output directory: {builddir}\n"
        yield f"Build script: {build_file}\n"
        yield f"Start script: {build_file}\n"

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
