from difflib import unified_diff
from os import getenv
from pathlib import Path
import re
from repo2docker.app import Repo2Docker
from shutil import copytree, rmtree


# To replace reference-outputs/, set this environment variable
REPLACE_REFERENCE_OUTPUTS = getenv("REPLACE_REFERENCE_OUTPUTS", "").lower() in (
    "true",
    "1",
)


def _recursive_filelist(d):
    parent = Path(d)
    files = list(p for p in parent.rglob("*") if p.is_file())
    relative_files = [p.relative_to(parent) for p in files]
    return files, relative_files


def _normalise_build_script(lines):
    for line in lines:
        line = re.sub(
            r"build_script_files/\S+-2f(repo2docker-2fbuildpacks-2f\S+)-\w+(\s+|/)",
            r"<normalised>\1 ",
            line,
        )
        line = re.sub(r"(LABEL repo2docker.version=)\S+", r"\1 <normalised>", line)
        yield line


def test_compare(tmp_path):
    r2d = Repo2Docker()
    r2d.engine = "shellscript"
    r2d.output_image_spec = "test"
    r2d.repo = "https://github.com/binder-examples/conda"
    r2d.ref = "577865357337eb0b562fc747afb9e98b4a7bcacc"
    r2d.run = False
    r2d.user_id = 1002
    r2d.user_name = "test"

    r2d.config.ShellScriptEngine.output_directory = str(tmp_path)
    r2d.config.ShellScriptEngine.jupyter_token = "test-token"

    r2d.start()

    # Ignore .git when comparing outputs
    rmtree(tmp_path / "test" / "src" / ".git")
    # Normalise filenames under build_script_files
    for build_script in (tmp_path / "test" / "build_script_files").iterdir():
        normalised_name = re.match(
            r"^.+-2f(repo2docker-2fbuildpacks-2f.+)-\w+$", build_script.name
        ).group(1)
        build_script.rename(build_script.parent / normalised_name)

    files, relative_files = _recursive_filelist(
        Path(__file__).parent / "reference-outputs"
    )
    outputs, relative_outputs = _recursive_filelist(tmp_path)
    # Normalise the outputs in-place
    for o in outputs:
        normalised_lines = list(_normalise_build_script(o.read_text().splitlines()))
        o.write_text("\n".join(normalised_lines) + "\n")

    if REPLACE_REFERENCE_OUTPUTS:
        print("Updating reference-outputs from {tmp_path}")
        rmtree(Path(__file__).parent / "reference-outputs")
        copytree(tmp_path, Path(__file__).parent / "reference-outputs")

    assert sorted(relative_files) == sorted(relative_outputs)
    for f, o in zip(sorted(files), sorted(outputs)):
        flines = list(_normalise_build_script(f.read_text().splitlines()))
        olines = list(_normalise_build_script(o.read_text().splitlines()))
        diff = list(unified_diff(flines, olines))
        assert not diff, "\n".join(diff)
