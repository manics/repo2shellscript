#!/usr/bin/env bash
set -eux
if [ $(id -un) != test ]; then
    echo ERROR: Must be run as user test
    exit 1
fi
export PATH=/home/test/.local/bin:/home/test/.local/bin:/srv/conda/envs/notebook/bin:/srv/conda/bin:/srv/npm/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export DEBIAN_FRONTEND=noninteractive
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export LANGUAGE=en_US.UTF-8
export SHELL=/bin/bash
export USER=test
export HOME=/home/test
export APP_BASE=/srv
export CONDA_DIR=/srv/conda
export NB_PYTHON_PREFIX=/srv/conda/envs/notebook
export NPM_DIR=/srv/npm
export NPM_CONFIG_GLOBALCONFIG=/srv/npm/npmrc
export NB_ENVIRONMENT_FILE=/tmp/env/environment.lock
export MAMBA_ROOT_PREFIX=/srv/conda
export MAMBA_EXE=/srv/conda/bin/mamba
export KERNEL_PYTHON_PREFIX=/srv/conda/envs/notebook
export REPO_DIR=/home/test
export CONDA_DEFAULT_ENV=/srv/conda/envs/notebook
export PYTHONUNBUFFERED=1
export JUPYTER_TOKEN=${JUPYTER_TOKEN-test-token}
cd /home/test
exec /usr/local/bin/repo2docker-entrypoint jupyter notebook --ip 0.0.0.0
