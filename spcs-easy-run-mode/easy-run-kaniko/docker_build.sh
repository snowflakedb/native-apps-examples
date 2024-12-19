# parse args 
IMAGE=${1}
TAG=${2}
BUILD_DIR=${3}
echo "Building image ${IMAGE}:${TAG} from ${BUILD_DIR}"

# build image
DOCKER_BUILDKIT=1 docker build --platform=linux/amd64 --progress=plain -t ${IMAGE}:${TAG} ${BUILD_DIR}