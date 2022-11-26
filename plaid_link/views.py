from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid_django.settings import LOGIN_REDIRECT_URL
from .models import Item
import os
from django.views.decorators.csrf import csrf_exempt

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
    return jsonify({'public_token_exchange': 'complete'})


@csrf_exempt
def get_access_token(request):
    global access_token
    global item_id
    public_token = request.POST['public_token']

    try:
        p = PlaidCredential.objects.get(user=request.user)
        request.session["access_token"] = p.access_token
        return JsonResponse({'error': None, 'access_token': p.access_token})
    except PlaidCredential.DoesNotExist:
        pass

    try:
        exchange_response = client.Item.public_token.exchange(public_token)
    except plaid.errors.PlaidError as e:
        return JsonResponse(format_error(e))

    pretty_print_response(exchange_response)
    request.session["access_token"] = exchange_response['access_token']
    item_id = exchange_response['item_id']

    PlaidCredential.objects.create(user=request.user,
                                   access_token=exchange_response['access_token'],
    ).save()
    print("YESS1")
    return JsonResponse(exchange_response)

def pretty_print_response(response):
    print(json.dumps(response, indent=2, sort_keys=True))


@login_required(login_url=LOGIN_REDIRECT_URL)
def get_access_token(request):
    global access_token
    global item_id
    public_token = request.POST['public_token']
    print("YESS2")

    try:
        p = PlaidCredential.objects.get(user=request.user)
        request.session["access_token"] = p.access_token
        return JsonResponse({'error': None, 'access_token': p.access_token})
    except PlaidCredential.DoesNotExist:
        pass

    try:
        exchange_response = client.Item.public_token.exchange(public_token)
    except plaid.errors.PlaidError as e:
        return JsonResponse(format_error(e))

    pretty_print_response(exchange_response)
    request.session["access_token"] = exchange_response['access_token']
    item_id = exchange_response['item_id']

    PlaidCredential.objects.create(user=request.user,
                                   access_token=exchange_response['access_token'],
    ).save()

    return JsonResponse(exchange_response)

  
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
