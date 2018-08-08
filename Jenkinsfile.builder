pipeline {
  options {
    buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '30'))
  }
  agent { label 'singularity' }
  parameters {
    booleanParam(name: 'centos', defaultValue: false, description: 'ubuntu or centos')
    string(name: 'openmpi_version', defaultValue: '3.1.3', description: '')
  }
  stages {
    stage('Build') {
      steps {
        echo "Using CentOS ${params.centos}, OpenMPI version: ${params.openmpi_version}"
      }
    }
  }
}
