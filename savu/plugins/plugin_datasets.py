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
.. module:: plugin_datasets
   :platform: Unix
   :synopsis: Base class of plugin containing all dataset related functions

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""
import savu.plugins.plugin_datasets_notes as notes
from savu.core.utils import docstring_parameter
from savu.data.data_structures.plugin_data import PluginData


class PluginDatasets(object):
    """
    The base class from which all plugins should inherit.
    """

    def __init__(self):
        super(PluginDatasets, self).__init__()
        self.exp = None
        self.data_objs = {}
        self.variable_data_flag = False
        self.multi_params_dict = {}
        self.extra_dims = []

    def __get_data_objects(self, dtype):
        """ Get the data objects associated with the plugin from the experiment
        data index.

        :params str dtype: "in_data" or "out_data"
        :returns: A list of data objects with the names given in
            ``self.parameters``
        :rtype: list(Data)
        """
        data_list = self.parameters[dtype + 'sets']
        data_objs = []
        for data in data_list:
            data_objs.append(self.exp.index[dtype][data])
        return data_objs

    def __set_in_datasets(self):
        """ Set the in_data objects.

        :returns: the in_datasets associated with the plugin.
        :rtype: list[Data]
        """
        return self.__get_data_objects('in_data')

    def __set_out_datasets(self):
        """ Set the out_data objects.

        If the out_datasets do not exist inside the experiment then create
        them.

        :returns: the out_datasets associated with the plugin.
        :rtype: list[Data]
        """
        try:
            out_data = self.__get_data_objects('out_data')
        except KeyError:
            out_data = []
            for data in self.parameters['out_datasets']:
                self.exp.create_data_object("out_data", data)
            out_data = self.__get_data_objects('out_data')
        for data in out_data:
            data.extra_dims = self.extra_dims
        return out_data

    def _get_plugin_data(self, data_list):
        """ Encapsulate a PluginData object in each dataset associated with
        the plugin.

        :params list(Data) data_list: A list of Data objects used in a plugin.
        :returns: A list of PluginData objects.
        :rtype: list(PluginData)
        """
        pData_list = []
        for data in data_list:
            pData_list.append(PluginData(data, self))
            pData_list[-1].extra_dims = self.extra_dims
            pData_list[-1].multi_params_dict = self.multi_params_dict
        return pData_list

    def _set_plugin_datasets(self):
        """ Populate ``self.parameters`` in/out_datasets and
        plugin_in/out_datasets with the relevant objects (Data or PluginData).
        """
        self.parameters['in_datasets'] = self.__set_in_datasets()
        self.parameters['out_datasets'] = self.__set_out_datasets()
        self.parameters['plugin_in_datasets'] = \
            self._get_plugin_data(self.parameters['in_datasets'])
        self.parameters['plugin_out_datasets'] = \
            self._get_plugin_data(self.parameters['out_datasets'])

    @docstring_parameter('PluginData', 'in')
    @docstring_parameter(notes.datasets_notes.__doc__)
    def get_plugin_in_datasets(self):
        """ {0} """
        return self.parameters['plugin_in_datasets']

    @docstring_parameter('PluginData', 'out')
    @docstring_parameter(notes.datasets_notes.__doc__)
    def get_plugin_out_datasets(self):
        """ {0} """
        return self.parameters['plugin_out_datasets']

    @docstring_parameter("PluginData")
    @docstring_parameter(notes.two_datasets_notes.__doc__)
    def get_plugin_datasets(self):
        """ {0} """
        return self.get_plugin_in_datasets(), self.get_plugin_out_datasets()

    @docstring_parameter("Data", "in")
    @docstring_parameter(notes.datasets_notes.__doc__)
    def get_in_datasets(self):
        """ {0} """
        return self.parameters['in_datasets']

    @docstring_parameter("Data", "out")
    @docstring_parameter(notes.datasets_notes.__doc__)
    def get_out_datasets(self):
        """ {0} """
        return self.parameters['out_datasets']

    @docstring_parameter("PluginData")
    @docstring_parameter(notes.two_datasets_notes.__doc__)
    def get_datasets(self):
        """ {0} """
        return self.get_in_datasets(), self.get_out_datasets()

    @docstring_parameter("in")
    @docstring_parameter(notes.mData_notes.__doc__)
    def get_in_meta_data(self):
        """ {0} """
        return self.__set_meta_data(self.parameters['in_datasets'], 'in_data')

    @docstring_parameter("out")
    @docstring_parameter(notes.mData_notes.__doc__)
    def get_out_meta_data(self):
        """ {0} """
        return self.__set_meta_data(self.parameters['out_datasets'],
                                    'out_data')

    def get_meta_data(self):
        """ Get a list of meta_data objects associated with the
        in/out_datasets.

        :returns: All MetaData objects associated with out data objects.
        :rtype: list(MetaData(in_datasets)), list(MetaData(out_datasets))
        """
        return self.get_in_meta_data(), self.get_out_meta_data()

    def __set_meta_data(self, data_list, dtype):
        """ Append all MetaData objs associated with specified datasets to a
        list.

        :params list(Data) data_list:
        :returns: All MetaData objects associated with data objects in
            data_list
        :rtype: list(MetaData)
        """
        meta_data = []
        for data in data_list:
            meta_data.append(data.meta_data)
        return meta_data

    def _set_unknown_shape(self, data, key):
        try:
            return (len(data.meta_data.get_meta_data(key)),)
        except KeyError:
            return (0,)
