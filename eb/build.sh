module load EasyBuild
module load Singularity

# use current directory as location for generated container recipes & images
export EASYBUILD_CONTAINERPATH=$PWD

# build base container image for OpenMPI + GCC parts of foss/2018a toolchain, on top of CentOS 7.4 base image from Singularity Hub
eb -C --container-build-image OpenMPI-2.1.2-GCC-6.4.0-2.28.eb --container-base shub:shahzebsiddiqui/eb-singularity:centos-7.4.1708 --experimental

# build another container image for the for the full foss/2018a toolchain, using the OpenMPI + GCC container as a base
eb -C --container-build-image foss-2018a.eb --container-base localimage:$PWD/OpenMPI-2.1.2-GCC-6.4.0-2.28.simg --experimental

# build container image for Python 3.6.4 with foss/2018a toolchain by leveraging base container image foss-2018a.simg
eb -C --container-build-image Python-3.6.4-foss-2018a.eb --container-base localimage:$PWD/foss-2018a.simg --experimental
