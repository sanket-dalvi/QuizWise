# QuizWise: Quiz Management System

QuizWise is not just a tool; it encapsulates a user-centric philosophy that places the needs and experiences of its users at the forefront

![Alt text](image.png)

### Prerequisites

- Python 3.x.
- Django
- PostgreSQL

### How to Run:

- Unzip provided file and open "QUIZWISE" folder  in VScode
- Load libraries:
  ```
  pipenv install
  ```
- To add a package
  ```
  pipenv install <package>
  ```
- Create and activate environment:
  ```
  pipenv shell
  ```

- update settings.py (database) add according to your database

```
  DATABASES = {
    'default': {
         "ENGINE": "django.db.backends.postgresql",
         "NAME": "YOUR_DATABASE_NAME",
         "USER":"postgres",
         "PASSWORD":"YOUR_PASSWORD",
         "HOST":"localhost",
         "PORT":"5432",
     }
}
```

- Install below modules:
```
pip install django
pip install psycopg2
pip install django-money
pip install pipreqs
python manage.py collect static
```` 
- Install modules from requirements.txt:
```
pipreqs . --force
```` 
- Run Migrations:
 ```
  python manage.py makemigration
  python manage.py makemigrations QuizCreator
  python manage.py makemigrations QuizParticipant
  python manage.py migrate
  ```
- Run server:
```
  python manage.py runserver
```
### Now, you're all set to use QuizWise! Open your browser and navigate to http://127.0.0.1:8000/ to access the QuizWise application.