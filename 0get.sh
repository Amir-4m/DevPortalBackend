DESTINATION="$1"
ANSWER_FILE="$2"
DATA="$3"


if [ -z "$DESTINATION" ]; then
	echo "DESTINATION is mandatory"
	exit
fi

if [ -z "$ANSWER_FILE" ]; then
	echo "ANSWER_FILE is mandatory"
	exit
fi

copier copy --overwrite --UNSAFE -a $ANSWER_FILE . $DESTINATION
