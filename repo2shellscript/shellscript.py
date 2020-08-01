# Create a shell script instead of building a Docker image
import os
from shutil import copytree

# from subprocess import CalledProcessError, PIPE, STDOUT, Popen
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

        cmdargs = ["build"]

        bargs = buildargs or {}
        for k, v in bargs.items():
            cmdargs.extend(["--build-arg", "{}={}".format(k, v)])

        # if tag:
        #     cmdargs.extend(["--tag", tag])
        if not tag:
            tag = str(uuid4())
        # TODO: Delete existing directory

        if dockerfile:
            cmdargs.extend(["--file", dockerfile])

        if kwargs:
            raise ValueError("Additional kwargs not supported")

        builddir = os.path.join(self.output_directory, tag)
        os.makedirs(builddir)
        if fileobj:
            tarf = tarfile.open(fileobj=fileobj)
            tarf.extractall(builddir)
        else:
            copytree(path, builddir)
        print(builddir)
        yield builddir

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
