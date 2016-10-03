#!env/python3
# coding: utf-8 
import time
import requests
import shutil
import requests
import logging
import json
import pylxd

from celery import Celery, Task
from pluginloader import PluginLoader


# CONFIG
from config import *






app = Celery('pirus_worker')
app.conf.update(
    BROKER_URL = 'amqp://guest@localhost',
    CELERY_RESULT_BACKEND = 'rpc',
    CELERY_RESULT_PERSISTENT = False,

    CELERY_TASK_SERIALIZER = 'json',
    CELERY_ACCEPT_CONTENT = ['json'],
    CELERY_RESULT_SERIALIZER = 'json',
    CELERY_INCLUDE = [
    'pirus_worker'
    ],
    CELERY_TIMEZONE = 'Europe/Paris',
    CELERY_ENABLE_UTC = True,
)



class PirusTask(Task):
    """Task that sends notification on completion."""
    abstract = True

    notify_url = ""
    run_path   = ""

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        #data = {'clientid': kwargs['clientid'], 'result': retval}
        #requests.get(NOTIFY_URL, data=data)
        pass

    def dump_context(self):
        print('  Context : Executing task id {0.id}, args: {0.args!r} kwargs: {0.kwargs!r}'.format(self.request))


    def notify_progress(self, completion:float, infos:str=None):
        data = { 
            "progress" : str(completion),
            "info" : infos
        }
        requests.get(self.notify_url + "/" + str(completion))
        print ("send notify progress : ", self.notify_url)

    def notify_status(self, status:str):
        requests.get(self.notify_url + "/status/" + status)
        print ("send notify status : ", self.notify_url + "/status/" + status)

    def log_msg(self, msg:str):
        path = os.path.join(self.run_path, "out.log")
        print ("OUT.LOG", time.ctime(), msg)
        pass

    def log_err(self, msg:str):
        path = os.path.join(self.run_path, "err.log")
        print ("ERR.LOG", time.ctime(), msg)
        pass





@app.task(base=PirusTask, queue='PirusQueue', bind=True)
def execute_plugin(self, fullpath, config):
    self.run_path   = os.path.join(RUN_DIR, str(self.request.id))
    self.notify_url = NOTIFY_URL + str(self.request.id)
    self.notify_status("INIT")
    # 1- Create pipeline run directory
    try:
        shutil.copytree(fullpath, self.run_path)
        self.log_msg("Pipeline running environment created.")
    except:
        self.log_err("Failed to create pipeline running environment.")
        self.notify_status("FAILED")
        return 1
    # 2- Load pipeline instance
    try:
        loader = PluginLoader()
        # FIXME TODO : being able to load whole directory as plugin (not only one py file)
        # plugins = loader.load_directory(path=self.run_path, recursive=True)
        loader.load_directory(path=self.run_path, recursive=True)
        pluginInstance = loader.plugins['PirusPlugin']()
        pluginInstance.notify  = self.notify_progress
        pluginInstance.log_msg = self.log_msg
        pluginInstance.log_err = self.log_err
    except:
        self.log_err("Failed to load the pipeline ands instanciate the run.")
        self.notify_status("FAILED")
        return 2
    # 3- Run !
    try:
        self.notify_status("RUN")
        self.log_msg("Pipeline run ! GO.")
        self.dump_context()
        pluginInstance.run(config)
    except Exception as error:
        self.log_err("The execution of the pipeline stopped and raised the following exception.\n" + repr(error))
        self.notify_status("ERROR")
        return 3
    # 4- Done
    self.log_msg("Pipeline run done.")
    self.notify_status("DONE")
    return 0



@app.task(base=PirusTask, queue='PirusQueue', bind=True)
def run_pipeline(self, run_id, config):
    self.run_id = str(self.request.id)
    self.run_path   = os.path.join(RUN_DIR, self.run_id)
    self.notify_url = NOTIFY_URL + str(self.request.id)
    lxd_client = pylxd.Client()


    # Check database, to see how many container are running and if we can create a new one for this run
    # TODO => STATE : WAITING SERVER DISPONIBILTY
    self.notify_status("Waiting server disponibility")
    while len(lxd_client.containers.all()) > 2:
        time.sleep(1)
	break # FIXME to remove 


    # Register job in database 
    # TODO => STATE : INITIALIZING (Db registration)
    self.notify_status("Init (Db registration)")

    # Create run's folders on the pirus server
    # TODO => STATE : INITIALIZING (Filesystem creation)
    runpath = os.path.join(RUNS_DIR, self.run_id)
    ipath = os.path.join(runpath, "inputs")
    opath = os.path.join(runpath, "outputs")
    lpath = os.path.join(runpath, "logs")
    rpath = os.path.join(runpath, "run")


    # Create lxd container and bind it on run repositories
    # TODO => STATE : INITIALIZING (LXC Container creation)
    c = lxd_client.container.get("pirus")
    c.devices.update(
        {
            'pirus_inputs': {'limits.write': '0iops', 'path': 'pipeline/inputs','source': ipath, 'type': 'disk'},
            'pirus_ouputs': {'path': 'pipeline/outputs','source': opath, 'type': 'disk'},
            'pirus_logs'  : {'path': 'pipeline/logs', 'source': lpath, 'type': 'disk'},
            'pirus_db'    : {'path': 'pipeline/db', 'source': DATABASES_DIR, 'type': 'disk'},
            'pirus_run'   : {'path': 'pipeline/run', 'source': rpath, 'type': 'disk'}
        })
    c.save()
    c.start()

    # Run the pipe !
    # TODO => STATE : RUNNING
    c.start()
    c.execute([rpath + "/run.sh"])

    # Stop container execution to release hdw resource
    # TODO => STATE : STOPING
    c.stop()

    # Delete container
    # TODO => STATE : DONE
    c.delete()



    # edit env variable of the lxc container with "well known" path for the pipeline
    #envfile = os.path.dirname(c_run.config_file_name) + "/rootfs/etc/environment"
    #os.chmod(envfile, 744)
    #with open( envfile, "a") as envfile:
    #    envfile.write("INPUTS_PATH = /home/ubuntu/run/inputs/\n")
    #    envfile.write("OUTPUTS_PATH = /home/ubuntu/run/outputs/\n")
    #    envfile.write("RUN_PATH = /home/ubuntu/run/\n")
    #    envfile.write("OUT_LOG = /home/ubuntu/run/logs/out.log\n")
    #    envfile.write("ERR_LOG = /home/ubuntu/run/logs/err.log\n")
    #    envfile.write("DB_PATH = /home/ubuntu/db/\n")
    #    envfile.write("NOTIFY_URL = " + str(socket.gethostbyname(socket.gethostname())) +  ":8080/run/" +  str(self.request.id) + "/\n")
    #os.chmod(envfile, 644)

    # run the container
    # c_run.start()

    # run the pipeline in the container :)
    # c_run.attach_wait(lxc.attach_run_command, ["/run_pipe.sh"])



