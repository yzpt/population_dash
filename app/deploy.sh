# Dockerize and deploy the app to Cloud Run

# config
PROJECT_ID="kooling-yzpt"
REGION="europe-west9"
CONTAINER_NAME="population-map-container"
ARTIFACT_REGISTRY_LOCATION="europe-west9"
ARTIFACT_REGISTRY_REPO_NAME="population-map-repo"
APP_SERVICE_NAME="population-map-service"
APP_FOLDER="./"
PORT=8050

# requirements
# pip freeze > requirements.txt

# Build
echo "Building $CONTAINER_NAME"
docker build -t $ARTIFACT_REGISTRY_LOCATION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY_REPO_NAME/$CONTAINER_NAME $APP_FOLDER

# local docker run
docker run -p $PORT:$PORT $ARTIFACT_REGISTRY_LOCATION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY_REPO_NAME/$CONTAINER_NAME

# Create a repository on Artifact Registry
# echo "Creating repository $ARTIFACT_REGISTRY_REPO_NAME"
# gcloud artifacts repositories create $ARTIFACT_REGISTRY_REPO_NAME --repository-format=docker --location=$ARTIFACT_REGISTRY_LOCATION --description="allo"

# Docker login
# gcloud auth configure-docker europe-west9-docker.pkg.dev

# Push
echo "Pushing $CONTAINER_NAME"
docker push $ARTIFACT_REGISTRY_LOCATION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY_REPO_NAME/$CONTAINER_NAME

# Cloud Run 
echo "Deploying $APP_SERVICE_NAME"
# --cpu 8 --memory 16Gi --execution-environment gen2
gcloud run deploy $APP_SERVICE_NAME --image $ARTIFACT_REGISTRY_LOCATION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY_REPO_NAME/$CONTAINER_NAME --platform managed --region $REGION --allow-unauthenticated --port $PORT --cpu 8 --memory 16Gi --execution-environment gen2
