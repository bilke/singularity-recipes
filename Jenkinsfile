pipeline {
  agent { label 'singularity' }
  environment {
	  SREGISTRY_CLIENT = 'registry'
  }
  stages {
    stage('serial') {
      steps {
        dir('centos7') {
	  sh 'sudo singularity build ogs.simg Singularity.gcc.minimal'
	}
      }
    }
    stage('openmpi-2.1.3') {
      steps {
        dir('centos7') {
	  sh 'sudo singularity build ogs-petsc-openmpi-2.1.3.simg Singularity.gcc.openmpi-2.1.3'
	}
      }
    }
    stage('openmpi-3.1.1') {
      steps {
        dir ('centos7') {
	  sh 'sudo singularity build ogs-petsc-openmpu.3.1.1.simg Singularity.gcc.openmpi-3.1.1'
	}
      }
    }
  }
}
