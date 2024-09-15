# https://github.com/docker-library/buildpack-deps/blob/91dd87eecfa0cf2ae7e793aedbaca682dfcf693d/ubuntu/jammy/Dockerfile
# With the addition of
# - sudo since it makes it easier to switch USER

apt-get -qq update

# buildpack-deps:jammy-curl
# buildpack-deps:jammy-scm
# buildpack-deps:jammy
# + sudo

apt-get -qq install --yes --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    netbase \
    wget \
    \
    tzdata \
    \
    git \
    mercurial \
    openssh-client \
    subversion \
    \
    procps \
    \
    autoconf \
    automake \
    bzip2 \
    default-libmysqlclient-dev \
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

rm -rf /var/lib/apt/lists/*
