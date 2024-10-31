#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

import netCDF4
import numpy as np
import numpy.ma as ma

# Ensemble size
nens = 20

# Variables
cvNames = ["WSN_VEG12","RSN_VEG12","HSN_VEG12"]
hofxName = "DSN_T_ISBA"

# Open mean file
with netCDF4.Dataset("data/member_hofx_000000.nc", 'w', format="NETCDF4") as outputFileMean:
  for iens in range(0, nens):
    print("Processing member: " + str(iens))

    # Processing control variables
    print("- Control variables")
    with netCDF4.Dataset("data/member_cv_" + str(iens+1).zfill(6) + ".nc", 'w', format="NETCDF4") as outputFile:
      with netCDF4.Dataset("data/" + str(iens).zfill(3) + "/SURFOUT.nc", 'r', format="NETCDF4") as inputFile:
        init = False
        for cvName in cvNames:
          var = inputFile.variables[cvName][:,:,:]
          var = ma.filled(var, 0.0)
          fillValue = inputFile.variables[cvName]._FillValue
          npatch = np.shape(var)[0]
          for ipatch in range(0, npatch):
            patchName = cvName + "_" + str(ipatch+1)
            if not init:
              nx = outputFile.createDimension('nx', var.shape[2])
              ny = outputFile.createDimension('ny', var.shape[1])
              init = True
            nz = outputFile.createDimension('nz_' + patchName, 1)
            patchVar = outputFile.createVariable(patchName,np.float64,('nz_' + patchName,'ny','nx'), fill_value=fillValue)
            patchVar[0,:,:] = var[ipatch,:,:]

    # Processing hofx variable
    print("- Hofx variable")
    with netCDF4.Dataset("data/member_hofx_" + str(iens+1).zfill(6) + ".nc", 'w', format="NETCDF4") as outputFile:
      with netCDF4.Dataset("data/" + str(iens).zfill(3) + "/SURFOUT.20231204_06h00.nc", 'r', format="NETCDF4") as inputFile:
        var = inputFile.variables[hofxName][:,:]
        var = ma.filled(var, 0.0)
        fillValue = inputFile.variables[hofxName]._FillValue
        nx = outputFile.createDimension('nx', var.shape[1])
        ny = outputFile.createDimension('ny', var.shape[0])
        nz = outputFile.createDimension('nz_' + hofxName, 1)
        hofxVar = outputFile.createVariable(hofxName,np.float64,('nz_' + hofxName,'ny','nx'), fill_value=fillValue)
        hofxVar[0,:,:] = var
        if iens == 0:
          nxMean = outputFileMean.createDimension('nx', var.shape[1])
          nyMean = outputFileMean.createDimension('ny', var.shape[0])
          nzMean = outputFileMean.createDimension('nz_' + hofxName, 1)
          hofxVarMean = outputFileMean.createVariable(hofxName,np.float64,('nz_' + hofxName,'ny','nx'), fill_value=fillValue)
          hofxVarMean[0,:,:] = 0.0
        hofxVarMean[0,:,:] += var

  hofxVarMean[0,:,:] /= float(nens) 
