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
.. module:: base_recon
   :platform: Unix
   :synopsis: A base class for all reconstruction methods

.. moduleauthor:: Mark Basham <scientificsoftware@diamond.ac.uk>

"""
import logging
import math

from savu.plugins.plugin import Plugin
import numpy as np


class BaseRecon(Plugin):
    """
    A base class for reconstruction plugins

    :param center_of_rotation: Centre of rotation to use for the \
        reconstruction. Default: 0.0.
    :param in_datasets: Create a list of the dataset(s) to \
        process. Default: [].
    :param out_datasets: Create a list of the dataset(s) to \
        process. Default: [].
    :param init_vol: Dataset to use as volume initialiser. Default: None.
    :param sino_pad: Pad the sinogram to remove edge artefacts in the \
        reconstructed ROI (NB. This will increase the size of the data and \
        the time taken to perform the reconstruction). Default: False.
    :param log: Take the log of the data before reconstruction. Default: True.
    :param preview: A slice list of required frames. Default: [].
    """
    count = 0

    def __init__(self, name='BaseRecon'):
        super(BaseRecon, self).__init__(name)
        self.nOut = 1
        self.nIn = 1

    def base_dynamic_data_info(self):
        if self.parameters['init_vol']:
            self.nIn += 1
            self.parameters['in_datasets'].append(self.parameters['init_vol'])

    def base_pre_process(self):
        in_dataset = self.get_in_datasets()[0]
        in_pData, out_pData = self.get_plugin_datasets()
        self.pad_dim = \
            in_pData[0].get_data_dimension_by_axis_label('x', contains=True)
        in_meta_data = self.get_in_meta_data()[0]

        self.set_centre_of_rotation(in_dataset, in_meta_data, in_pData[0])
        self.exp.log(self.name + " End")
        self.vol_shape = out_pData[0].get_shape()
        self.main_dir = in_pData[0].get_pattern()['SINOGRAM']['main_dir']
        self.angles = in_meta_data.get_meta_data('rotation_angle')
        self.slice_dirs = out_pData[0].get_slice_directions()

        shape = in_pData[0].get_shape()
        pad_len = shape[self.pad_dim] if self.parameters['sino_pad'] else 0
        self.sino_pad = int(math.ceil((math.sqrt(2)-1)*pad_len))

        bases = [b.__name__ for b in self.__class__.__bases__]
        # pad the data now if the recon is not astra
        self.sino_func, self.cor_func = self.set_function(False) if \
            'NewBaseAstraRecon' in bases else self.set_function(shape)

    def set_centre_of_rotation(self, inData, mData, pData):
        try:
            cor = mData.get_meta_data("centre_of_rotation")
        except KeyError:
            cor = np.ones(inData.get_shape()[pData.get_slice_dimension()])
            cor *= self.parameters['center_of_rotation']
        self.cor = cor

    def set_function(self, pad_shape):
        if not pad_shape:
            cor_func = lambda cor: cor
            if self.parameters['log']:
                sino_func = lambda sino: -np.log(np.nan_to_num(sino)+1)
            else:
                sino_func = lambda sino: np.nan_to_num(sino)
        else:
            cor_func = lambda cor: cor+self.sino_pad
            pad_tuples = [(0, 0)]*(len(pad_shape)-1)
            pad_tuples.insert(self.pad_dim, (self.sino_pad, self.sino_pad))
            pad_tuples = tuple(pad_tuples)
            if self.parameters['log']:
                sino_func = lambda sino: -np.log(np.nan_to_num(
                    np.pad(sino, pad_tuples, 'edge'))+1)
            else:
                sino_func = lambda sino: np.nan_to_num(np.pad(
                    sino, pad_tuples, 'edge'))
        return sino_func, cor_func

    def process_frames(self, data, slice_list):
        """
        Reconstruct a single sinogram with the provided center of rotation
        """
        cor = self.cor[slice_list[0][self.main_dir]]
        init = data[1] if len(data) is 2 else None
        result = self.reconstruct(self.sino_func(data[0]), self.cor_func(cor),
                                  self.angles, self.vol_shape, init)
        return result

    def reconstruct(self, data, cor, angles, shape):
        """
        This is the main processing method for all plugins that inherit from
        base recon.  The plugin must implement this method.
        """
        logging.error("process needs to be implemented")
        raise NotImplementedError("process needs to be implemented")

    def setup(self):
        in_dataset, out_dataset = self.get_datasets()

        # reduce the data as per data_subset parameter
        in_dataset[0].get_preview().set_preview(self.parameters['preview'])

        # set information relating to the plugin data
        in_pData, out_pData = self.get_plugin_datasets()

        in_pData[0].plugin_data_setup('SINOGRAM', self.get_max_frames(),
                                      fixed=True)
        if len(in_pData) is 2:
            in_pData[1].plugin_data_setup('VOLUME_XZ', self.get_max_frames(),
                                          fixed=True)

        axis_labels = in_dataset[0].data_info.get_meta_data('axis_labels')[0]

        dim_volX, dim_volY, dim_volZ = \
            self.map_volume_dimensions(in_dataset[0], in_pData[0])

        axis_labels = [0]*3
        axis_labels = {in_dataset[0]:
                       [str(dim_volX) + '.voxel_x.voxels',
                        str(dim_volY) + '.voxel_y.voxels',
                        str(dim_volZ) + '.voxel_z.voxels']}

        shape = list(in_dataset[0].get_shape())
        shape[dim_volX] = shape[dim_volZ]
        
        out_dataset[0].create_dataset(axis_labels=axis_labels,
                                      shape=tuple(shape))

        out_dataset[0].add_volume_patterns(dim_volX, dim_volY, dim_volZ)

        # set pattern_name and nframes to process for all datasets
        out_pData[0].plugin_data_setup('VOLUME_XZ', self.get_max_frames(),
                                       fixed=True)
                                       

    def map_volume_dimensions(self, data, pData):
        data._finalise_patterns()
        dim_rotAngle = data.get_data_patterns()['PROJECTION']['main_dir']
        dim_detY = data.get_data_patterns()['SINOGRAM']['main_dir']

        core_dirs = pData.get_core_directions()
        dim_detX = list(set(core_dirs).difference(set((dim_rotAngle,))))[0]

        dim_volX = dim_rotAngle
        dim_volY = dim_detY
        dim_volZ = dim_detX
        return dim_volX, dim_volY, dim_volZ

    def get_max_frames(self):
        """
        Should be overridden to define the max number of frames to process at
        a time

        :returns:  an integer of the number of frames
        """
        return 8

    def nInput_datasets(self):
        return self.nIn

    def nOutput_datasets(self):
        return self.nOut

    def reconstruct_pre_process(self):
        """
        Should be overridden to perform pre-processing in a child class
        """
        pass

logging.debug("Completed base_recon import")
