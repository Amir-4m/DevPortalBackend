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

if [ -z "$DATA" ]; then
	echo "$DATA is mandatory"
	exit
fi
echo "$DATA" | jq . > cookie-anwser.json
PROJECT_SLUG=$(jq -r '.project_slug' cookie-anwser.json)

yes | cookiecutter --replay-file cookie-anwser.json https://github.com/projectpipeline/cookiecutter-django.git
cp ./{{_copier_conf.answers_file}} ./$PROJECT_SLUG/{{_copier_conf.answers_file}}.jinja
cp ./copier.yml ./$PROJECT_SLUG/
mv ./$PROJECT_SLUG/$PROJECT_SLUG/* ../pp_backend/{{project_name}}
rm -r ./$PROJECT_SLUG/$PROJECT_SLUG
copier copy --overwrite --UNSAFE -a $ANSWER_FILE ./$PROJECT_SLUG $DESTINATION

rm -r ./$PROJECT_SLUG
