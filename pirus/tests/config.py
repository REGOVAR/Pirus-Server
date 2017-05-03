#!env/python3
# coding: utf-8 
import os

# HOST (internal)
HOST           = "127.0.0.1"
PORT           = "8200"
VERSION        = "v1"
HOSTNAME       = HOST + ":" + PORT + "/" + VERSION

# HOST (public)
HOST_P         = HOSTNAME

RANGE_DEFAULT = 20
RANGE_MAX     = 1000

# DB
DATABASE_NAME = "pirus_test"



# FILESYSTEM
FILES_DIR     = "/var/regovar/pirus/files"
TEMP_DIR      = "/var/regovar/pirus/downloads"
DATABASES_DIR = "/var/regovar/pirus/databases"
PIPELINES_DIR = "/var/regovar/pirus/pipelines"
RUNS_DIR      = "/var/regovar/pirus/runs"


# AUTOCOMPUTED VALUES
PIRUS_DIR      = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR   = os.path.join(PIRUS_DIR, "api_rest/templates/")
ERROR_ROOT_URL = "api.pirus.org/errorcode/"
NOTIFY_URL     = "http://" + HOST_P + "/run/notify/"


# LXD
PIRUS_UID      = 1000
PIRUS_GID      = PIRUS_UID
LXD_UID        = 165537
LXD_GID        = LXD_UID
LXD_MAX        = 2
LXD_CONTAINER_PREFIX  = "pirus-run-"
LXD_IMAGE_PREFIX      = "pirus-pipe-"
LXD_HDW_CONF = {
    "CPU"  : None,
    "CORE" : None,
    "RAM"  : None,
    "DISK" : None
}


# MANIFEST fields in the pirus pipeline package
MANIFEST = {
    "mandatory" : {
        "name"        : "The displayed name of the pirus pipeline", 
        "run"         : "The command line that will executed by pirus to run the pipeline.", 
    },
    "default" : {
        "pirus_api"   : VERSION,               # The version of the pirus api used by the pipeline
        "inputs"      : "/pipeline/inputs",    # The absolute path in the pipeline lxd container to the directory where input files have to be mount.
        "outputs"     : "/pipeline/outputs",   # The absolute path in the pipeline lxd container to the directory where output files will be write.
        "logs"        : "/pipeline/logs",      # The absolute path in the pipeline lxd container to the directory where logs files will be write. Note that out.log, err.log and pirus.log will be automatically created in this directory.
        "databases"   : "/pipeline/databases", # The absolute path in the pipeline lxd container to the directory where common databases have to be mount.
        "form"        : None,                  # The absolute path in the pipeline lxd container to the json file use to describe the form that will be used by the user to configure the run.
        "icon"          : None,                  # The absolute path in the pipeline lxd container to the icon of the pipe.
    }
}


PIPELINE_DEFAULT_ICON_PATH = os.path.join(TEMPLATE_DIR , "pipeline_icon.png")