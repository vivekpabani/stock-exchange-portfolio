build:
	python3 manage.py makemigrations
	python3 manage.py migrate

run:
	python3 manage.py runserver

test:
	python3 manage.py test portfolio
