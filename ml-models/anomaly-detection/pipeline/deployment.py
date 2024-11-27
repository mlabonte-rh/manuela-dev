def get_deployment_resource(model_artifact_id):
    deployment_resource = {
        'apiVersion': 'serving.kserve.io/v1beta1',
        'kind': 'InferenceService',
        'metadata': {
            'name': 'inference-service',
            'labels': {
                'opendatahub.io/dashboard': 'true'
            },
            'annotations': {
                'serving.kserve.io/deploymentMode': 'ModelMesh'
            },
        },
        'spec': {
            'predictor': {
                'model': {
                    'modelFormat': {
                        'name': 'sklearn',
                        'version': '0',
                    },
                    'runtime': 'anomaly-detection-model-server',
                    'storage': {
                        'key': 'aws-connection-user-bucket',
                        'path': model_artifact_id,
                    }
                }
            }
        }
    }
    return deployment_resource


