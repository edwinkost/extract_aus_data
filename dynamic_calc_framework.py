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

    def __init__(self, cloneMapFileName,\
                       input_files, \
                       modelTime, \
                       output):
        DynamicModel.__init__(self)
        
        # set the clone map
        self.cloneMapFileName = cloneMapFileName
        pcr.setclone(self.cloneMapFileName)
        
        # time variable/object
        self.modelTime = modelTime
        
        # output folder 
        self.output = output
        
        # prepare temporary directory
        self.tmpDir = self.output['folder'] +"/tmp/"
        try:
            os.makedirs(self.tmpDir)
        except:
            os.system('rm -r /' + tmpDir + "/*")
        
        # input files
        self.input_files = input_files

        # object for reporting
        self.netcdf_report = OutputNetcdf(cloneMapFileName, self.output['netcdf_format'], self.output['netcdf_attributes'])       

        # make netcdf files for daily/monthly evaporation values:
        self.variable_name = "potential_evaporation"
        self.variable_unit = "m.day-1"               # This must be in daily average value
        # for daily values:
        for lc_type in ["forest", "grassland", "irrPaddy", "irrNonPaddy"]:
            file_name = self.output['folder'] + "/daily_potential_evaporation_" + self.variable_unit + "_" + lc_type + ".nc"
            self.netcdf_report.createNetCDF(file_name,\
                                            self.variable_name,\
                                            self.variable_unit,\
                                            self.variable_name)
        # for monthly values:
        for lc_type in ["forest", "grassland", "irrPaddy", "irrNonPaddy"]:
            file_name = self.output['folder'] + "/monthly_potential_evaporation_" + self.variable_unit + "_" + lc_type + ".nc"
            self.netcdf_report.createNetCDF(file_name,\
                                            self.variable_name,\
                                            self.variable_unit,\
                                            self.variable_name)
        
        # initiate acummulator variables for calculating monthly averages:
        self.monthly_accumulator = {}
        for lc_type in ["forest", "grassland", "irrPaddy", "irrNonPaddy"]:
            self.monthly_accumulator[lc_type] = pcr.scalar(0.0)

    def initial(self): 
        pass

    def dynamic(self):
        
        # re-calculate current model time using current pcraster timestep value
        self.modelTime.update(self.currentTimeStep())

        # open input data 
        referencePotET = vos.netcdf2PCRobjClone(\
                             self.input_files['referencePotET']['file_name'], \
                             self.input_files['referencePotET']['variable_name'], \
                             str(self.modelTime.fulldate), \
                             useDoy = None, \
                             cloneMapFileName = self.cloneMapFileName)
        cropKC = {}
        for lc_type in ["forest", "grassland", "irrPaddy", "irrNonPaddy"]:
            cropKC[lc_type] = vos.netcdf2PCRobjClone(\
                                  self.input_files['cropKC'][lc_type], \
                                  self.input_files['cropKC']['variable_name'], \
                                  str(self.modelTime.fulldate), 
                                  useDoy = None,
                                  cloneMapFileName = self.cloneMapFileName)
               
        # calculate
        potential_evaporation = {}
        for lc_type in ["forest", "grassland", "irrPaddy", "irrNonPaddy"]:
            potential_evaporation[lc_type] = referencePotET * cropKC[lc_type]
        
        # reporting for daily values
        timeStamp = datetime.datetime(self.modelTime.year,\
                                      self.modelTime.month,\
                                      self.modelTime.day,0)
        for lc_type in ["forest", "grassland", "irrPaddy", "irrNonPaddy"]:
            file_name = self.output['folder'] + "/daily_potential_evaporation_" + self.variable_unit + "_" + lc_type + ".nc"
            self.netcdf_report.data2NetCDF(file_name,\
                                           self.variable_name,\
                                           pcr.pcr2numpy(potential_evaporation[lc_type], vos.MV),\
                                           timeStamp)

        # reporting for monthly values
        # - reset at the beginning of the month:
        if self.modelTime.isFirstDayOfMonth:
            for lc_type in ["forest", "grassland", "irrPaddy", "irrNonPaddy"]:
                self.monthly_accumulator[lc_type] = pcr.scalar(0.0)
        # - accumulate until the last day of the month:
        for lc_type in ["forest", "grassland", "irrPaddy", "irrNonPaddy"]:
            self.monthly_accumulator[lc_type] = self.monthly_accumulator[lc_type] + potential_evaporation[lc_type]
        if self.modelTime.endMonth:
            for lc_type in ["forest", "grassland", "irrPaddy", "irrNonPaddy"]:
                file_name = self.output['folder'] + "/monthly_potential_evaporation_" + self.variable_unit + "_" + lc_type + ".nc"
                
                print file_name
                
                self.netcdf_report.data2NetCDF(file_name,\
                                               self.variable_name,\
                                               pcr.pcr2numpy(self.monthly_accumulator[lc_type]/calendar.monthrange(self.modelTime.year, self.modelTime.month)[1], vos.MV),\
                                               timeStamp)
