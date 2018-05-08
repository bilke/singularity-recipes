sudo singularity build centos7.base centos7/base/Singularity &&
sregistry add --name centos7/base centos7.base &&
sudo singularity build centos7.openmpi-2.1.1 centos7/openmpi/2.1.1/Singularity &&
sregistry add --name centos7/openmpi:2.1.1 centos7.openmpi-2.1.1 &&
sudo singularity build centos7.openmpi-2.1.3 centos7/openmpi/2.1.3/Singularity &&
sregistry add --name centos7/openmpi:2.1.3 centos7.openmpi-2.1.3 &&
sudo singularity build centos7.ogs.petsc centos7/ogs/petsc/Singularity &&
sregistry add --name centos7/ogs/petsc centos7.ogs.petsc

