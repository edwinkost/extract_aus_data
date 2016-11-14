#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import shutil

# pcraster dynamic framework is used.
from pcraster.framework import DynamicFramework

# The calculation script (engine) is imported from the following module.
from dynamic_calc_framework import CalcFramework

# time object
from currTimeStep import ModelTime

# utility module:
import virtualOS as vos

import logging
logger = logging.getLogger(__name__)


# output
output_files = {}
# - output folder where you will store your output file
output_files['folder']          = "/scratch/edwin/tmp_test_for_nils/"
# - name of output file (txt file)
output_files['output_txt_file'] = output_files['folder'] + "003303.txt"

# input
input_files = {}
# - input folder where you store tif file 
input_files["folder"]                         = "/scratch/edwin/for_nils/data_from_nils/"
input_files["tif_catchment_file"]             = input_files["folder"] + "stID_003303.tif"

# general input data                          
input_files["netcdf_runoff"]                  = {}
# - netcdf input file for runoff
input_files["netcdf_runoff"]["file_name"]     = "/scratch/edwin/for_nils/general_data/e2o_univu_wrr1_glob30_day_Runoff_1979.nc"    # unit: kg m-2 s-1
input_files["netcdf_runoff"]["variable_name"] = "Runoff"

# start and end dates (based on input netcdf files)
startDate     = "1979-01-01"
endDate       = "1979-12-31" 

# prepare output folder
try:
    os.makedirs(output_files['folder'])
except:
    shutil.rmtree(output_files['folder'])
    pass

# temporary output folder:
output_files['tmp_output_folder'] = output_files['folder'] + "/tmp"
try:
    os.makedirs(output_files['tmp_output_folder'])
except:
    os.remove(output_files['tmp_output_folder'])
    pass

###########################################################################################################

def main():
    
    # time object
    modelTime = ModelTime() # timeStep info: year, month, day, doy, hour, etc
    modelTime.getStartEndTimeSteps(startDate, endDate)
    
    # - cell area (unit: m2) for every 0.05 arc-degree
    input_files["cellarea_0.05deg_file"] = "australia_cellsize0.05deg.map"	                         # unit: m2
    input_files["cellarea_0.05deg_file"] = os.path.abspath(input_files["cellarea_0.05deg_file"])

    # modeling framework
    calculationModel = CalcFramework(modelTime,\
                                     input_files, \
                                     output_files)

    dynamic_framework = DynamicFramework(calculationModel, modelTime.nrOfTimeSteps)
    dynamic_framework.setQuiet(True)
    dynamic_framework.run()

if __name__ == '__main__':
    sys.exit(main())
