#!/bin/bash

show_usage()
{
  echo "Usage:"
  echo "./scp_server.sh [options] host fullpath"
  echo
  echo "Options:"
  echo "-c, --clean    delete remote static and template folders before copying"
  echo "-r, --restart  restart app container after updating files"
  echo
}

CLEAN=false
RESTART=false

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -c|--clean)
      CLEAN=true
      shift # past argument
      ;;
    -r|--restart)
      RESTART=true
      shift # past argument
      ;;
    -*|--*)
      echo "Unknown option $1"
	  echo
	  show_usage
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

if [ -z "$1" ] || [ -z "$2" ]
  then
    show_usage
	exit 1
fi
HOST=$1
BASE=$2

set -e
set -x

scp server/*.py $HOST:$BASE/server
scp server/config.server.json $HOST:$BASE/server/config.json
scp server/requirements.txt $HOST:$BASE/server
scp server/blocked_words.txt $HOST:$BASE/server

if [ "$CLEAN" = true ]
  then
    ssh $HOST "rm -rf $BASE/server/static"
    ssh $HOST "rm -rf $BASE/server/template"
fi
scp -r server/static/ $HOST:$BASE/server
scp -r server/template/ $HOST:$BASE/server

ssh $HOST "find $BASE -type f | xargs chmod 664"

if [ "$RESTART" = true ]
  then
    ssh $HOST "cd $BASE; docker-compose restart cherrypy"
fi
