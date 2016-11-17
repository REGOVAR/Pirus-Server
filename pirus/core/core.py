#!env/python3
# coding: utf-8

import os
import json
import tarfile
import datetime
import time
import uuid
import subprocess

# from config import *
from core.framework import *
from core.model import *
from core.pirus_worker import start_run, terminate_run






# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# CORE OBJECT
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
class Core:
    def __init__(self):
        self.files = FileManager()
        self.pipelines= PipelineManager()
        self.runs = RunManager()

        # method handler for some spe
        self.notify_all_delegate = None


        # CHECK filesystem
        if not os.path.exists(RUNS_DIR):
            os.makedirs(RUNS_DIR)
        if not os.path.exists(PIPELINES_DIR):
            os.makedirs(PIPELINES_DIR)
        if not os.path.exists(FILES_DIR):
            os.makedirs(FILES_DIR)
        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)
        if not os.path.exists(DATABASES_DIR):
            os.makedirs(DATABASES_DIR)

        # CHECK consistensy between database and filesystem
        # Todo




    def set_notify_all(self, deletegate):
        self.notify_all_delegate = deletegate

    def notify_all(self, msg):
        if self.notify_all_delegate is not None:
            self.notify_all_delegate(msg)

    def init(self):
        """
            Do some verifications on the server to check that all is good.
             - check that config parameters are consistency
             - check that 
        """



 

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# FILE MANAGER
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
class FileManager:
    def __init__(self):
        pass



    def public_fields(self):
        return PirusFile.public_fields



    def total(self):
        return PirusFile.objects.count()



    def get(self, fields=None, query=None, order=None, offset=None, limit=None, sublvl=0):
        """
            Generic method to get files metadata according to provided filtering options
        """
        if fields is None:
            fields = PirusFile.public_fields
        if query is None:
            query = {}
        if order is None:
            order = ['-create_date', "name"]
        if offset is None:
            offset = 0
        if limit is None:
            limit = offset + RANGE_MAX
        return [f.export_client_data(sublvl, fields) for f in PirusFile.objects(__raw__=query).order_by(*order)[offset:limit]]



    def get_from_id(self, file_id, sublvl=0):
        file = PirusFile.from_id(file_id)
        if file == None:
            raise PirusException("No file with id " + str(file_id))
        return file.export_client_data(sublvl)
        
    

    def get_from_ids(self, file_ids, sublvl=0):
        return [f.export_client_data(sublvl) for f in PirusFile.from_id(file_ids)]



    def register(self, filename, path, metadata={}):
        """ 
            Create an entry for the file in the database and return the id of the file in pirus
            This method shall be used to init a resumable upload of a file 
            (the file is not yet available, but we need to manipulate its pirus metadata)
        """
        pirusfile = PirusFile()
        pirusfile.import_data({
                "name"          : filename,
                "type"          : os.path.splitext(filename)[1][1:].strip().lower(),
                "path"          : path,
                "size"          : int(os.path.getsize(path)),
                "status"        : "WAITING",
                "create_date"   : str(datetime.datetime.now().timestamp()),
                "md5sum"        : md5(fullpath)
            })
        pirusfile.import_data(metadata);
        pirusfile.save()
        plog.info('core.FileManager.register : New file registered with the id ' + str(pirusfile.id) + ' (available at ' + path + ')')
        return pirusfile.export_client_data()



    def edit(self, file_id, json_data):
        # TODO : implement PUT to edit file metadata (and remove the obsolete  "simple post" replaced by TUS upload )
        pass



    def delete(self, file_id):
        file = PirusFile.from_id(file_id)
        if file != None:
            shutil.rmtree(file.path)
            file.delete()


        








# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# PIPELINE MANAGER
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
class PipelineManager:
    def __init__(self):
        pass



    def public_fields(self):
        return Pipeline.public_fields



    def total(self):
        return Pipeline.objects.count()



    def get(self, fields=None, query=None, order=None, offset=None, limit=None, sublvl=0):
        """
            Generic method to get pipelines metadata according to provided filtering options
        """
        if fields is None:
            fields = Pipeline.public_fields
        if query is None:
            query = {}
        if order is None:
            order = ['-create_date', "name"]
        if offset is None:
            offset = 0
        if limit is None:
            limit = offset + RANGE_MAX
        return [p.export_client_data(sublvl, fields) for p in Pipeline.objects(__raw__=query).order_by(*order)[offset:limit]]



    def get_from_id(self, pipe_id, sublvl=0):
        pipe = Pipeline.from_id(pipe_id)
        if pipe == None:
            raise PirusException("No pipeline with id " + str(pipe_id))
        return pipe.export_client_data(sublvl)



    def get_from_ids(self, pipe_ids, sublvl=0):
        return [p.export_client_data(sublvl) for p in Pipeline.from_id(pipe_ids)]



    def register(self, fullpath, metadata={}):
        """ 
            Create an entry for the pipeline in the database and return the id of the pipeline in pirus
            This method shall be used to init a resumable upload of a pipeline 
            (the pipeline is not yet installed and available, but we need to manipulate its pirus metadata)
        """
        pipe = Pipeline()
        pipe.import_data({
                "name"          : fullpath,
                "pirus_api"     : "Unknow",
                "pipeline_file" : os.path.join(TEMP_DIR, str(uuid.uuid4())),
                "size"          : file_size,
                "upload_offset" : 0,
                "status"        : "WAITING"
            })
        pipe.import_data(metadata);
        pipe.save()
        return pipe.export_client_data()



    def edit(self, file_id, json_data):
        pipe = Pipeline.from_id(pipe_id)
        if pipe == None:
            raise PirusException("No pipeline with id " + str(pipe_id))
        pipe.import_data(metadata);
        pipe.save()
        return pipe.export_client_data()



    def delete(self, pipe_id, delete_also_run=False):
        try:
            pipe = Pipeline.from_id(pipe_id)
            if pipe != None:
                # Clean filesystem
                if pipe.root_path is not None:
                    shutil.rmtree(pipe.root_path)
                if os.path.exists(pipe.pipeline_file):
                    if os.path.isdir(pipe.pipeline_file):
                        shutil.rmtree(pipe.pipeline_file)
                    else:
                        os.unlink(pipe.pipeline_file)
                # Clean LXD
                if pipe.lxd_alias is not None:
                    try:
                        cmd = ["lxc", "image", "delete", pipe.lxd_alias]
                        out_tmp = '/tmp/' + pipe.lxd_alias + '-out'
                        err_tmp = '/tmp/' + pipe.lxd_alias + '-err'
                        subprocess.call(cmd, stdout=open(out_tmp, "r+"), stderr=open(err_tmp, "r+"))
                    except Exception as err:
                        plog.info('W: Unable to clean LXD for the pipe : ' + pipe.lxd_alias)
                # Clean DB
                pipe.delete()
        except Exception as error:
            # TODO : manage error
            raise PirusException("core.PipelineManager.delete : Unable to delete the pipeline with id " + str(pipe_id) + ". " + error.msg)
        return True



    def install(self, pipe_id):
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
        lxd_alias = LXD_IMAGE_PREFIX + lxd_alias
        metadata.update({
            "root_path"        : root_path,
            "lxd_inputs_path"  : metadata["inputs"],
            "lxd_outputs_path" : metadata["outputs"],
            "lxd_logs_path"    : metadata["logs"],
            "lxd_db_path"      : metadata["databases"],
            "lxd_run_cmd"      : metadata["run"],
            "form_file"        : form_file,
            "icon_file"        : icon_file,
            "lxd_alias"        : lxd_alias,
            "pipeline_file"    : pipeline_file,
            "size"             : pipeline.size,
            "upload_offset"    : pipeline.upload_offset,
            "status"           : "INSTALLING"
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

        pipeline.status = "READY"
        pipeline.save()
        return pipeline





# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# RUN MANAGER
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
class RunManager:
    def __init__(self):
        pass


        
    def public_fields(self):
        return Run.public_fields



    def total(self):
        return Run.objects.count()



    def get(self, fields=None, query=None, order=None, offset=None, limit=None, sublvl=0):
        """
            Generic method to get runs metadata according to provided filtering options
        """
        if fields is None:
            fields = Run.public_fields
        if query is None:
            query = {}
        if order is None:
            order = ['-create_date', "name"]
        if offset is None:
            offset = 0
        if limit is None:
            limit = offset + RANGE_MAX
        return [r.export_client_data(sublvl, fields) for r in Run.objects(__raw__=query).order_by(*order)[offset:limit]]



    def get_from_id(self, run_id, sublvl=0):
        run = Run.from_id(run_id)
        if run == None:
            raise PirusException("No run with id " + str(run_id))
        return run.export_client_data(sublvl)



    def get_from_ids(self, file_ids, sublvl=0):
        return [r.export_client_data(sublvl) for r in Run.from_id(file_ids)]



    def delete(self, request):
        run_id = request.match_info.get('run_id', -1)
        print ("DELETE run/<id=" + str(run_id) + ">")
        return web.Response(body=b"DELETE run/<id>")



    def create(self, pipeline_id, config_data, inputs_data):
        config_data = { "run" : config_data, "pirus" : { "notify_url" : ""}}
        pipeline = Pipeline.from_id(pipeline_id)
        if pipeline is None:
            # TODO : LOG rest_error("Unknow pipeline id " + str(pipeline_id))
            return None
        
        # Create run in database.
        lxd_container = LXD_CONTAINER_PREFIX + str(uuid.uuid4())

        run = Run()
        run.import_data({
            "pipeline_id" : pipeline_id,
            "name" : config_data["run"]["name"],
            "lxd_container" : lxd_container,
            "lxd_image" : pipeline.lxd_alias,
            "start" : str(datetime.datetime.now().timestamp()),
            "status" : "WAITING",
            "config" : json.dumps(config_data),
            "inputs" : inputs_data,
            "progress" : {"value" : 0, "label" : "0%", "message" : "", "min" : 0, "max" : 0}
        })
        run.save()

        run.url = 'http://' + HOSTNAME + '/dl/r/' + str(run.id)
        run.notify_url = 'http://' + HOSTNAME + '/run/notify/' + str(run.id)
        config_data = json.loads(run.config)
        config_data["pirus"]["notify_url"] = run.notify_url
        run.config = json.dumps(config_data)

        # Update input files to indicate that they will be used by this run
        for file_id in run.inputs:
            f = PirusFile.from_id(file_id)
            if f is None :
                # This file doesn't exists, so we will ignore it
                run.inputs.remove(file_id)
            elif run.id not in f.runs :
                f.runs.append(str(run.id))
                f.save()
        
        run.save()

        return run.export_client_data()



    def get_io(self, run_id):
        run = Run.from_id(run_id)
        if run == None:
            return rest_error("Unable to find the run with id " + str(run_id))
        result={"inputs" : [], "outputs":[]}
        # Retrieve inputs files data of the run
        files = PirusFile.from_ids(run.inputs)
        result["inputs"] = [a.export_client_data() for a in files]
        # Retrieve outputs files data of the run
        files = PirusFile.from_ids(run.outputs)
        result["outputs"] = [a.export_client_data() for a in files]
        return result



    def edit(self, run_id, json_data):
        run = Run.from_id(run_id)
        if run is not None:
            if "status" in json_data.keys():
                self.set_status(run, json_data["status"])
            run.import_data(json_data)
            run.save()
        return run.export_client_data()


    # Update the status of the run, and according to the new status will do specific action
    # Notify also every one via websocket that run status changed
    def set_status(self, run, new_status):
        # Avoid useless notification
        # Impossible to change state of a run in error or canceled
        if (new_status != "RUNNING" and run.status == new_status) or run.status in  ["ERROR", "CANCELED"]:
            return

        # Update status
        run.status = new_status
        run.save()

        #Need to do something according to the new status ?
        # Nothing to do for status : "WAITING", "INITIALIZING", "RUNNING", "FINISHING"
        if run.status in ["PAUSE", "ERROR", "DONE", "CANCELED"]:
            next_run = Run.objects(status="WAITING").order_by('start')
            if len(next_run) > 0:
                if next_run[0].status == "PAUSE":
                    start_run.delay(str(next_run[0].id))
                else :
                    start_run.delay(str(next_run[0].id))
        elif run.status == "FINISHING":
            terminate_run.delay(str(run.id))
        # Push notification
        msg = {"action":"run_changed", "data" : [run.export_client_data()] }
        pirus_core.notify_all(json.dumps(msg))



    def start(self, run_id):
        run = Run.from_id(run_id)
        if run == None:
            raise PirusException("Unable to find the run with id " + str(run_id))
        start_run.delay(run_id)


    def pause(self, run_id):
        run = Run.from_id(run_id)
        if run == None:
            raise PirusException("Unable to find the run with id " + str(run_id))
        if run.status in ["WAITING", "RUNNING"]:
            subprocess.Popen(["lxc", "pause", run.lxd_container])
            self.set_status(run, "PAUSE")
            return True, run.export_client_data()
        return False, run.export_client_data()


    def play(self, run_id):
        run = Run.from_id(run_id)
        if run == None:
            raise PirusException("Unable to find the run with id " + str(run_id))
        if run.status == "PAUSE":
            subprocess.Popen(["lxc", "start", run.lxd_container])
            self.set_status(run, "RUNNING")
            return True, run.export_client_data()
        return False, run.export_client_data()


    def stop(self, run_id):
        run = Run.from_id(run_id)
        if run == None:
            raise PirusException("Unable to find the run with id " + str(run_id))
        if run.status in ["WAITING", "PAUSE", "INITIALIZING", "RUNNING", "FINISHING"]:
            subprocess.Popen(["lxc", "delete", run.lxd_container, "--force"])
            self.set_status(run, "CANCELED")
            return True, run.export_client_data()
        return False, run.export_client_data()


    def monitoring(self, run_id):
        run = Run.from_id(run_id)
        if run == None:
            raise PirusException("Unable to find the run with id " + str(run_id))
        if run.status in ["INITIALIZING", "FINISHING", "ERROR", "DONE", "CANCELED"]:
            raise PirusException("No monitoring data for the run " + str(run_id))

        out = subprocess.check_output(["lxc", "info", run.lxd_container])
        result = {}
        for l in out.decode().split('\n'):
            data = l.split(': ')
            if data[0].strip() in ["Name","Created", "Status", "Processes", "Memory (current)", "Memory (peak)"]:
                result.update({data[0].strip(): data[1]})
                
        result.update({
            "out_tail" : subprocess.check_output(["tail", os.path.join(RUNS_DIR, run.lxd_container, "logs/out.log"), "-n", "100"]).decode(), 
            "err_tail" : subprocess.check_output(["tail", os.path.join(RUNS_DIR, run.lxd_container, "logs/err.log"), "-n", "100"]).decode()
        })
        return result




pirus = Core()