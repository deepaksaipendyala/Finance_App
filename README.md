# Finance App with Plaid and Django Rest Framework

# BrightMoney Assignment

[Plaid](https://plaid.com/docs/)​ is an account aggregation service where users can login with their bank credentials and plaid fetches last two years of transaction and account balance data for their bank account. This project is its implementation using Django.

* `Item`​ , a set of credentials (map of key value pairs) associated with a financial institution and a user.
  * Users can have multiple Items for multiple financial institutions.

* Each `​Item​` can have many associated accounts, which hold information such as balance, name, and account type


    $ redis-server
  python -m pip install -r requirements.txt
    $ source ./env/bin/activate
    $ celery -A plaid_django worker -l info
    $ python manage.py runserver
