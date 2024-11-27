from datetime import datetime
from os import environ

import boto3
import git
import yaml

from deployment import get_deployment_resource


s3_endpoint_url = environ.get('S3_ENDPOINT_URL')
s3_access_key = environ.get('S3_ACCESS_KEY')
s3_secret_key = environ.get('S3_SECRET_KEY')
s3_bucket_name = environ.get('S3_BUCKET_NAME')

timestamp = datetime.now().strftime('%y%m%d%H%M')
git_server_url = 'http://gitea-in-cluster-http.vp-gitea.svc.cluster.local:3000'
git_user = environ.get('username')
git_password = environ.get('password')
git_branch = environ.get('branch', 'main')
ops_repo_location = f'{git_server_url}/{git_user}/industrial-edge.git'
ops_repo_url = (
    f'http://{git_user}:{git_password}@{ops_repo_location.lstrip("http://")}'
)
model_artifact_id = 'model.joblib'


print(f'Uploading model to bucket {s3_bucket_name}'
      f'to S3 storage at {s3_endpoint_url}')
s3_client = boto3.client(
    's3', endpoint_url=s3_endpoint_url,
    aws_access_key_id=s3_access_key, aws_secret_access_key=s3_secret_key
)
try:
    s3_client.create_bucket(Bucket=s3_bucket_name)
except Exception:
    print(f'Failed to create new bucket with name "{s3_bucket_name}". Continuing.')
with open('model.joblib', 'rb') as model_file:
    s3_client.upload_fileobj(model_file, s3_bucket_name, model_artifact_id)


print(f'Checking out repo at {ops_repo_location} with user {git_user}')
ops_repository_local = '/opt/app-root/src/industrial-edge'
try:
    repository = git.Repo.clone_from(ops_repo_url, ops_repository_local)
except git.GitCommandError as error:
    print(f'Git clone failed: {error}\nChecking out local repository.')
    repository = git.Repo(ops_repository_local)

print(f'Checking out branch {git_branch}.')
repository.git.checkout(git_branch)
with repository.config_writer() as git_config:
    git_config.set_value('user', 'name', git_user)

inference_service_cr = get_deployment_resource(model_artifact_id)

print(f'Writing updated Inference Service CR: {inference_service_cr}')

inference_service_manifest_location_dev = (
    f'{ops_repository_local}/charts/datacenter/data-science-project/templates/'
    f'anomaly-detection/anomaly-detection-service.yaml'
)

with open(inference_service_manifest_location_dev, 'w') as outputfile:
    yaml.safe_dump(inference_service_cr, outputfile)

inference_service_manifest_location_tst = (
    f'{ops_repository_local}/charts/datacenter/manuela-tst/templates/'
    f'anomaly-detection/anomaly-detection-service.yaml'
)

with open(inference_service_manifest_location_tst, 'w') as outputfile:
    yaml.safe_dump(inference_service_cr, outputfile)

repository.index.add(inference_service_manifest_location_dev)
repository.index.add(inference_service_manifest_location_tst)
repository.index.commit(f'Model update {timestamp} in test environment.')
repository.remotes.origin.push()
