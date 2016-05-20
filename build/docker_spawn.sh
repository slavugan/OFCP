#!/bin/bash
# Author: Alastair Kerr
# Spin up infrastructure with docker
# Create docker images from Dockerfiles, runs containers

YELLOW='\033[0;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

#FORCE=true # delete all existing OFC images/ containers and rebuild from scratch
FORCE=false 

# Container names
OFC_SVC="ofc-service"
OFC_SQL="ofc-sql"
OFC_DATA_VOL="ofc-sql-data"

# Image names
OFC_SVC_IMG="ofc-service-image"
OFC_SQL_IMG="ofc-sql-image"
OFC_DATA_IMG="ofc-sql-data-image"

function usage {
    echo -e "${YELLOW}Usage: -f (force rebuild) -h (help)${NC}"
}

while [[ $# > 0 ]]
do
flag="$1"
case $flag in
    -f|--force)
    FORCE=true
    shift
    ;;
    -h|--help)
    usage && exit 0
    shift
    ;;
    *)
    echo -e "${RED}Unknown flag `echo $flag | tr -d '-'`${NC}" && usage && exit 1
esac
shift
done

echo -e "${YELLOW}Force rebuild: ${FORCE}\nSpawning OFC infrastructure..${NC}"

docker images | grep -q ${OFC_DATA_IMG}
if [ $? -eq 0 ] && [ "$FORCE" = false ]; then
    echo -e "${YELLOW}Using existing docker image for ofc-sql-data container${NC}"
else
    echo -e "${YELLOW}Building new image for ofc-sql-data container${NC}"
    ( cd mysql-data && docker build --no-cache -t ${OFC_DATA_IMG} . )
fi
docker run -dit --name ${OFC_DATA_VOL} ${OFC_DATA_IMG}

docker images | grep -q ${OFC_SQL_IMG}
if [ $? -eq 0 ] && [ "$FORCE" = false ]; then
    echo -e "${YELLOW}Using existing docker image for ofc-sql container${NC}"
else
    echo -e "${YELLOW}Building new image for ofc-sql container${NC}"
    ( cd mysql && docker build --no-cache -t ${OFC_SQL_IMG} . )
fi
docker run --volumes-from ${OFC_DATA_VOL} -dit --name ${OFC_SQL} -p 3306:3306 ${OFC_SQL_IMG}

docker images | grep -q ${OFC_SVC_IMG}
if [ $? -eq 0 ] && [ "$FORCE" = false ]; then
    echo -e "${YELLOW}Using existing docker image for ofc-service container${NC}"
else
    echo -e "${YELLOW}Building new image for ofc-service container${NC}"
    ( cd ofc && docker build --no-cache -t ${OFC_SVC_IMG} . )
fi
docker run -dit --name ${OFC_SVC} -p 8080:8080 ${OFC_SVC_IMG}
