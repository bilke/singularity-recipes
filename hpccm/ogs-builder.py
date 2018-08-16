"""This example demonstrates user arguments.
The OpenMPI version can be specified on the command line.  
Note: no validation is performed on the user supplied information.
Usage:
$ hpccm.py --recipe ogs-builder.py --userarg ompi=2.1.3 centos=true repo=https://github.com/bilke/ogs branch=singularity
"""
# pylint: disable=invalid-name, undefined-variable, used-before-assignment

import os
from hpccm.templates.git import git

singularity = hpccm.config.g_ctype == container_type.SINGULARITY
docker = hpccm.config.g_ctype == container_type.DOCKER

######
# Devel stage
######

Stage0 += comment(__doc__, reformat=False)

# Choose between either Ubuntu 16.04 (default) or CentOS 7
# Add '--userarg centos=true' to the command line to select CentOS
image = 'ubuntu:16.04'
centos = USERARG.get('centos', False)
if centos:
  image = 'centos/devtoolset-6-toolchain-centos7'

Stage0.baseimage(image=image)

if centos:
  Stage0 += user(user='root')
  Stage0 += packages(ospackages=['epel-release'])

# Common packages
Stage0 += packages(ospackages=['curl', 'ca-certificates'])

if singularity:
  Stage0 += packages(ospackages=['locales'])
  Stage0 += shell(commands=['echo "LC_ALL=en_US.UTF-8" >> /etc/environment',
                            'echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen',
                            'echo "LANG=en_US.UTF-8" > /etc/locale.conf',
                            'locale-gen en_US.UTF-8'])

# Python
if centos:
  Stage0 += packages(ospackages=['python34-setuptools'])
  Stage0 += shell(commands=['easy_install-3.4 pip'])
else:
  Stage0 += packages(ospackages=['python3-setuptools', 'python3-pip'])
Stage0 += shell(commands=['python3 -m pip install --upgrade pip',
                          'python3 -m pip install cmake conan'])

# GNU compilers
if not centos:
  gnu = gnu(fortran=False)
  Stage0 += gnu


# Mellanox OFED
ofed = mlnx_ofed(version='3.4-1.0.0.0')
Stage0 += ofed

# Set the OpenMPI version based on the specified version (default to 3.0.0)
ompi_version = USERARG.get('ompi', '3.1.1')
ompi = openmpi(version=ompi_version, cuda=False)

Stage0 += ompi

### OGS ###
if centos:
  Stage0 += shell(commands=['curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | bash'])
else:
  Stage0 += packages(ospackages=['software-properties-common'])
  Stage0 += shell(commands=['cd ~',
                            'add-apt-repository ppa:git-core/ppa',
                            'curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash'])
Stage0 += packages(ospackages=['git', 'git-lfs'])
Stage0 += shell(commands=['git lfs install'])

repo = USERARG.get('repo', 'https://github.com/ufz/ogs')
branch = USERARG.get('branch', 'master')

build_cmds = ['mkdir -p /apps/ogs/install',
              'mkdir -p /apps/ogs/build',
              git().clone_step(
                  repository=repo, branch=branch, path='/apps/ogs',
                  directory='ogs', lfs=centos),
              'cd /apps/ogs/build',
              ('CONAN_SYSREQUIRES_SUDO=0 CC=gcc CXX=g++ cmake /apps/ogs/ogs ' +
               '-DCMAKE_BUILD_TYPE=Release ' +
               '-DCMAKE_INSTALL_PREFIX=/apps/ogs/install ' +
               '-DOGS_USE_PETSC=ON ' +
               '-DOGS_USE_CONAN=ON ' +
               '-DOGS_CONAN_USE_SYSTEM_OPENMPI=ON '),
              'make -j',
              'make install']
Stage0 += shell(commands=build_cmds)

######
# Runtime image
######
