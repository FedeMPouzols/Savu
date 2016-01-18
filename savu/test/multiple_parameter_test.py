# -*- coding: utf-8 -*-
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
.. module:: plugins_test
   :platform: Unix
   :synopsis: unittest test classes for plugins

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import unittest

import savu.plugins.utils as pu
import savu.test.test_utils as tu


@unittest.skip('library error - use a different plugin for online tests')
class MultipleParameterTest(unittest.TestCase):

    def plugin_setup(self):
        ppath = 'savu.plugins.reconstructions.astra_recons.astra_recon_cpu'
        plugin = pu.load_plugin(ppath)
        return plugin

    def framework_options_setup(self):
        key1 = 'reconstruction_type'
        key2 = 'number_of_iterations'
        key3 = 'in_datasets'
        key4 = 'out_datasets'
        params = {key1: 'FBP;CGLS', key2: '1;2;3', key3: 'tomo', key4: 'tomo'}

        options = tu.set_experiment('tomo')
        plugin = 'savu.plugins.reconstructions.astra_recons.astra_recon_cpu'
        tu.set_plugin_list(options, plugin, [{}, params, {}])
        return options

    def test_parameter_space_int(self):
        plugin = self.plugin_setup()
        key = 'number_of_iterations'
        params = {key: '1;2;3'}
        plugin.set_parameters(params)
        params = plugin.parameters[key]
        self.assertEqual(params, [1, 2, 3])
        self.assertEqual(plugin.extra_dims[0], 3)

    def test_parameter_space_str(self):
        plugin = self.plugin_setup()
        key = 'reconstruction_type'
        params = {key: 'FBP;CGLS'}
        plugin.set_parameters(params)
        params = plugin.parameters[key]
        self.assertEqual(params, ['FBP', 'CGLS'])
        self.assertEqual(plugin.extra_dims[0], 2)

    def test_parameter_space_extra_dims(self):
        plugin = self.plugin_setup()
        key1 = 'reconstruction_type'
        key2 = 'number_of_iterations'
        params = {key1: 'FBP;CGLS', key2: '1;2;3'}
        plugin.set_parameters(params)
        out_datasets = plugin.get_out_datasets()
        for data in out_datasets:
            self.assertEqual(data.extra_dims, plugin.extra_dims)

    def test_parameter_space_data_shape(self):
        options = self.framework_options_setup()
        plugin = tu.plugin_runner_load_plugin(options)
        tu.plugin_setup(plugin)

        out_dataset = plugin.get_out_datasets()[0]
        self.assertEqual((160, 135, 160, 3, 2), out_dataset.get_shape())

    def test_parameter_space_full_run(self):
        options = self.framework_options_setup()
        tu.plugin_runner_real_plugin_run(options)


class MultipleParameterTest2(unittest.TestCase):

    def plugin_setup(self):
        ppath = 'savu.plugins.reconstructions.scikitimage_sart'
        plugin = pu.load_plugin(ppath)
        return plugin

    def framework_options_setup(self):
        key1 = 'interpolation'
        key2 = 'iterations'
        key3 = 'in_datasets'
        key4 = 'out_datasets'
        key5 = 'sino_pad_width'
        params = {key1: 'nearest;linear', key2: '1;2;3', key3: 'tomo',
                  key4: 'tomo', key5: 0}

        options = tu.set_experiment('tomo')
        plugin = 'savu.plugins.reconstructions.scikitimage_sart'
        tu.set_plugin_list(options, plugin, [{}, params, {}])
        return options

    def test_parameter_space_int(self):
        plugin = self.plugin_setup()
        key = 'iterations'
        params = {key: '1;2;3'}
        plugin.set_parameters(params)
        params = plugin.parameters[key]
        self.assertEqual(params, [1, 2, 3])
        self.assertEqual(plugin.extra_dims[0], 3)

    def test_parameter_space_str(self):
        plugin = self.plugin_setup()
        key = 'interpolation'
        params = {key: 'nearest;linear'}
        plugin.set_parameters(params)
        params = plugin.parameters[key]
        self.assertEqual(params, ['nearest', 'linear'])
        self.assertEqual(plugin.extra_dims[0], 2)

    def test_parameter_space_extra_dims(self):
        plugin = self.plugin_setup()
        key1 = 'interpolation'
        key2 = 'iterations'
        params = {key1: 'nearest;linear', key2: '1;2;3'}
        plugin.set_parameters(params)
        out_datasets = plugin.get_out_datasets()
        for data in out_datasets:
            self.assertEqual(data.extra_dims, plugin.extra_dims)

    def test_parameter_space_data_shape(self):
        options = self.framework_options_setup()
        plugin = tu.plugin_runner_load_plugin(options)
        tu.plugin_setup(plugin)

        out_dataset = plugin.get_out_datasets()[0]
        self.assertEqual((160, 135, 160, 3, 2), out_dataset.get_shape())

    def test_parameter_space_full_run(self):
        options = self.framework_options_setup()
        tu.plugin_runner_real_plugin_run(options)

if __name__ == "__main__":
    unittest.main()