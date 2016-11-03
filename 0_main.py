#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

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

# file name of the clone map defining the scope of output
cloneMapFileName = "/scratch/chinmay/IGB_Data/clone_and_landmask_IGB/clone_igbmntb.map"

# input
input_files = {}
input_files['referencePotET']                  = {}
input_files['referencePotET']['file_name']     = "/data/hydroworld/forcing/CRU-TS3.21/merged_1958_to_2010/CRU-TS3.21_ERA-40_ERA-Interim_daily_referencePotET_1958_to_2010.nc"
input_files['referencePotET']['variable_name'] = "referencePotET"
input_files['cropKC'] = {}           
input_files['cropKC']['variable_name'] = "kc"
input_files['cropKC']['forest']        = "/storagetemp/chinmay/test/newextent_lai_05.04.2016/forest_newextent_crop_factors.nc"
input_files['cropKC']['grassland']     = "/storagetemp/chinmay/test/newextent_lai_05.04.2016/grassland_newextent_crop_factors.nc"
input_files['cropKC']['irrPaddy']      = "/storagetemp/chinmay/test/newextent_lai_05.04.2016/paddy_newextent_crop_factors.nc"
input_files['cropKC']['irrNonPaddy']   = "/storagetemp/chinmay/test/newextent_lai_05.04.2016/nonpaddy_newextent_crop_factors.nc"

# output
output = {}
output['folder']            = "/scratch/edwin/tmp/"
output['netcdf_format']     = "NETCDF3_CLASSIC"
output['netcdf_attributes'] = {}
output['netcdf_attributes']['institution']  = "Department of Physical Geography, Utrecht University"
output['netcdf_attributes']['title'      ]  = "Potential evaporation estimates  "
output['netcdf_attributes']['source'     ]  = "None"
output['netcdf_attributes']['history'    ]  = "None"
output['netcdf_attributes']['references' ]  = "None"
output['netcdf_attributes']['comment'    ]  = "None"

# prepare the output directory
try:
    os.makedirs(output['folder'])
except:
    os.system('rm -r ' + output['folder'])
    pass

startDate     = "2001-01-01" # YYYY-MM-DD
endDate       = "2007-12-31" 

###########################################################################################################

def main():
    
    # prepare logger and its directory
    log_file_location = output['folder'] + "/log/"
    try:
        os.makedirs(log_file_location)
    except:
        pass
    vos.initialize_logging(log_file_location)
    
    # time object
    modelTime = ModelTime() # timeStep info: year, month, day, doy, hour, etc
    modelTime.getStartEndTimeSteps(startDate, endDate)
    
    calculationModel = CalcFramework(cloneMapFileName,\
                                     input_files, \
                                     modelTime, \
                                     output)

    dynamic_framework = DynamicFramework(calculationModel, modelTime.nrOfTimeSteps)
    dynamic_framework.setQuiet(True)
    dynamic_framework.run()

if __name__ == '__main__':
    sys.exit(main())
