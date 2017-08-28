# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
    config.vm.box = "centos/7"
    config.vm.hostname = "loris-dev"
    # config.vm.box_check_update = false

    config.vm.network :forwarded_port, guest: 80, host: 8080, host_ip: "127.0.0.1"
    # config.vm.network "private_network", ip: "192.168.33.10"
    # config.vm.network "public_network"

    config.vm.synced_folder ".", "/home/vagrant/sync", disabled: true
    config.vm.synced_folder ".", "/vagrant", create: true, type: "virtualbox"

    config.vm.provider "virtualbox" do |vb|
        vb.gui = false
        vb.memory = "2048"
    end

    config.vm.provision "shell", privileged: false, inline: <<-EOT
        # Set selinux
        sudo setenforce 0
        sudo sed -i 's/^SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config

        # Update
        sudo yum -y update

        # Set sysctl
        sudo sysctl -w vm.max_map_count=262144
        echo "vm.max_map_count = 262144" | sudo tee -a /etc/sysctl.conf

        # Set timezone
        sudo timedatectl set-timezone Asia/Tokyo

        # Set locale
        sudo localectl set-locale LANG=ja_JP.utf8
        source /etc/locale.conf

        # Install repository
        sudo yum -y install epel-release

        # Install docker
        sudo yum install -y yum-utils
        sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        sudo yum makecache fast
        sudo yum -y install docker-ce
        sudo usermod -aG docker vagrant
        sudo systemctl enable docker
        sudo systemctl daemon-reload
        sudo systemctl start docker
EOT

end
