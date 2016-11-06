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
        
        # use temporary folder as the working folder
        tmp_output_folder = self.output_files['tmp_output_folder']
        os.chdir(output_files['tmp_output_folder'])
        
        # set the clone map and set the catchment area
        # - convert tif to a pcraster map 
        input_tif_file    = self.input_files["tif_catchment_file"]
        cmd = 'cp ' + input_tif_file + " tmp.tif" 
        print(cmd); os.system(cmd)
        # - convert to a pcraster map 
        cmd = 'pcrcalc catchment.map = "nominal(tmp.tif)"'
        print(cmd); os.system(cmd)
        # - make sure that it has a good projection system
        cmd = 'mapattr -s -P yb2t catchment.map'
        print(cmd); os.system(cmd)
        # - set it as the clone and set it as the catchment map
        self.clone_map_file = "catchment.map"
        pcr.setclone(self.clone_map_file)
        # - and set it as the catchment map
        self.catchment = pcr.readmap("catchment.map")
        # - remove tif file
        cmd = 'rm -r tmp.tif'
        
        # calculate catchment area (m2)
        self.cell_area      = vos.readPCRmapClone(self.input_files['cellarea_0.05deg_file'], clone_map_file, tmp_output_folder)
        catchment_area_map  = pcr.areatotal(cell_area, catchment)
        self.catchment_area = float(pcr.cellvalue(catchment_area_map, 1))     # unit: m2
        
        # time variable/object
        self.modelTime = modelTime
        
        # output files
        
    def initial(self): 
        pass

    def dynamic(self):
        
        # re-calculate current model time using current pcraster timestep value
        self.modelTime.update(self.currentTimeStep())

        input_files["netcdf_runoff"]                  = {}
        input_files["netcdf_runoff"]["file_name"]     = "general_data/" + "e2o_univu_wrr1_glob30_day_Runoff_1979.nc"    # unit: kg m-2 s-1
        input_files["netcdf_runoff"]["variable_name"] = "Runoff"
        input_files["cellarea_0.05deg_file"]          = "general_data/" + "australia_cellsize0.05deg.map"	            # unit: m2 
        
        # runoff (from netcdf files, unit: kg m-2 s-1)
        self.runoff = vos.netcdf2PCRobjClone(self.input_files["netcdf_runoff"]["file_name"], \
                                             self.input_files["netcdf_runoff"]['variable_name'], \
                                             str(self.modelTime.fulldate), \
                                             useDoy = None, \
                                             cloneMapFileName = self.cloneMapFileName)
        # - use runoff value only within the catchment 
        
        
        # convert runoff to m3/day
                                             
        
        # total runoff within the catchment 
        self.total_runoff_within_the_catchment =  
        
        # write it to a txt file
        
