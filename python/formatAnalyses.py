#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

import netCDF4
import numpy as np
import numpy.ma as ma
import shutil

# Ensemble size
nens = 20

# Variables
cvNames = ["WSN_VEG12","RSN_VEG12","HSN_VEG12"]

for iens in range(0, nens):
  print("Processing member: " + str(iens))

  # Processing control variables
  with netCDF4.Dataset("data/member_letkf_" + str(iens+1).zfill(6) + ".nc", 'r', format="NETCDF4") as inputFile:
    shutil.copy2("data/" + str(iens).zfill(3) + "/SURFOUT.nc", "data/" + str(iens).zfill(3) + "/SURFOUT_ANALYSIS.nc")
    with netCDF4.Dataset("data/" + str(iens).zfill(3) + "/SURFOUT_ANALYSIS.nc", 'r+', format="NETCDF4") as outputFile:
      for cvName in cvNames:
        var = outputFile.variables[cvName][:,:,:]
        npatch = np.shape(var)[0]
        for ipatch in range(0, npatch):
          patchName = cvName + "_" + str(ipatch+1)
          patchVar = inputFile.variables[patchName]
          nx = var.shape[2]
          ny = var.shape[1]
          for ix in range(0, nx):
            for iy in range(0, nx):
              if not ma.is_masked(var[ipatch,iy,ix]):
                var[ipatch,iy,ix] = patchVar[0,iy,ix]
        outputFile.variables[cvName][:,:,:] = var
