#!env/python3
# coding: utf-8
import ipdb; 


import os
import sys
import time
import logging
import json
import yaml
import subprocess
import tarfile
import shutil

from mongoengine import *
from bson.objectid import ObjectId


from config import *
from framework import *


class PirusFile(Document):
    public_fields = ["id", "name", "type", "size", "status", "comments", "runs", "create_date", "tags", "md5sum", "url"]

    name          = StringField(required=True)
    type          = StringField()
    path          = StringField()
    size          = IntField() 
    upload_offset = IntField()
    status        = StringField() # UPLOADING, UPLOADED, PAUSE, ERROR, CHECKED
    comments      = StringField()    
    runs          = ListField(StringField())
    create_date   = StringField()
    tags          = ListField(StringField())
    md5sum        = StringField()


    def __str__(self):
        return self.name + " (" + self.size + ") : " + self.path


    def export_server_data(self):
        return {
            "name"          : self.name,
            "type"          : self.type,
            "path"          : self.path,
            "size"          : self.size,
            "upload_offset" : self.upload_offset,
            "status"        : self.status,
            "comments"      : self.comments,
            "runs"          : self.runs,
            "create_date"   : self.create_date,
            "tags"          : self.tags,
            "md5sum"        : self.md5sum,
            "id"            : str(self.id)
        }

    def url(self):
        return "http://" + HOSTNAME + "/dl/f/" + str(self.id)
    def upload_url(self):
        return "http://" + HOSTNAME + "/file/upload/" + str(self.id)

    def export_client_data(self, fields=None):
        result = {}
        if fields is None:
            fields = PirusFile.public_fields

        for k in fields:
            if k == "id":
                result.update({"id" : str(self.id)})
            elif k == "url":
                result.update({"url" : self.url()})
            else:
                result.update({k : eval("self."+k)})
        return result


    def import_data(self, data):
        try:
            self.name          = data['name']
            self.type          = data["type"]
            self.path          = data['path']
            self.size          = int(data["size"])
            self.status        = data["status"]
            self.create_date   = data["create_date"]
            if "md5sum" in data.keys():
                self.md5sum = data["md5sum"]
            if "runs" in data.keys():
                self.runs = data["runs"]
            if "upload_offset" in data.keys():
                self.upload_offset = int(data["upload_offset"])
            else:
                self.upload_offset = 0
            if "tags" in data.keys():
                self.tags = data['tags']
            if "comments" in data.keys():
                self.comments  = data["comments"]
        except KeyError as e:
            raise ValidationError('Invalid input file: missing ' + e.args[0])
        return self


    @staticmethod
    def from_id(id):
        if not ObjectId.is_valid(id):
            return None;
        file = PirusFile.objects.get(pk=id)
        return file

    @staticmethod
    def remove(id):
        file = PirusFile.from_id(id)
        if file != None:
            shutil.rmtree(file.path)
            file.delete()







