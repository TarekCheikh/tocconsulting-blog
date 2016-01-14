# This is my conf file
$yum_upgrade = <<SCRIPT
echo "Start centos provisionning"
sudo yum -y install epel-release
sudo yum -y update
SCRIPT

$apt_upgrade = <<SCRIPT
echo "Start debian provisionning"
sudo apt-get update
sudo apt-get -y upgrade
SCRIPT

Vagrant.configure("2") do |config|
	# Global for all VMs
	#config.vm.provision "shell", inline: "echo Hello you"
	config.vm.network "public_network"

	# centos7one VM
	config.vm.define "centos7one" do |centos7one|
		centos7one.vm.box = "centos7one"
		centos7one.vm.provision "shell", inline: $yum_upgrade

		centos7one.vm.provider "virtualbox" do |centos7one|
			centos7one.customize [ "modifyvm", :id, "--cpus", "2" ]
			centos7one.customize [ "modifyvm", :id, "--memory", "1024" ]
		end
	end

	# ubuntu14one VM
	config.vm.define "ubuntu14one" do |ubuntu14one|
		ubuntu14one.vm.box = "ubuntu14one"
		ubuntu14one.vm.provision "shell", inline: $apt_upgrade
		ubuntu14one.vm.provider "virtualbox" do |ubuntu14one|
                        ubuntu14one.customize [ "modifyvm", :id, "--cpus", "2" ]
                        ubuntu14one.customize [ "modifyvm", :id, "--memory", "1024" ]
                end
	end

	# debian8one VM
	config.vm.define "debian8one" do |debian8one|
                debian8one.vm.box = "debian8one"
		debian8one.vm.provision "shell", inline: $apt_upgrade
                debian8one.vm.provider "virtualbox" do |debian8one|
                        debian8one.customize [ "modifyvm", :id, "--cpus", "2" ]
                        debian8one.customize [ "modifyvm", :id, "--memory", "1024" ]
                end
        end

	# debian8two VM
        config.vm.define "debian8two" do |debian8two|
                debian8two.vm.box = "debian8two"
                debian8two.vm.provision "shell", inline: $apt_upgrade
                debian8two.vm.provider "virtualbox" do |debian8two|
                        debian8two.customize [ "modifyvm", :id, "--cpus", "2" ]
                        debian8two.customize [ "modifyvm", :id, "--memory", "1024" ]
                end
        end

	# freeBSD10 VM
	config.vm.define "freeBSD10" do |freeBSD10|
                freeBSD10.vm.box = "freeBSD10"
		freeBSD10.vm.synced_folder ".", "/vagrant", id: "vagrant-root", disabled: true
		freeBSD10.ssh.shell = "sh"
		freeBSD10.vm.base_mac = "080027D14C66"
                freeBSD10.vm.provider "virtualbox" do |freeBSD10|
                        freeBSD10.customize [ "modifyvm", :id, "--cpus", "2" ]
                        freeBSD10.customize [ "modifyvm", :id, "--memory", "1024" ]
                end
        end
end
