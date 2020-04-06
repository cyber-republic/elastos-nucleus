dapp_dict = {
    "angular hello world": "https://raw.githubusercontent.com/Ashwin-Pokharel/dappangularhelloworld/master/",
    "react hello world": "https://raw.githubusercontent.com/Ashwin-Pokharel/dappreacthelloworld/master/",
}

def get_dapp_list():
    dapp_list = []
    for key, val in dapp_dict.items():
        dapp_list.append(val)
    return dapp_list


def get_dapp_link(name):
    name = name.lower()
    name = name.strip()
    return dapp_dict.get(name)


def get_github_link(name):
    github_base = 'https://github.com/'
    raw_list = get_dapp_link(name)
    raw_list = raw_list.split('/')
    raw_list = raw_list[3:6]
    raw_list = raw_list[:-1]
    for i in range(0, len(raw_list)):
        raw_list[i] = raw_list[i] + "/"
    for i in raw_list:
        github_base += i
    return github_base

def get_github_api_link(name):
    github_api = "https://api.github.com/repos/"
    raw_list = get_dapp_link(name).split('/')
    raw_list = raw_list[3:5]
    for i in range(0, len(raw_list)-1):
        raw_list[i] = raw_list[i] + "/"
    for i in raw_list:
        github_api += i
    return github_api


def get_download_link(name):
    github_base = 'https://github.com/'
    raw_list = get_dapp_link(name)
    raw_list = raw_list.split('/')
    branch = raw_list[5]
    raw_list = raw_list[3:6]
    raw_list = raw_list[:-1]
    for i in range(0, len(raw_list)):
        raw_list[i] = raw_list[i] + "/"
    for i in raw_list:
        github_base += i
    github_base += "archive/" + branch + ".zip"
    return github_base


def add_template_app(name , url):
    name = name.lower()
    name = name.strip()
    dapp_dict[name] = url