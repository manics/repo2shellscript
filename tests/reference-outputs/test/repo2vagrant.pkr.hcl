source "vagrant" "virtualbox" {
  communicator = "ssh"
  source_path = "ubuntu/bionic64"
  # box_version = "v20200821.1.0"
  provider = "virtualbox"
  # add_force = true
}

build {
  sources = [
    "source.vagrant.virtualbox"
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
      "sudo /tmp/repo2shellscript/repo2shellscript-build.bash",
      "sudo cp /tmp/repo2shellscript/repo2shellscript.service /etc/systemd/system/",
      "sudo systemctl daemon-reload",
      "sudo systemctl enable repo2shellscript",
    ]
    # Some environments such as conda can take a very long time to build
    timeout = "30m"
  }
}
