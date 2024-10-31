#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

import netCDF4
import numpy as np
import json

# Ensemble size
nens = 20

# Open observations file
with netCDF4.Dataset("data/observations.nc", 'a', format="NETCDF4") as file:
  # Append hofx from members into observations file
  for iens in range(0, nens):
    print("Processing member: " + str(iens))
    with netCDF4.Dataset("data/member_hofx_obs_" + str(iens+1).zfill(6) + ".nc", 'r', format="NETCDF4") as memFile:
      # Read member's hofx
      memHofxVar = memFile["hofx"]["DSN_T_ISBA"][:]

    # Write into observations file
    hofxGrp = file.createGroup("hofx0_" + str(iens+1))
    hofxVar = hofxGrp.createVariable("DSN_T_ISBA", np.float32, ('Location'), fill_value=-3.368795e38)
    hofxVar[:] = memHofxVar

  # Append hofx from ensemble mean into observations file
  print("Processing mean")
  with netCDF4.Dataset("data/member_hofx_obs_000000.nc", 'r', format="NETCDF4") as memFile:
    # Read member's hofx
    meanHofxVar = memFile["hofx"]["DSN_T_ISBA"][:]

  # Write into observations file
  hofxGrp = file.createGroup("hofx_y_mean_xb0")
  hofxVar = hofxGrp.createVariable("DSN_T_ISBA", np.float32, ('Location'), fill_value=-3.368795e38)
  hofxVar[:] = meanHofxVar
