#!/bin/bash


if [ "$DATABASE" = "postgres" ]
then
    echo "waiting for database"
    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done
    echo "database is ready."
fi

# اجرای migrate
python manage.py migrate


exec "$@"
