# https://github.com/docker-library/buildpack-deps/tree/f84f6184d79f2cb7ab94c365ac4f47915e7ca2a8/ubuntu/bionic
# With the addition of
# - sudo since it makes it easier to switch USER

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
