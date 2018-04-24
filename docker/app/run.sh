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
    --privileged \
    -e "container=docker" \
    -v /sys/fs/cgroup:/sys/fs/cgroup \
    --rm=true \
    --name $CONTAINERNAME \
    --link tele_postgres:pg \
    --link tele_es:elasticsearch \
    -e TELEUID=$TELEUID \
    -e TELEGID="$TELEGID" \
    -e TELEOSTYPE=$OSTYPE \
    -v $TELE:/home/teleceptor/teleceptor \
    -p $HOSTPORT:$HOSTPORT \
    teleceptor/app \
    /home/teleceptor/teleceptor/entrypoint.sh
