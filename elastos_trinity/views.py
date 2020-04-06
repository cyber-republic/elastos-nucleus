import json
import os
import requests
from decouple import config
from django.shortcuts import render
from django.http import HttpResponse
from console_main.views import login_required, track_page_visit, get_recent_services
from elastos_trinity.dapp_store import DAppStore

from .dapps_list import get_dapp_list, get_dapp_link, get_github_link, get_download_link, get_github_api_link


@login_required
def dapp_store_dashboard(request):
    context = {}
    did = request.session['did']
    track_page_visit(did, 'elastOS dApp Store Dashboard', 'elastos_trinity:dapp_store_dashboard', False)
    context['recent_services'] = get_recent_services(did)
    dapp_store = DAppStore()
    dapps_list = dapp_store.get_apps_list()
    dapp_store_url = config('ELASTOS_TRINITY_DAPPSTORE_URL')
    for dapp in dapps_list:
        id = dapp["_id"]
        dapp["id"] = id
        dapp["icon_url"] = f"{dapp_store_url}/apps/{id}/icon"
    context['dapps_list'] = dapps_list
    return render(request, "elastos_trinity/dapp_store_dashboard.html", context)

def dapp_templates(request):
    if request.method == "POST":
        context = {}
        name = request.POST.get('name')
        is_angular = False
        dapp_url = get_dapp_link(name)
        github_link = get_github_link(name)
        download_link = get_download_link(name)
        get_github_api_link(name)
        angular_check = dapp_url + "angular.json"
        try:
            angular_request = requests.get(angular_check)
            if int(angular_request.status_code) == 200:
                is_angular = True
            else:
                is_angular = False
        except Exception as e:
            print("error in angular_check")

        if is_angular:
            request_string = dapp_url + "src/assets/manifest.json"
        else:
            request_string = dapp_url + "public/assets/manifest.json"

        try:
            manifest = requests.get(request_string)
            json_dict = manifest.json()
        except:
            print("error in getting manifest files")

        logo_location = json_dict['icons'][1].get('src')
        if is_angular:
            logo_string = dapp_url + "src/" + logo_location
        else:
            logo_string = dapp_url + "public/" + logo_location

        readme_url = dapp_url + "README.md"
        readmehtml = ""
        try:
            readme = requests.get(readme_url)
            readme = readme.text
            headers = {
                "Content-Type": "text/plain"
            }
            readmehtml = requests.post('https://api.github.com/markdown/raw', headers=headers, data=readme)
            readmehtml = readmehtml.text
        except Exception as e:
            print("error in getting readmefile")

        github_data = get_github_api_link(name)
        try:
            github_dict = requests.get(github_data)
            github_dict = github_dict.json()
            created_at = get_date(github_dict['created_at'])
            updated_at = get_date(github_dict['updated_at'])
        except:
            print("error getting repo data")

        context['template'] = json_dict
        context['logo_url'] = logo_string
        context['github_link'] = github_link
        context['download_link'] = download_link
        context['version'] = json_dict['version']
        context['whitelisted_urls'] = json_dict['urls']
        context['plugins'] = json_dict['plugins']
        context['readme'] = readmehtml
        context['created_at'] = created_at
        context['updated_at'] = updated_at
        return render(request, 'elastos_trinity/daap_template_application.html', context)
    else:
        context = {}
        did = request.session['did']
        template_apps = get_dapp_list()
        jsonfiles = {"angular": [], "react": []}
        is_angular = False
        for items in template_apps:
            angular_check = items + "angular.json"
            print(angular_check)
            try:
                angular_request = requests.get(angular_check)
                if int(angular_request.status_code) == 200:
                    is_angular = True
                else:
                    is_angular = False
            except:
                print("error in angular_check")
                continue
            if is_angular:
                request_string = items + "src/assets/manifest.json"
            else:
                request_string = items + "public/assets/manifest.json"
            try:
                manifest = requests.get(request_string)
                json_dict = manifest.json()
                json_dict_1 = manifest.json()
                dapp_url = get_dapp_link(json_dict['name'])
                logo_location = json_dict['icons'][1].get('src')
                if is_angular:
                    logo_string = dapp_url + "src/" + logo_location
                else:
                    logo_string = dapp_url + "public/" + logo_location

                json_dict['logo_url'] = logo_string
                if is_angular:
                    jsonfiles["angular"].append(json_dict)
                else:
                    jsonfiles["react"].append(json_dict)
            except:
                print("error with manifest request")
                continue

        context['templates'] = jsonfiles
        context['recent_services'] = get_recent_services(did)
        return render(request, 'elastos_trinity/dapp_template.html', context)


def get_date(datetime):
    datetimelist = datetime.split('T')
    return datetimelist[0]
