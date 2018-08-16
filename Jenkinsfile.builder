pipeline {
  options {
    buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '30'))
  }
  agent { label 'singularity' }
  parameters {
    booleanParam(name: 'centos', defaultValue: false, description: 'ubuntu or centos')
    string(name: 'openmpi_version', defaultValue: '3.1.3', description: '')
    string(name: 'repo', defaultValue: 'https://github.com/ufz/ogs', description: 'Git repository URL')
    string(name: 'branch', defaultValue: 'master', description: 'Git repository branch')
  }
  stages {
    stage('Build') {
      steps {
        echo "Using CentOS ${params.centos}, OpenMPI version: ${params.openmpi_version}"
        dir('hpccm') {
          sh "python3 ../hpc-container-maker/hpccm.py --recipe ogs-builder.py \
            --userarg ompi=${params.openmpi_version} \
                      centos=${params.centos} \
                      repo=${params.repo} \
                      branch={params.branch} \
            --format singularity \
            > Singularity.${params.centos}-openmpi-${params.openmpi_version}"
          sh "cat Singularity.${params.centos}-openmpi-${params.openmpi_version}"
          sh "sudo singularity build \
            ogs.${params.centos}-openmpi-${params.openmpi_version}.simg \
            Singularity.${params.centos}-openmpi-${params.openmpi_version}"
        }
      }
    }
  }
}
