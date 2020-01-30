import json
import logging
import os
import secrets
from binascii import unhexlify
from datetime import timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import F
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse

from decouple import config
from django.utils import timezone
from django.db import models
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt
from fastecdsa import curve, ecdsa
from fastecdsa.encoding.sec1 import SEC1Encoder

from login.tokens import account_activation_token
from .models import TrackUserPageVisits
from login.models import DIDUser, DIDRequest
from service.models import UserServiceSessionVars
from .settings import MEDIA_ROOT


def login_required(function):
    def wrapper(request, *args, **kw):
        if not request.session.get('logged_in'):
            return redirect(reverse('landing'))
        return function(request, *args, **kw)

    wrapper.__doc__ = function.__doc__
    wrapper.__name__ = function.__name__
    return wrapper


def privacy_policy_pdf(request):
    try:
        return FileResponse(open(os.path.join(MEDIA_ROOT, 'nucleus_privacy_policy.pdf'), 'rb'),
                            content_type='application/pdf')
    except FileNotFoundError:
        raise Http404('not found')


@csrf_exempt
def did_callback(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        if request.content_type == "application/json" or 'Data' not in response.keys():
            HttpResponse(status=400)
        data = json.loads(response['Data'])
        sig = response['Sign']
        client_public_key = data['PublicKey']

        r, s = int(sig[:64], 16), int(sig[64:], 16)
        public_key = SEC1Encoder.decode_public_key(unhexlify(client_public_key), curve.P256)
        valid = ecdsa.verify((r, s), response['Data'], public_key)
        if not valid:
            return JsonResponse({'message': 'Unauthorized'}, status=401)
        try:
            recently_created_time = timezone.now() - timedelta(minutes=1)
            did_request_query_result = DIDRequest.objects.get(state=data["RandomNumber"],
                                                              created_at__gte=recently_created_time)
            if not did_request_query_result:
                return JsonResponse({'message': 'Unauthorized'}, status=401)
            data["auth"] = True
            DIDRequest.objects.filter(state=data["RandomNumber"]).update(data=json.dumps(data))
        except Exception as e:
            logging.debug(f" Method: did_callback Error: {e}")
            JsonResponse({'error': str(e)}, status=404)

    return JsonResponse({'result': True}, status=200)


def check_ela_auth(request):
    if 'elaState' not in request.session.keys():
        return JsonResponse({'authenticated': False}, status=403)
    state = request.session['elaState']
    try:
        recently_created_time = timezone.now() - timedelta(minutes=1)
        did_request_query_result = DIDRequest.objects.get(state=state, created_at__gte=recently_created_time)
        data = json.loads(did_request_query_result.data)
        if not data["auth"]:
            return JsonResponse({'authenticated': False}, status=403)
        request.session['name'] = data['Nickname']
        request.session['email'] = data['Email']
        request.session['did'] = data['DID']
        if DIDUser.objects.filter(did=data["DID"]).exists() is False:
            redirect_url = "/login/register"
            request.session['redirect_success'] = True
        else:
            user = DIDUser.objects.get(did=data["DID"])
            request.session['name'] = user.name
            request.session['email'] = user.email
            request.session['did'] = user.did
            if user.is_active is False:
                redirect_url = "/"
                send_email(request, user.email, user)
                messages.success(request,
                                 "The email '%s' needs to be verified. Please check your email for confirmation link" % user.email)
            else:
                redirect_url = "/login/feed"
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                request.session['logged_in'] = True
                populate_session_vars_from_database(request, request.session['did'])
                messages.success(request, "Logged in successfully!")
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'redirect': redirect_url}, status=200)


def send_email(request, to_email, user):
    current_site = get_current_site(request)
    mail_subject = 'Activate your Nucleus Console account'
    message = render_to_string('login/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.did)),
        'token': account_activation_token.make_token(user),
    })
    email = EmailMessage(
        mail_subject, message, from_email='"Nucleus Console Support Team" <support@nucleusconsole.com>', to=[to_email]
    )
    email.content_subtype = 'html'

    try:
        email.send()
        return HttpResponse("Success")
    except Exception as e:
        logging.debug(f"Method: send_email Error: {e}")
        return HttpResponse("Failure")


