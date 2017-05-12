#!python
# coding: utf-8

import ipdb

import os
import sys
import shutil
import unittest
import subprocess
import yaml
import time

from config import *
from core.model import File, Pipeline, Job
from core.core import pirus


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# TEST PARAMETER / CONSTANTS
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #





class TestCoreLxdManager(unittest.TestCase):
    """ Test case for lxd container management. """

    IMAGE_FILE_PATH = "/var/regovar/pirus/_pipes/PirusTest.tar.xz"
    MAX_WAITING_4_INSTALL = 60 # 60s (actually, installing PirusSimple need ~45s)



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # PREPARATION
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @classmethod
    def setUpClass(self):
        pass
        

    @classmethod
    def tearDownClass(self):
        pass



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    # TESTS
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def test_000_pipeline_image_installation(self):
        """ Check that installation of the PirusSimpleContainer from local image file is working. """

        # install the fake pipeline
        p = pirus.pipelines.install_init_image_local(self.IMAGE_FILE_PATH, move=False, metadata={"type" : "lxd"})
        pirus.pipelines.install(p.id, asynch=False)  # install it synchronously to be able to test correctly
        TestCoreLxdManager.pid = p.id

        # waiting = self.MAX_WAITING_4_INSTALL
        # success = False
        # while waiting > 0:
        #     time.sleep(1)
        #     waiting -= 1
        #     if Pipeline.from_id(TestCoreLxdManager.pid).status == "ready":
        #         break;

        p = Pipeline.from_id(TestCoreLxdManager.pid, 1)
        self.assertEqual(p.status, "ready")
        self.assertEqual(os.path.isfile(self.IMAGE_FILE_PATH), True)
        self.assertNotEqual(self.IMAGE_FILE_PATH, p.image_file.path)



    def test_100_job_CRUD_normal_workflow(self):
        """ Check lxd job's normal worklow (without errors) """

        fake_config = {
            "name" : "job4test",
            "file1" : "",
            "duration" : 50,
            "crash" : False,
            "outfilename" : "result.txt"
        }



        # Create a new job
        job = pirus.jobs.new(TestCoreLxdManager.pid, fake_config, asynch=False)
        lxd_name = os.path.basename(job.root_path)
        self.assertEqual(job.status, "running")
        self.assertEqual(os.path.exists(job.root_path), True)
        self.assertEqual(os.path.exists(os.path.join(job.root_path, "inputs", "config.json")), True)
        self.assertEqual(os.path.exists(os.path.join(job.root_path, "logs", "out.log")), True)
        self.assertEqual(os.path.exists(os.path.join(job.root_path, "logs", "err.log")), True)
        self.assertEqual(lxd_name in exec_cmd(["lxc", "list"])[1], True)
        self.assertEqual("Status: Running" in exec_cmd(["lxc", "info", lxd_name])[1], True)
        # TODO check config.json : retrieve fake_config with the "job" key and a notification url in "pirus" key
        

        # monotoring when job is running
        job = pirus.jobs.monitoring(job.id)
        self.assertEqual(job.status, "running")
        self.assertEqual(isinstance(job.logs_moninitoring, dict), True)
        self.assertEqual('Memory (current)' in job.logs_moninitoring.keys(), True)
        self.assertEqual(job.logs_moninitoring['Status'], 'Running')
        self.assertEqual(job.logs_moninitoring['Name'], lxd_name)
        self.assertEqual(len(job.logs), 2)
        olog = job.logs[0]
        self.assertEqual(olog.name, "out.log")
        self.assertEqual(olog.head(1), "START Plugin de test\n")

        # pause the job
        pirus.jobs.pause(job.id, asynch=False)
        self.assertEqual(job.status, "pause")


        # monotoring when the job is paused
        job = pirus.jobs.monitoring(job.id)
        self.assertEqual(job.status, "pause")
        self.assertEqual(job.logs_moninitoring['Status'], 'Frozen')


        # restart the job
        pirus.jobs.start(job.id, asynch=False)
        job = Job.from_id(job.id)
        self.assertEqual(job.status, "running")
        self.assertEqual(job.logs_moninitoring['Status'], 'Running')


        # finalize the job
        pirus.jobs.finalize(job.id, asynch=False)
        job = Job.from_id(job.id)
        self.assertEqual(job.status, "done")
        # Todo check path for inputs, outputs, logs
        # Todo check output stored in database and file no more in outputs (just slinks)
        # Todo check log out/err
        job = pirus.jobs.monitoring(job.id)
        self.assertEqual(job.logs_moninitoring, {})



    def test_900_pipeline_image_deletion(self):
        # uninstall the pipeline
        p0 = Pipeline.from_id(TestCoreLxdManager.pid)
        pirus.pipelines.delete(p0.id, False)  # delete it synchronously to be able to test correctly

        # check that image file no more exists
        self.assertEqual(os.path.isfile(p0.image_file.path), False)
        f = File.from_id(p0.image_file_id)
        self.assertEqual(f, None)

        # check that pipeline no more exists
        self.assertEqual(os.path.exists(p0.root_path), False)
        p1 = Pipeline.from_id(p0.id)
        self.assertEqual(p1, None)

        # check that lxd image no more exists
        lxd_alias = yaml.load(p0.vm_settings)["lxd_alias"]
        r, o, e = exec_cmd(["lxc", "image", "list"])
        self.assertEqual(r, 0)
        self.assertEqual(lxd_alias in out, False)


