pipeline {
    agent { label 'singularity' }
    environment {
	SREGISTRY_CLIENT = 'registry'
    }
    stages {
        stage('Build') {
            steps {
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
