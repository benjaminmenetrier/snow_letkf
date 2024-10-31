#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

import os
import sys
from sys import exit
import netCDF4
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm
import matplotlib as mp
import numpy as np
import cartopy.crs as ccrs

# Ensemble size
nens = 20

# Read observations in NetCDF format, complying with IODA standard
with netCDF4.Dataset("data/observations.nc", 'r', format="NETCDF4") as file:
  # Get longitude / latitude
  obsLon = file["MetaData"]["longitude"][:]
  obsLat = file["MetaData"]["latitude"][:]

  # ObsValue group
  obsVal = file["ObsValue"]["DSN_T_ISBA"][:]

# Read grid
with netCDF4.Dataset("data/grid.nc", 'r') as file:
  gridLat = file.variables['lat'][:,:]
  gridLon = file.variables['lon'][:,:]

for iens in range(0, nens):
  print("Processing member: " + str(iens))

  # Read data
  with netCDF4.Dataset("data/member_hofx_" + str(iens).zfill(3) + ".nc", 'r', format="NETCDF4") as file:
    gridVal = file["DSN_T_ISBA"][0,:,:]
    fillValue = file["DSN_T_ISBA"]._FillValue

  # Levels
  vmin = 0.0
  vmax = max(np.max(obsVal), np.max(gridVal))
  levels = np.linspace(vmin, vmax, 101)

  # Plot
  ax = plt.axes(projection=ccrs.LambertConformal(central_longitude=26.0, central_latitude=70.0, standard_parallels=(70.0,70.0)))
  ax.coastlines(linewidth=0.5)
  ax.set_title('Total snow depth')
  ax.contourf(gridLon, gridLat, gridVal, cmap="viridis", levels=levels, transform=ccrs.PlateCarree())
  cmap = mp.colormaps['viridis']
  for i in range(0, len(obsVal)):
    obsVal_norm = (obsVal[i]-vmin)/(vmax-vmin)
    plt.plot(obsLon[i], obsLat[i], color=cmap(obsVal_norm), linewidth=0, markersize=8, marker='.', transform=ccrs.PlateCarree())
  plt.savefig('../fig/total_snow_depth_' + str(iens).zfill(3) + '.jpg', format='jpg', dpi=300)
  plt.close()
  os.system('mogrify -trim ../fig/total_snow_depth_' + str(iens).zfill(3) + '.jpg')
  exit()
