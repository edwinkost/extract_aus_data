#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import calendar

import pcraster as pcr
from pcraster.framework import DynamicModel

from outputNetcdf import OutputNetcdf
import virtualOS as vos

import logging
logger = logging.getLogger(__name__)

class CalcFramework(DynamicModel):

    def __init__(self, modelTime, \
                       input_files, \
                       output_files):
        DynamicModel.__init__(self)
        
        self.input_files  = input_files
        self.output_files = output_files
        
        # use cell area as the clone map
        self.clone_map_file = self.input_files["cellarea_0.05deg_file"]
        pcr.setclone( self.clone_map_file)
        self.x_min = pcr.clone().west()
        self.y_min = pcr.clone().north() - pcr.clone().nrRows() * pcr.clone().cellSize()
        self.x_max = pcr.clone().west()  + pcr.clone().nrCols() * pcr.clone().cellSize() 
        self.y_max = pcr.clone().north()

        # change working directory to the temporary output folder
        os.chdir(self.output_files['tmp_output_folder')
        
        # resample tif to the extent of the clone  
        input_tif_file    = self.input_files["tif_catchment_file"]
        cmd = 'gdalwarp -te 122 -44 155 -10 ' + input_tif_file + " tmp.tif" 
        print(cmd); os.system(cmd)
        # - convert to a pcraster map 
        cmd = 'pcrcalc catchment.map = "nominal(tmp.tif)"'
        print(cmd); os.system(cmd)
        # - make sure that it has a good projection system
        cmd = 'mapattr -s -P yb2t catchment.map'
        # - set it as the catchment and landmask maps
        self.catchment = pcr.readmap("catchment.map")
        self.landmask  = pcr.defined(self.catchment)
        
        # calculate catchment area (m2)
        self.cell_area      = vos.readPCRmapClone(self.input_files['cellarea_0.05deg_file'], self.clone_map_file, self.output_files['tmp_output_folder')
        catchment_area_map  = pcr.ifthen(self.landmask, self.cell_area)
        pcr.aguila(catchment_area_map)
        self.catchment_area = vos.getMapTotal(catchment_area_map)       # unit: m2
        
        print_to_screen = 'The catchment area is (m2):' + self.catchment_area 
        print(print_to_screen)
        
        # time variable/object
        self.modelTime = modelTime
        
    def initial(self): 
        pass

    def dynamic(self):
        
        # re-calculate current model time using current pcraster timestep value
        self.modelTime.update(self.currentTimeStep())

        # runoff (from netcdf files, unit: kg m-2 s-1)
        self.runoff = vos.netcdf2PCRobjClone(self.input_files["netcdf_runoff"]["file_name"], \
                                             self.input_files["netcdf_runoff"]['variable_name'], \
                                             str(self.modelTime.fulldate), \
                                             useDoy = None, \
                                             cloneMapFileName = self.clone_map_file)
        # - use runoff value only within the catchment 
        self.runoff = pcr.ifthen(self.landmask, self.runoff)
        
        # convert runoff to m3/day and direction 
        self.runoff = self.runoff * 1000. * self.cell_area * 86400. * -1.0
        
        # average runoff (mm/day) within the catchment 
        average_runoff_within_the_catchment =  vos.getMapTotal(self.runoff) / (1000. * self.catchment_area)
        
        print_to_screen = 'Average runoff within the catchment (mm/day) for the date'  + str(self.modelTime.fulldate) + " : " + str(average_runoff_within_the_catchment) 
        print(print_to_screen)

        # write it to a txt file
