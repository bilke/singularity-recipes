pipeline {
  options {
    buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '1'))
  }
  agent { label 'singularity' }
  environment {
    SREGISTRY_CLIENT = 'registry'
  }
  stages {
    stage('SCM') {
      steps {
        checkout scm: [
                        $class: 'GitSCM',
                        branches: scm.branches,
                        doGenerateSubmoduleConfigurations: false,
                        extensions: [[$class: 'SubmoduleOption',
                                      disableSubmodules: false,
                                      parentCredentials: false,
                                      recursiveSubmodules: true,
                                      reference: '',
                                      trackingSubmodules: false]],
                        submoduleCfg: [],
                        userRemoteConfigs: scm.userRemoteConfigs
                ]
      }
    }

    stage('Build Docker and Singularity images') {
      parallel {
        stage('Singularity') {
          stages {
            stage('ubuntu-openmpi-2.1.3') {
              steps {
                dir('hpccm') {
                  sh 'python3 ../hpc-container-maker/hpccm.py --recipe ogs-builder.py --userarg ompi=2.1.3 --format singularity > Singularity.ubuntu-openmpi-2.1.3'
                  sh 'sudo singularity build ogs.ubuntu-openmpi-2.1.3.simg Singularity.ubuntu-openmpi-2.1.3'
                }
              }
            }
            stage('ubuntu-openmpi-3.1.1') {
              steps {
                dir('hpccm') {
                  sh 'python3 ../hpc-container-maker/hpccm.py --recipe ogs-builder.py --userarg ompi=3.1.1 --format singularity > Singularity.ubuntu-openmpi-3.1.1'
                  sh 'sudo singularity build ogs.ubuntu-openmpi-3.1.1.simg Singularity.ubuntu-openmpi-3.1.1'
                }
              }
            }
          }
        }
        stage('Docker') {
          stages {
            stage('ubuntu-openmpi-2.1.3') {
              steps {
                dir('hpccm') {
                  sh 'python3 ../hpc-container-maker/hpccm.py --recipe ogs-builder.py > Dockerfile.ubuntu-openmpi-2.1.3'
                  sh 'docker build -t ogs.ubuntu-openmpi-2.1.3 -f Dockerfile.ubuntu-openmpi-2.1.3 .'
                }
              }
            }
          }
        }
      }
    }
  }
  post {
    always {
      archiveArtifacts artifacts: 'hpccm/**/Singularity.*,hpccm/**/Dockerfile.*'
    }
    success { 
      archiveArtifacts artifacts: '**/*.simg'
    }
  }
}
