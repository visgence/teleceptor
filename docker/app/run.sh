TELE=$(cd $(dirname "${BASH_SOURCE[0]}")/../../ && pwd -P)
TELEUID=$UID
TELEGID=$(id $USER -g)

HOSTPORT=8000
CONTAINERNAME=tele
while getopts ":p:n:" opt; do
    case $opt in
        p)
          HOSTPORT=$OPTARG
          ;;
        n)
          CONTAINERNAME=$OPTARG
          ;;
        \?)
          echo "Invalid option: -$OPTARG" >&2
          exit 1
          ;;
        :)
          echo "Option -$OPTARG requires an argument." >&2
          exit 1
          ;;
    esac
done


docker run -t -i -P \
    --rm=true \
    --name $CONTAINERNAME \
    --link tele_postgres:pg \
    -e TELEUID=$TELEUID \
    -e TELEGID="$TELEGID" \
    -e TELEOSTYPE=$OSTYPE \
    -v $TELE:/home/tele/teleceptor \
    -p $HOSTPORT:8000 \
    teleceptor/app \
    /home/tele/teleceptor/entrypoint.sh
