from decouple import config
from django.shortcuts import render

from console_main.views import login_required, track_page_visit, get_recent_services
from elastos_trinity.dapp_store import DAppStore
from django.db.models.expressions import RawSQL


@login_required
def dapp_store_dashboard(request):
    context = {}
    did = request.session['did']
    track_page_visit(did, 'elastOS dApp Store Dashboard',
                     'elastos_trinity:dapp_store_dashboard', False)
    context['recent_services'] = get_recent_services(did)
    dapp_store = DAppStore()
    dapps_list = dapp_store.get_apps_list()
    dapp_store_url = config('ELASTOS_TRINITY_DAPPSTORE_URL')
    for dapp in dapps_list:
        createdAt = dapp["createdAt"][:10]
        dapp["createdAt"] = createdAt
        id = dapp["_id"]
        dapp["id"] = id
        dapp["icon_url"] = f"{dapp_store_url}/apps/{id}/icon"
    context['dapps_list'] = dapps_list
    context['downloads'] = dapps_list
    context['downloads'] = sorted(
        context['downloads'], key=lambda k: k['downloadsCount'], reverse=True)[:4]
    return render(request, "elastos_trinity/dapp_store_dashboard.html", context)
