source "vagrant" "vb_ubuntu1804" {
  communicator = "ssh"
  source_path = "generic/ubuntu1804"
  provider = "virtualbox"
  # add_force = true
}

build {
  sources = [
    "source.vagrant.vb_ubuntu1804"
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
  }
}
