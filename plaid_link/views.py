from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid_django.settings import LOGIN_REDIRECT_URL
from .models import Item
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


# environment variable
PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_ENV = 'sandbox'
PLAID_COUNTRY_CODES = 'US'
PLAID_PRODUCTS = 'transactions'
PLAID_REDIRECT_URI = None

access_token = None
item_id = None

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
access_token = None
item_id = None


@csrf_exempt
def create_link_token(request):
    # Get the client_user_id by searching for the current user
    user = 'user_good'
    client_user_id = user
    # Create a link_token for the given user
    request = LinkTokenCreateRequest(
            products=[Products("auth")],
            client_name="Plaid Test App",
            country_codes=[CountryCode('US')],
            redirect_uri='https://financeapp.deepaksaip.repl.co/oauth.html',
            language='en',
            webhook='https://financeapp.deepaksaip.repl.co/webhook',
            user=LinkTokenCreateRequestUser(
                client_user_id=client_user_id
            )
        )
    response = client.link_token_create(request)
    # Send the data to the client
    return JsonResponse(response.to_dict())


@csrf_exempt
def exchange_public_token():
    global access_token
    public_token = request.form['public_token']
    request = ItemPublicTokenExchangeRequest(
      public_token=public_token
    )
    response = client.item_public_token_exchange(request)
    # These values should be saved to a persistent database and
    # associated with the currently signed-in user
    access_token = response['access_token']
    item_id = response['item_id']
    return JsonResponse({'public_token_exchange': 'complete'})


@login_required(login_url=LOGIN_REDIRECT_URL)
def index(request):
    keys = {
        'plaid_environment': PLAID_ENV,
        'plaid_products': PLAID_PRODUCTS,
        'plaid_country_codes': PLAID_COUNTRY_CODES,

    }
    return render(request, "oauth.html", context=keys)


@login_required(login_url=LOGIN_REDIRECT_URL)
def home(request):
    items = Item.objects.filter(user=request.user)
    user = request.user
    transactions_query = items.values_list('account__transaction__name', "account__transaction__amount",
                      'account__transaction__date').all()
    transactions = []
    cnt = 0
    for x in transactions_query:
        if cnt > 30:
            break
        if x[0]:
            x = {"name": x[0], "amount": x[1], "date": str(x[2])}
            transactions.append(x)
            cnt = cnt + 1
    if items.count() > 0:
        return render(request, 'home.html',
                      {'items': items, 'user': user, 'have_access_token': True, 'transactions': transactions})
    return render(request, 'home.html', {'user': user, 'have_access_token': False})


def loginview(request):
    return render(request, "login.html")


def signupview(request):
    return render(request, "signup.html")
