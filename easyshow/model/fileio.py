# ######################################################################
# Copyright (c) 2015, Brookhaven Science Associates, Brookhaven        #
# National Laboratory. All rights reserved.                            #
#                                                                      #
# Redistribution and use in source and binary forms, with or without   #
# modification, are permitted provided that the following conditions   #
# are met:                                                             #
#                                                                      #
# * Redistributions of source code must retain the above copyright     #
#   notice, this list of conditions and the following disclaimer.      #
#                                                                      #
# * Redistributions in binary form must reproduce the above copyright  #
#   notice this list of conditions and the following disclaimer in     #
#   the documentation and/or other materials provided with the         #
#   distribution.                                                      #
#                                                                      #
# * Neither the name of the Brookhaven Science Associates, Brookhaven  #
#   National Laboratory nor the names of its contributors may be used  #
#   to endorse or promote products derived from this software without  #
#   specific prior written permission.                                 #
#                                                                      #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS  #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT    #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS    #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE       #
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,           #
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES   #
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR   #
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)   #
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,  #
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OTHERWISE) ARISING   #
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE   #
# POSSIBILITY OF SUCH DAMAGE.                                          #
########################################################################

from __future__ import (absolute_import, division,
                        print_function)

__author__ = 'Li Li'

import six
import sys
import h5py
import numpy as np
import os
from collections import OrderedDict
import pandas as pd
import json
import skimage.io as sio

from atom.api import Atom, Str, observe, Typed, Dict, List, Int, Enum, Float, Bool

import logging
logger = logging.getLogger(__name__)

try:
    from databroker.databroker import DataBroker as db, get_table
    # registers a filestore handler for the XSPRESS3 detector
    from hxntools import handlers as hxn_handlers
except ImportError as e:
    db = None
    logger.error('databroker and hxntools are not available: %s', e)


class FileIOModel(Atom):
    """
    This class focuses on file input and output.

    Attributes
    ----------
    working_directory : str
        current working path
    working_directory : str
        define where output files are saved
    file_names : list
        list of loaded files
    load_status : str
        Description of file loading status
    data_sets : dict
        dict of experiment data, 3D array
    img_dict : dict
        Dict of 2D arrays, such as 2D roi pv or fitted data
    """
    working_directory = Str()
    file_names = List()
    file_name = Str()
    file_path = Str()
    load_status = Str()
    data_sets = Typed(object)
    data_status = Dict()
    data_list = List()
    img_dict = Dict()

    file_channel_list = List()
    runid = Int(-1)
    h_num = Int(1)
    v_num = Int(1)
    fname_from_db = Str()

    def __init__(self, **kwargs):
        self.working_directory = kwargs['working_directory']

    @observe('file_names')
    def update_more_data(self, change):
        self.file_channel_list = []
        #self.file_names.sort()
        if change['type'] != 'create':
            logger.info('Files are loaded: %s' % (self.file_names))
            for fname in self.file_names:
                fpath = os.path.join(self.working_directory, fname)
                data_list = sorted(list(load_1d_data_keys(fpath)))
                data_list = ['None'] + data_list
                self.data_status[fname] = {v: False for v in data_list}
                self.data_status[fname]['None'] = True

    @observe('runid')
    def _update_fname(self, change):
        self.fname_from_db = 'scan_'+str(self.runid)+'.h5'

    def load_data_runid(self):
        """
        Load data according to runID number.

        requires databroker
        """
        if db is None:
            raise RuntimeError("databroker is not installed. This function "
                               "is disabled.  To install databroker, see "
                               "https://nsls-ii.github.io/install.html")
        if self.h_num != 0 and self.v_num != 0:
            datashape = [self.v_num, self.h_num]

        fname = self.fname_from_db
        fpath = os.path.join(self.working_directory, fname)
        config_file = os.path.join(self.working_directory, 'pv_config.json')
        db_to_hdf_config(fpath, self.runid,
                         datashape, config_file)
        self.file_names = [fname]

    @observe('file_name')
    def choose_file(self, change):
        # load mask data
        print(change)
        if len(change['value']) != 0:
            fpath = os.path.join(self.working_directory, self.file_name)
            self.data_sets = load_1d_data(fpath)
            self.data_list = ['None'] + sorted(list(self.data_sets.keys()))
            #self.data_status[self.file_name] = {v: False for v in self.data_list}


def load_1d_data(fpath):
    """ Read data from file and output dataframe.
    """
    return pd.read_csv(fpath)


def load_1d_data_keys(fpath):
    """ Read data keys only from input file.

    Parameters
    ----------
    fpath : str
        input file path

    Returns
    -------
    pandas.core.index.Index
    """
    dframe = pd.read_csv(fpath)
    return dframe.keys()
