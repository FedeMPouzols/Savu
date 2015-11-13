# Copyright 2014 Diamond Light Source Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. module:: tomo_recon
   :platform: Unix
   :synopsis: runner for tests using the MPI framework

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import unittest
import tempfile
from savu.test import test_utils as tu

from savu.core.plugin_runner import PluginRunner


def run_protected_plugin_runner_no_process_list(options, plugin, **kwargs):
    try:
        if 'data' in kwargs.keys():
            tu.set_plugin_list(options, plugin, kwargs['data'])
        else:
            tu.set_plugin_list(options, plugin)
        plugin_runner = PluginRunner(options)
        plugin_runner.run_plugin_list(options)
    except ImportError as e:
        print("Failed to run test as libraries not available (%s)," % (e) +
              " passing test")
        pass


def run_protected_plugin_runner(options):
    try:
        plugin_runner = PluginRunner(options)
        plugin_runner.run_plugin_list(options)
    except ImportError as e:
        print("Failed to run test as libraries not available (%s)," % (e) +
              " passing test")
        pass


@unittest.skip("can't find calibration path")
class PluginRunnerMultiModalTest(unittest.TestCase):

    def test_process(self):
        options = {
            "transport": "hdf5",
            "process_names": "CPU0",
            "data_file": tu.get_test_data_path('mm.nxs'),
            "process_file": tu.get_test_process_path('MMtest.nxs'),
            "out_path": tempfile.mkdtemp()
            }
        run_protected_plugin_runner(options)


class PluginRunnerTomoTest(unittest.TestCase):

    def test_process(self):
        options = {
            "transport": "hdf5",
            "process_names": "CPU0",
            "data_file": tu.get_test_data_path('24737.nxs'),
            "process_file": tu.get_test_process_path('basic_tomo_process.nxs'),
            "out_path": tempfile.mkdtemp()
            }
        run_protected_plugin_runner(options)


class PluginRunnerSTXMTest(unittest.TestCase):

    def test_process(self):
        options = {
            "transport": "hdf5",
            "process_names": "CPU0",
            "data_file": tu.get_test_data_path('mm.nxs'),
            "process_file": tu.get_test_process_path('basic_stxm_process.nxs'),
            "out_path": tempfile.mkdtemp()
            }
        run_protected_plugin_runner(options)


@unittest.skip("can't find calibration path")
class PluginRunnerXRDTest(unittest.TestCase):

    def test_process(self):
        options = {
            "transport": "hdf5",
            "process_names": "CPU0",
            "data_file": tu.get_test_data_path('mm.nxs'),
            "process_file": tu.get_test_process_path('basic_xrd_process.nxs'),
            "out_path": tempfile.mkdtemp()
            }
        run_protected_plugin_runner(options)


class PluginRunnerFluoTest(unittest.TestCase):

    def test_process(self):
        options = {
            "transport": "hdf5",
            "process_names": "CPU0",
            "data_file": tu.get_test_data_path('mm.nxs'),
            "process_file": tu.get_test_process_path('basic_fluo_process.nxs'),
            "out_path": tempfile.mkdtemp()
            }
        run_protected_plugin_runner(options)


class PluginRunnerMonitorTest(unittest.TestCase):

    def test_process(self):
        options = {
            "transport": "hdf5",
            "process_names": "CPU0",
            "data_file": tu.get_test_data_path('mm.nxs'),
            "process_file": tu.get_test_process_path(
                'basic_monitor_process.nxs'),
            "out_path": tempfile.mkdtemp()
            }
        run_protected_plugin_runner(options)

if __name__ == "__main__":
    unittest.main()
