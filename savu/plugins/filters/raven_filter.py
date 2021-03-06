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
.. module:: raven_filter
   :platform: Unix
   :synopsis: A plugin remove ring artefacts

.. moduleauthor:: Nicola Wadeson <scientificsoftware@diamond.ac.uk>
"""
import logging
import numpy as np
import pyfftw

from savu.plugins.base_filter import BaseFilter
from savu.plugins.driver.cpu_plugin import CpuPlugin

from savu.plugins.utils import register_plugin


@register_plugin
class RavenFilter(BaseFilter, CpuPlugin):
    """
    Ring artefact removal method

    :param uvalue: To define the shape of filter. Default: 30.
    :param vvalue: How many rows to be applied the filter. Default: 1.
    :param nvalue: To define the shape of filter. Default: 8.
    :param padFT: Padding for Fourier transform. Default: 20.
    """

    def __init__(self):
        logging.debug("Starting Raven Filter")
        super(RavenFilter, self).__init__("RavenFilter")
        self.count=0

    def set_filter_padding(self, in_data, out_data):
        self.pad = self.parameters['padFT']
        # don't currently have functionality to pad top/bottom but not
        # right/left so padding everywhere for now
        in_data[0].padding = {'pad_frame_edges': self.pad}
        out_data[0].padding = {'pad_frame_edges': self.pad}

    def pre_process(self):
        in_pData = self.get_plugin_in_datasets()[0]
        sino_shape = in_pData.get_shape()

        width1 = sino_shape[1] + 2*self.pad
        height1 = sino_shape[0] + 2*self.pad

        v0 = np.abs(self.parameters['vvalue'])
        u0 = np.abs(self.parameters['uvalue'])
        n = np.abs(self.parameters['nvalue'])
        # Create filter
        centerx = np.ceil(width1/2.0)-1.0
        centery = np.int16(np.ceil(height1/2.0)-1)
        self.row1 = centery - v0
        self.row2 = centery + v0+1
        listx = np.arange(width1)-centerx
        filtershape = 1.0/(1.0 + np.power(listx/u0, 2*n))
        filtershapepad2d = np.zeros((self.row2 - self.row1, filtershape.size))
        filtershapepad2d[:] = np.float64(filtershape)
        self.filtercomplex = filtershapepad2d + filtershapepad2d*1j

        a = pyfftw.n_byte_align_empty((height1, width1), 16, 'complex128')
        self.fft_object = pyfftw.FFTW(a, a, axes=(0, 1))
        self.ifft_object = pyfftw.FFTW(a, a, axes=(0, 1),
                                       direction='FFTW_BACKWARD')

    def filter_frames(self, data):
        if(self.count%25==0):
           logging.debug( "raven...%i"%self.count)
        data2d = data[0]
        sino2 = np.fft.fftshift(self.fft_object(data2d))
        sino2[self.row1:self.row2] = \
            sino2[self.row1:self.row2] * self.filtercomplex
        sino3 = np.fft.ifftshift(sino2)
        sino4 = self.ifft_object(sino3).real
        sino4 = sino4[:, np.newaxis, :]
        self.count+=1
        return sino4

    def get_plugin_pattern(self):
        return 'SINOGRAM'

    def get_max_frames(self):
        return 1
