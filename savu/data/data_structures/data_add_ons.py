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
.. module:: data_additions
   :platform: Unix
   :synopsis: A module containing add_on classes, which have instances \
       encapsulated within the Data class.

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>

"""

import logging
import warnings

import savu.data.data_structures.data_notes as notes
from savu.core.utils import docstring_parameter


class Padding(object):
    """ A class that organises padding of the data. An instance of Padding can
    be associated with a Data object in a plugin that inherits from BaseFilter,
    inside :meth:`savu.plugins.base_filter.BaseFilter.set_filter_padding`
    """

    def __init__(self, pattern):
        self.padding_dirs = {}
        self.pad_dict = None
        self.pattern_name = pattern.keys()[0]
        self.pattern = pattern[self.pattern_name]
        self.dims = self.__set_dims()

    def __set_dims(self):
        dims = []
        for key in self.pattern.keys():
            temp = self.pattern[key]
            for dim in (temp,) if isinstance(temp, int) else temp:
                dims.append(int(dim))
        dims = list(set(dims))
        for dim in dims:
            self.padding_dirs[dim] = {'before': 0, 'after': 0}
        return dims

    def pad_frame_edges(self, padding):
        """ Pad all the edges of a frame of data with the same pad amount
        (i.e pad in the core dimensions).

        :param int padding: The pad amount
        """
        core_dirs = self.pattern['core_dir']
        for core in core_dirs:
            self._pad_direction(str(core) + '.' + str(padding))

    def pad_multi_frames(self, padding):
        """ Add extra frames before and after the current frame of data (i.e
        pad in the fastest changing slice dimension).

        :param int padding: The pad amount
        """
        try:
            main_dir = self.pattern['main_dir']
        except KeyError:
            raise Exception('There is no main_dir associated with this '
                            'pattern')
        self._pad_direction(str(main_dir) + '.' + str(padding))

    @docstring_parameter(notes._padding.__doc__)
    def pad_directions(self, pad_list):
        """ Pad multiple, individually specified, dimensions.

        :param list(dict) pad_list: A list of strings of the form: {0}.
        """
        for entry in pad_list:
            self.__pad_direction(entry)

    @docstring_parameter(notes._padding.__doc__)
    def _pad_direction(self, pad_str):
        """ Pad the data in a specified dimension.

        :param str pad_str: {0}.
        """
        pad_vals = pad_str.split('.')
        pplace = None
        pad_place = ['before', 'after']
        if len(pad_vals) is 3:
            pdir, pplace, pval = pad_vals
            remove = list(set(pad_place).difference(set([pplace])))[0]
            pad_place.remove(remove)
        else:
            pdir, pval = pad_vals

        pdir = int(pdir)
        if pdir not in self.dims:
            warnings.warn('Dimension '+str(pdir)+' is not associated with the '
                          'pattern ' + self.pattern_name + '. IGNORING!')
        else:
            for p in pad_place:
                self.padding_dirs[pdir][p] += int(pval)

    def _get_padding_directions(self):
        """ Get padding directions.

        :returns: padding dictionary
        :rtype: dict
        """
        for key in self.padding_dirs.keys():
            if sum(self.padding_dirs[key].values()) is 0:
                del self.padding_dirs[key]
        return self.padding_dirs


class DataMapping(object):
    """ A class providing helper functions to multi-modal loaders.
    """

    def __init__(self):
        self._is_tomo = None
        self._is_map = None
        self._motors = None
        self._motor_type = None
        self._axes = None

    def set_motors(self, motors):
        self.motors = motors

    def get_motors(self):
        return self.motors

    def set_motor_type(self, motor_type):
        self.motor_type = motor_type

    def get_motor_type(self):
        return self.motor_type

    def set_axes(self, axes):
        self.axes = axes

    def get_axes(self):
        return self.axes

    def check_is_map(self, proj_dir):
        pattern = []
        if self.get_meta_data("is_map"):
            ovs = []
            for i in self.get_shape():
                if i != proj_dir[0]:
                    if i != proj_dir[1]:
                        ovs.append(i)
            pattern = {"PROJECTION", {'core_dir': proj_dir, 'slice_dir': ovs}}
        return pattern

    def check_is_tomo(self, proj_dir, rotation):
        pattern = []
        if self.get_meta_data("is_tomo"):
            ovs = []
            for i in self.get_shape():
                if i != rotation:
                    if i != proj_dir[1]:
                        ovs.append(i)
            pattern = {"SINOGRAM", {'core_dir': (rotation, proj_dir[-1]),
                                    'slice_dir': ovs}}
        return pattern
