pipeline {
  agent { label 'singularity' }
  environment {
	  SREGISTRY_CLIENT = 'registry'
  }
  stages {
    stage('Build') {
      steps {
        sh 'singularity --version'
	    	sh './build.sh'
	    }
	  }
	  stage('Push') {
	    steps {
		    sh './push.sh'
	    }
	  }
  }
}