def landing(request):
    did_login = config('DIDLOGIN', default=False, cast=bool)
    recent_services = None
    if not did_login:
        email = config('SUPERUSER_USER')
        try:
            user = DIDUser.objects.get(email=email)
        except(TypeError, ValueError, OverflowError, DIDUser.DoesNotExist):
            user = DIDUser()
            user.email = email
        user.name = "Test User"
        user.set_password(config('SUPERUSER_PASSWORD'))
        user.did = "test"
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        request.session['name'] = user.name
        request.session['email'] = user.email
        request.session['did'] = user.did
        request.session['logged_in'] = True
        populate_session_vars_from_database(request, user.did)
        recent_services = get_recent_services(user.did)
    else:
        public_key = config('ELA_PUBLIC_KEY')
        did = config('ELA_DID')
        app_id = config('ELA_APP_ID')
        app_name = config('ELA_APP_NAME')

        random = secrets.randbelow(999999999999)
        request.session['elaState'] = random

        url_params = {
            'CallbackUrl': config('APP_URL') + '/did_callback',
            'Description': 'Elastos DID Authentication',
            'AppID': app_id,
            'PublicKey': public_key,
            'DID': did,
            'RandomNumber': random,
            'AppName': app_name,
            'RequestInfo': 'Nickname,Email'
        }

        elephant_url = 'elaphant://identity?' + urlencode(url_params)

        # Save token to the database didauth_requests
        token = {'state': random, 'data': {'auth': False}}

        DIDRequest.objects.create(state=token['state'], data=json.dumps(token['data']))
        # Purge old requests for housekeeping. If the time denoted by 'created_by'
        # is more than 2 minutes old, delete the row
        stale_time = timezone.now() - timedelta(minutes=2)
        DIDRequest.objects.filter(created_at__lte=stale_time).delete()

        request.session['elephant_url'] = elephant_url
    return render(request, 'landing.html', {'recent_services': recent_services})


def populate_session_vars_from_database(request, did):
    api_key = ''

    mnemonic_mainchain = ''
    private_key_mainchain = ''
    public_key_mainchain = ''
    address_mainchain = ''

    private_key_did = ''
    public_key_did = ''
    address_did = ''
    did_did = ''

    address_eth = ''
    private_key_eth = ''
    if UserServiceSessionVars.objects.filter(did=did):
        obj = UserServiceSessionVars.objects.get(did=did)
        api_key = obj.api_key

        mnemonic_mainchain = obj.mnemonic_mainchain
        private_key_mainchain = obj.private_key_mainchain
        public_key_mainchain = obj.public_key_mainchain
        address_mainchain = obj.address_mainchain

        private_key_did = obj.private_key_did
        public_key_did = obj.public_key_did
        address_did = obj.address_did
        did_did = obj.did_did

        address_eth = obj.address_eth
        private_key_eth = obj.private_key_eth
    request.session['api_key'] = api_key

    request.session['mnemonic_mainchain'] = mnemonic_mainchain
    request.session['private_key_mainchain'] = private_key_mainchain
    request.session['public_key_mainchain'] = public_key_mainchain
    request.session['address_mainchain'] = address_mainchain

    request.session['private_key_did'] = private_key_did
    request.session['public_key_did'] = public_key_did
    request.session['address_did'] = address_did
    request.session['did_did'] = did_did

    request.session['address_eth'] = address_eth
    request.session['private_key_eth'] = private_key_eth


def track_page_visit(did, name, view, is_service):
    try:
        track_obj = TrackUserPageVisits.objects.get(did=did, name=name, view=view, is_service=is_service)
        track_obj.name = name
        track_obj.view = view
        track_obj.last_visited = timezone.now()
        track_obj.number_visits = F('number_visits') + 1
        track_obj.is_service = is_service
        track_obj.save()
    except models.ObjectDoesNotExist:
        track_obj = TrackUserPageVisits.objects.create(did=did, name=name, view=view, number_visits=1, is_service=is_service)
        track_obj.save()
    except Exception as e:
        logging.debug(e)


def get_recent_services(did):
    recent_services = TrackUserPageVisits.objects.filter(did=did, is_service=True).order_by('-last_visited')[:5]
    return recent_services












