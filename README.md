# Finance App with Plaid and Django Rest Framework

# BrightMoney Assignment

[Plaid](https://plaid.com/docs/)​ is an account aggregation service where users can login with their bank credentials and plaid fetches last two years of transaction and account balance data for their bank account. This project is its implementation using Django.

* `Item`​ , a set of credentials (map of key value pairs) associated with a financial institution and a user.
  * Users can have multiple Items for multiple financial institutions.

* Each `​Item​` can have many associated accounts, which hold information such as balance, name, and account type

## Demo:
[1](images/1.png)
[2](images/2.png)
[3](images/3.png)
[4](images/4.png)

## Commands to run the app
- ``` $ python -m pip install -r requirements.txt ```
- ``` $ source ./env/bin/activate ```
- ``` $ redis-server ```
- ``` $ celery -A plaid_django worker -l info```
-  ``` $ python manage.py runserver 0.0.0.0:3000 ```