class Pipeline(Document):
    # Static
    public_fields    = ["name", "description", "version", "pirus_api", "license", "developers", "size", "upload_offset", "status", "id"]
    # Metadata
    name             = StringField(required=True)
    description      = StringField()
    version          = StringField()
    pirus_api        = StringField(required=True)
    license          = StringField()
    developers       = ListField(StringField())
    # Upload data
    size             = IntField(required=True)
    upload_offset    = IntField(required=True)
    status           = StringField(required=True) # UPLOADING, PAUSE, ERROR, INSTALLING, READY
    # Internal data (run deployment)
    pipeline_file    = StringField(required=True)
    root_path        = StringField()
    lxd_alias        = StringField()
    lxd_inputs_path  = StringField()
    lxd_outputs_path = StringField()
    lxd_logs_path    = StringField()
    lxd_db_path      = StringField()
    lxd_run_cmd      = StringField()
    form_file        = StringField()
    icon_file        = StringField()

    def __str__(self):
        return self.pipeline_file

    def url(self):
        return "http://" + HOSTNAME + "/dl/p/" + str(self.id)
    def upload_url(self):
        return "http://" + HOSTNAME + "/pipeline/upload/" + str(self.id)

    def export_server_data(self):
        return {
            "id"               : str(self.id),
            "name"             : self.name,
            "description"      : self.description,
            "version"          : self.version,
            "pirus_api"        : self.pirus_api,
            "license"          : self.license,
            "developers"       : self.developers,
            "size"             : self.size,
            "upload_offset"    : self.upload_offset,
            "status"           : self.status,
            "pipeline_file"    : self.pipeline_file,
            "root_path"        : self.root_path,
            "lxd_alias"        : self.lxd_alias,
            "lxd_inputs_path"  : self.lxd_inputs_path,
            "lxd_outputs_path" : self.lxd_outputs_path,
            "lxd_logs_path"    : self.lxd_logs_path,
            "lxd_db_path"      : self.lxd_db_path,
            "lxd_run_cmd"      : self.lxd_run_cmd,
            "form_file"        : self.form_file,
            "icon_file"        : self.icon_file
        }


    def export_client_data(self, fields=None):
        result = {}
        if fields is None:
            fields = Pipeline.public_fields

        for k in fields:
            if k == "id":
                result.update({"id" : str(self.id)})
            elif k == "form_url":
                result.update({"form_url" : "http://" + HOSTNAME + "/pipeline/" + str(self.id) + "/form.json"})
            elif k == "icon_url":
                result.update({"icon" : "http://" + HOSTNAME + "/pipeline/" + str(self.id) + "/" + os.path.basename(self.icon_file)})
            else:
                result.update({k : eval("self."+k)})
        return result


    def import_data(self, data):
        try:
            # Required fields
            self.name           = data['name']
            self.pirus_api      = data["pirus_api"]
            self.size           = int(data["size"])
            self.upload_offset  = int(data["upload_offset"])
            self.status         = data["status"]
            self.pipeline_file  = data["pipeline_file"]
            # Optional fields
            if "description" in data.keys():
                self.description = data["description"]
            if "version" in data.keys():
                self.version = data['version']
            if "license" in data.keys():
                self.license = data["license"]
            if "developers" in data.keys():
                self.developers  = data["developers"]
            if "root_path" in data.keys():
                self.root_path = data['root_path']
            if "lxd_alias" in data.keys():
                self.lxd_alias = data['lxd_alias']
            if "lxd_inputs_path" in data.keys():
                self.lxd_inputs_path = data['lxd_inputs_path']
            if "lxd_outputs_path" in data.keys():
                self.lxd_outputs_path = data['lxd_outputs_path']
            if "lxd_logs_path" in data.keys():
                self.lxd_logs_path = data['lxd_logs_path']
            if "lxd_db_path" in data.keys():
                self.lxd_db_path = data['lxd_db_path']
            if "lxd_run_cmd" in data.keys():
                self.lxd_run_cmd = data['lxd_run_cmd']
            if "form_file" in data.keys():
                self.form_file = data['form_file']
            if "icon_file" in data.keys():
                self.icon_file = data['icon_file']
        except KeyError as e:
            raise ValidationError('Invalid pipeline: missing ' + e.args[0])
        return self


    @staticmethod
    def from_id(pipe_id):
        if not ObjectId.is_valid(pipe_id):
            return None;
        pipe = Pipeline.objects.get(pk=pipe_id)
        return pipe


    @staticmethod
    def remove(pipe_id):
        pipe = Pipeline.from_id(pipe_id)
        if pipe != None:
            shutil.rmtree(pipe.root_path)
            pipe.delete()


    @staticmethod
    def install(pipe_id):

        pipeline = Pipeline.from_id(pipe_id)
        if pipeline == None or pipeline.size != pipeline.upload_offset or pipeline.status != "UPLOADING":
            return None


        lxd_alias     = str(uuid.uuid4())
        root_path     = os.path.join(PIPELINES_DIR, lxd_alias)
        old_file      = pipeline.pipeline_file
        pipeline_file = os.path.join(root_path, pipeline.name)

        # 1- Copy file into final folder
        plog.info('I: Installation of the pipeline package : ' + root_path)
        os.makedirs(root_path)
        os.rename(old_file, pipeline_file)
        os.chmod(pipeline_file, 0o777)

        # 2- Extract pipeline metadata
        # TODO : instead of testing import json then yaml, loading only yaml should be enough. to be tested
        try:
            tar = tarfile.open(pipeline_file)
            tar_data = [info for info in tar.getmembers() if info.name == "metadata.yaml"]
            metadata = tar.extractfile(member=tar_data[0])
            metadata = metadata.read()
            try:
                # try json ?
                metadata = json.loads(metadata.decode())
            except:
                # try yaml ?
                metadata = yaml.load(metadata)
            metadata = metadata["pirus"]
        except:
            # TODO : manage error + remove package file
            plog.info('E:    [FAILLED] Extraction of ' + pipeline_file)
            raise PirusException("XXXX", "Unable to extract package. Corrupted file or wrong format")
        plog.info('I:    [OK     ] Extraction of metadata from ' + pipeline_file)

        # 2- Check that mandatory fields exists
        missing = ""
        for k in MANIFEST["mandatory"].keys():
            if k not in metadata.keys():
                missing += k + ", "                
        if missing != "":
            missing = missing[:-2]
            plog.info('E:    [FAILLED] Checking validity of metadata (missing : ' + missing + ")")
            raise PirusException("XXXX", "Bad pirus pipeline format. Mandory fields missing in the metadata : " + missing)
        plog.info('I:    [OK     ] Checking validity of metadata')

        # 3- Default value for optional fields in mandatory file
        for k in MANIFEST["default"].keys():
            if k not in metadata.keys():
                metadata[k] = MANIFEST["default"][k]

        # 4- Extract pirus technicals files from the tar file
        try:
            if metadata["form"] is not None:
                source     = os.path.join("rootfs",metadata['form'][1:] if metadata['form'][0]=="/" else metadata['form'])
                tar_data   = [info for info in tar.getmembers() if info.name == source]
                file       = tar.extractfile(member=tar_data[0])
                source     = os.path.join(root_path, source)
                form_file  = os.path.join(root_path, "form.json")
                with open(form_file, 'bw+') as f:
                    f.write(file.read())
            else :
                form_file = os.path.join(root_path, "form.json")
                with open(form_file, 'w+') as f:
                    f.write("{}")

            source = PIPELINE_DEFAULT_ICON_PATH
            icon_file = os.path.join(root_path, "icon.png")
            if metadata["icon"] is not None:
                source = os.path.join("rootfs",metadata['icon'][1:] if metadata['icon'][0]=="/" else metadata['icon'])
                tar_data = [info for info in tar.getmembers() if info.name == source]
                file = tar.extractfile(member=tar_data[0])
                source = os.path.join(root_path, source)
                icon_file = os.path.join(root_path, os.path.basename(metadata['icon']))
                with open(icon_file, 'bw+') as f:
                    f.write(file.read())
            else:
                shutil.copyfile(source, icon_file)
        except:
            # TODO : manage error + remove package file
            plog.info('E:    [FAILLED] Extraction of ' + pipeline_file)
            raise PirusException("XXXX", "Error occure during extraction of pipeline technical files (form.json / icon)")
        plog.info('I:    [OK     ] Extraction of pipeline technical files (form.json / icon)')


        # 5- Save pipeline into database
        metadata.update({
            "root_path"        : root_path,
            "lxd_inputs_path"  : metadata["inputs"],
            "lxd_outputs_path" : metadata["outputs"],
            "lxd_logs_path"    : metadata["logs"],
            "lxd_db_path"      : metadata["databases"],
            "lxd_run_cmd"      : metadata["run"],
            "form_file"        : form_file,
            "logo_file"        : icon_file,
            "lxd_alias"        : "pirus-pipe-" + lxd_alias,
            "pipeline_file"    : pipeline_file
        })
        try:
            pipeline.import_data(metadata)
            pipeline.save()
        except Exception as err:
            # TODO : manage error
            print(err)
            plog.info('E:    [FAILLED] Save pipeline information in database.')
            raise PirusException("XXXX", "Failed to save pipeling info into the database.")
        plog.info('I:    [OK     ] Save pipeline information in database with id='+ str(pipeline.id))

        # 6- Install lxd container
        cmd = ["lxc", "image", "import", pipeline_file, "--alias", lxd_alias]
        try:
            out_tmp = '/tmp/' + lxd_alias + '-out'
            err_tmp = '/tmp/' + lxd_alias + '-err'
            subprocess.call(cmd, stdout=open(out_tmp, "w"), stderr=open(err_tmp, "w"))

        except Exception as err:
            # TODO : manage error
            print(err)
            plog.info('E:    [FAILLED] Installation of the lxd image. ($: ' + " ".join(cmd) + ")")
            raise PirusException("XXXX", "Failed to install pipeline lxd image.")


        err = open(err_tmp, "r").read()
        if err != "":
            # TODO : manage error
            plog.info('E:    [FAILLED] Lxd image. ($: ' + " ".join(cmd) + ")")
            plog.info('--------------------------')
            plog.info(err)
            plog.info('--------------------------')
            pipeline.delete()
            shutil.rmtree(root_path)
            raise PirusException("XXXX", "Failed to install pipeline lxd image (" + err + ")")
        else:
            plog.info('I:    [OK     ] Installation of the lxd image.')

        # 7- Clean directory
        try:
            keep = [pipeline_file, form_file, icon_file]
            for f in os.listdir(root_path):
                fullpath = os.path.join(root_path, f)
                if fullpath not in keep:
                    if os.path.isfile(fullpath):
                        os.remove(fullpath)
                    else:
                        shutil.rmtree(fullpath)
        except Exception as err:
            # TODO : manage error, notify only admins
            print(err)
            plog.info('E:    [FAILLED] Cleaning repository.')
        plog.info('I:    [OK     ] Cleaning repository.')
        plog.info('I:    All fine. Pipeline is ready !')
        return pipeline
        
















