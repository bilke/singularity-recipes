pipeline {
  options {
    buildDiscarder(logRotator(numToKeepStr: '30', artifactNumToKeepStr: '30'))
  }
  agent { label 'singularity' }
  parameters {
    choice(choices: ['singularity', 'docker'], description: '', name: 'format')
    booleanParam(name: 'centos', defaultValue: false, description: 'ubuntu or centos')
    string(name: 'repo', defaultValue: 'https://github.com/ufz/ogs', description: 'Git repository URL')
    string(name: 'branch', defaultValue: 'master', description: 'Git repository branch')
    choice(choices: ['2.1.3', '2.1.4', '3.0.2', '3.1.1'], description: '', name: 'openmpi_version')
  }
  stages {
    stage('Build') {
      steps {
        script {
          def filename = params.format.capitalize()
          if (params.format == "docker") {
            filename += "file"
          }
          def config_string = "${params.centos}-openmpi-${params.openmpi_version}"
          filename += ".${config_string}"
          dir('hpccm') {
            sh "python3 ../hpc-container-maker/hpccm.py --recipe ogs-builder.py \
              --userarg ompi=${params.openmpi_version} \
                        centos=${params.centos} \
                        repo=${params.repo} \
                        branch=${params.branch} \
              --format ${params.format} \
              > ${filename}"
            sh "cat ${filename}"
            if (params.format == "docker") {
              sh "docker build -t ogs6/${config_string} -f ${filename} ."
            }
            else {
              sh "sudo singularity build ogs.${config_string}.simg ${filename}"
            }
          }
        }
      }
    }
  }
  post {
    success { 
      archiveArtifacts artifacts: '**/*.simg'
      script {
        currentBuild.displayName = "${params.repo} / ${params.branch}"
        currentBuild.description = """
          CentOS: ${params.centos}\n
          Repo: ${params.repo}\n
          Branch: ${params.branch}\n
          Container Format: ${params.format}\n
          OpenMPI: ${params.openmpi_version}
          """.stripIndent()
      }
    }
    always {
      archiveArtifacts artifacts: 'hpccm/**/Singularity.*,hpccm/**/Dockerfile.*'
    }
    cleanup { sh 'rm -rf hpccm/**/*.simg hpccm/**/Singularity.* hpccm/**/Dockerfile.*' }
  }
}

// Note: use input-step to deploy to HPC resource? https://stackoverflow.com/a/45216570/80480
