source "docker" "repo" {
  image = "ubuntu:18.04"
  commit = true
  changes = [
    "ENTRYPOINT /usr/local/bin/repo2shellscript-start.bash",
    "USER ${user}",
  ]
}

build {
  sources = [
    "source.docker.repo"
  ]

  provisioner "shell" {
    inline = [
      "mkdir /tmp/repo2shellscript",
    ]
  }

  provisioner "file" {
    source = "./"
    destination = "/tmp/repo2shellscript/"
  }

  provisioner "shell" {
    inline = [
      "/tmp/repo2shellscript/repo2shellscript-build.bash",
      "cp /tmp/repo2shellscript/repo2shellscript-start.bash /usr/local/bin/",
    ]
    # Some environments such as conda can take a very long time to build
    timeout = "30m"
  }

  post-processor "docker-tag" {
    repository = "${tag}"
  }
}