class Run(Document):
    public_fields = ["id", "pipe_id", "name", "config", "start", "end", "status", "inputs", "outputs", "progress"]

    pipe_id    = ObjectIdField(required=True)
    private_id = StringField(required=True)   # = private_id
    name       = StringField(requiered=True)
    config     = DynamicField(required=True)
    start      = StringField(required=True)
    end        = StringField()
    status     = StringField()  # WAITING, PAUSE, INITIALIZING, RUNNING, FINISHING, ERROR, DONE, CANCELED
    inputs     = ListField(StringField())
    outputs    = StringField()
    progress   = DynamicField(required=True)

    def __str__(self):
        return str(self.id)


    def export_server_data(self):
        return {
            "id"        : str(self.id),
            "pipe_id"   : str(self.pipe_id),
            "private_id" : self.private_id,
            "name"      : self.name,
            "config"    : self.config,
            "start"     : self.start,
            "end"       : self.end,
            "status"    : self.status,
            "inputs"    : self.inputs,
            "outputs"   : self.outputs,
            "progress"  : self.progress
        }


    def export_client_data(self, fields=None):
        result = {}
        if fields is None:
            fields = Run.public_fields

        for k in fields:
            if k == "id":
                result.update({"id" : str(self.id)})
            elif k == "pipe_id":
                result.update({"pipe_id" : str(self.pipe_id)})
            else:
                result.update({k : eval("self."+k)})
        return result


    def import_data(self, data):
        try:
            self.pipe_id   = data['pipe_id']
            self.private_id = data['private_id']
            self.name      = data['name']
            self.config    = data['config']
            self.start     = data['start']
            self.status    = data['status']
            self.progress  = data['progress']
            if "end" in data:
                self.end = data['end']
            if "inputs" in data:
                self.inputs = data["inputs"]
            if "outputs" in data:
                self.outputs = data["outputs"]
        except KeyError as e:
            raise ValidationError('Invalid plugin: missing ' + e.args[0])
        return self 

    @staticmethod
    def from_id(run_id):
        if not ObjectId.is_valid(run_id):
            return None;
        run = Run.objects.get(pk=run_id)
        return run

    @staticmethod
    def from_private_id(run_id):
        run = Run.objects.get(private_id=run_id)
        return run