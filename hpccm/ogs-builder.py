"""This example demonstrates user arguments.
The OpenMPI version can be specified on the command line.  
Note: no validation is performed on the user supplied information.
Usage:
$ hpccm.py --recipe ogs-builder.py --userarg ompi=2.1.3 centos=true \
  repo=https://github.com/bilke/ogs branch=singularity \
  cmake="-DOGS_BUILD_UTILS=ON -DOGS_BUILD_TESTS=OFF"

Other options:
- ogs=false Builds a MPI test container
- infiniband=false Disables infinband
"""
# pylint: disable=invalid-name, undefined-variable, used-before-assignment

import os
from hpccm.templates.git import git

singularity = hpccm.config.g_ctype == container_type.SINGULARITY
docker = hpccm.config.g_ctype == container_type.DOCKER


##### Tools #####
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

##### Options #####
centos =     str2bool(USERARG.get('centos',     'False'))
ogs =        str2bool(USERARG.get('ogs',        'True'))
infiniband = str2bool(USERARG.get('infiniband', 'True'))
ompi_version =        USERARG.get('ompi',       '3.1.1')

repo =                USERARG.get('repo',       'https://github.com/ufz/ogs')
branch =              USERARG.get('branch',     'master')
cmake_args =          USERARG.get('cmake',      '')

######
# Devel stage
######

Stage0 += comment(__doc__, reformat=False)

# Choose between either Ubuntu 16.04 (default) or CentOS 7
# Add '--userarg centos=true' to the command line to select CentOS
image = 'ubuntu:16.04'
if centos:
  image = 'centos/devtoolset-6-toolchain-centos7'

Stage0.baseimage(image=image)

if centos:
  Stage0 += user(user='root')
  Stage0 += packages(ospackages=['epel-release'])

# Common directories
Stage0 += shell(commands=['mkdir -p /apps /scratch /lustre /work /projects'])

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
                          'python3 -m pip install scif'])

# GNU compilers
if not centos:
  Stage0 += gnu(fortran=False)

# Mellanox OFED
if infiniband:
  Stage0 += mlnx_ofed(version='3.4-1.0.0.0')

# OpenMPI
Stage0 += openmpi(version=ompi_version, cuda=False, infiniband=infiniband)

# SCI-F: mpi-bandwidth
Stage0 += copy(src='mpi-bandwidth.scif', dest='/var/tmp/mpi-bandwidth.scif')
Stage0 += shell(commands=['scif install /var/tmp/mpi-bandwidth.scif'])

### OGS ###
if ogs:
  Stage0 += shell(commands=['python3 -m pip install cmake conan'])
  if centos:
    Stage0 += shell(commands=['curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.rpm.sh | bash'])
  else:
    Stage0 += packages(ospackages=['software-properties-common'])
    Stage0 += shell(commands=['cd ~',
                              'add-apt-repository ppa:git-core/ppa',
                              'curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash'])
  Stage0 += packages(ospackages=['git', 'git-lfs'])
  Stage0 += shell(commands=['git lfs install'])

  build_cmds = [git().clone_step(repository=repo, branch=branch, path='/apps/ogs',
                                 directory='ogs', lfs=centos),
                'cd /apps/ogs/ogs && git fetch --tags',
                'mkdir -p /apps/ogs/install',
                'mkdir -p /apps/ogs/build',
                'cd /apps/ogs/build',
                ('CONAN_SYSREQUIRES_SUDO=0 CC=mpicc CXX=mpic++ cmake /apps/ogs/ogs ' +
                 '-DCMAKE_BUILD_TYPE=Release ' +
                 '-DCMAKE_INSTALL_PREFIX=/apps/ogs/install ' +
                 '-DOGS_USE_PETSC=ON ' +
                 '-DOGS_USE_CONAN=ON ' +
                 '-DOGS_CONAN_USE_SYSTEM_OPENMPI=ON ' +
                 cmake_args
                 ),
                'make -j',
                'make install']
  Stage0 += shell(commands=build_cmds)

  run_cmds = ["exec /apps/ogs/install/bin/ogs \"$@\""]
  Stage0 += runscript(commands=run_cmds)

  Stage0 += label(metadata={
    'repo': repo, 'branch': branch
  })
else:
  run_cmds = ["scif \"$@\""]
  Stage0 += runscript(commands=run_cmds)

Stage0 += label(metadata={
  'openmpi.version': ompi_version,
  'infiniband': infiniband
})
######
# Runtime image
######
