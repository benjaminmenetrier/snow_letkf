#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

import netCDF4
import numpy as np
import json
from scipy.spatial import KDTree
from sklearn.metrics import pairwise_distances

def lonLatOroToXYZ(lon, lat, oro, req):
  lonRad = np.radians(lon)
  latRad = np.radians(lat)
  XYZ = np.zeros((3))
  XYZ[0] = (req+oro)*np.cos(lonRad)*np.cos(latRad)
  XYZ[1] = (req+oro)*np.sin(lonRad)*np.cos(latRad)
  XYZ[2] = (req+oro)*np.sin(latRad)
  return XYZ

# Earth radius
req = 6371.0e3

# Grid cell size
dmin = 2.5e3

# Observation name
varname = "totalSnowDepth"
newvarname = "DSN_T_ISBA"

# Observations time
centralTimeISO = "2023-12-04T06:00:00Z"
centralTimeInt = centralTimeISO.replace("-","").replace("T","").replace(":","").replace("Z","")

# Read grid
with netCDF4.Dataset("data/grid.nc", 'r') as file:
  lat = file.variables['lat'][:,:]
  lon = file.variables['lon'][:,:]
nx = lon.shape[1]
ny = lon.shape[0]

# Build vector of cartesian coordinates
cc = np.zeros((nx*ny, 3))
bnd = []
ixy = 0
for iy in range(0, ny):
  for ix in range(0, nx):
    cc[ixy,:] = lonLatOroToXYZ(lon[iy,ix], lat[iy,ix], 0.0, req)
    if ix == 0 or ix == nx-1 or iy == 0 or iy == ny-1:
      bnd.append(True)
    else:
      bnd.append(False)
    ixy += 1

# Build KDTree
T = KDTree(cc)

# Read observations in JSON format
with open("data/qc_surface_snow_thickness.json", "r") as obsFile:
  obsdb = json.load(obsFile)
  nobsMax = len(obsdb.keys())
  obsLon = []
  obsLat = []
  obsOro = []
  obsVal = []
  obsErr = []
  ccObs = np.zeros((1, 3))
  for iobs in range(0, nobsMax):
    obs = obsdb[str(iobs)]

    # Check all conditions successively
    validObs = True

    # Condition on name
    validObs = validObs and (obs["varname"] == varname)

    # Condition on time
    validObs = validObs and (obs["obstime"] == centralTimeInt)

    # Condition on flag
    validObs = validObs and (obs["flag"] == 0.0)

    # Condition on location
    ccObs[0,:] = lonLatOroToXYZ(obs["lon"], obs["lat"], 0.0, req)
    d, i = T.query(ccObs)
    validObs = validObs and ((not bnd[i[0]]) or d < dmin)

    # Append valid observations
    if validObs:
      obsLon.append(obs["lon"])
      obsLat.append(obs["lat"])
      obsOro.append(obs["elev"])
      obsVal.append(obs["value"])
#      obsErr.append(obs["epsilon"]) # ???
      obsErr.append(0.001)
      

# Write observations in NetCDF format, complying with IODA standard
with netCDF4.Dataset("data/observations.nc", 'w', format="NETCDF4") as file:
  # Number of observations
  nobs = len(obsLon)
  print(str(nobs) + " obs. selected over " + str(nobsMax))

  # Location dimension and variable
  dimLocation = file.createDimension('Location', None)
  varLocation = file.createVariable('Location', np.int32, ('Location'), fill_value=-2147483643)
  file._ioda_layout = "ObsGroup"
  file._ioda_layout_version = 0
  varLocation[:] = np.linspace(0, nobs-1, nobs, dtype=int)

  # EffectiveError group
  effectiveErrorGrp = file.createGroup("EffectiveError")
  effectiveErrorVar = effectiveErrorGrp.createVariable(newvarname, np.float32, ('Location'), fill_value=-3.368795e38)
  effectiveErrorVar[:] = obsErr

  # EffectiveQC group
  effectiveQCGrp = file.createGroup("EffectiveQC")
  effectiveQCVar = effectiveQCGrp.createVariable(newvarname, np.int32, ('Location'), fill_value=-2147483643)
  effectiveQCVar[:] = 0

  # MetaData group
  metaDataGrp = file.createGroup("MetaData")
  dateTime = metaDataGrp.createVariable("dateTime", np.int64, ('Location'), fill_value=-9223372036854775801)
  dateTime.units = "seconds since " + centralTimeISO
  dateTime[:] = 0
  longitude = metaDataGrp.createVariable("longitude", np.float32, ('Location'), fill_value=-3.368795e38)
  longitude.units = "degrees_north"
  longitude[:] = obsLon
  latitude = metaDataGrp.createVariable("latitude", np.float32, ('Location'), fill_value=-3.368795e38)
  latitude.units = "degrees_east"
  latitude[:] = obsLat
  height = metaDataGrp.createVariable("height", np.float32, ('Location'), fill_value=-3.368795e38)
  height.units = "m"
  height[:] = obsOro

  # ObsBias group
  obsBiasGrp = file.createGroup("ObsBias")
  obsBiasVar = obsBiasGrp.createVariable(newvarname, np.float32, ('Location'), fill_value=-3.368795e38)
  obsBiasVar[:] = 0

  # ObsError group
  obsErrorGrp = file.createGroup("ObsError")
  obsErrorVar = obsErrorGrp.createVariable(newvarname, np.float32, ('Location'), fill_value=-3.368795e38)
  obsErrorVar[:] = obsErr

  # ObsValue group
  obsValueGrp = file.createGroup("ObsValue")
  obsValueVar = obsValueGrp.createVariable(newvarname, np.float32, ('Location'), fill_value=-3.368795e38)
  obsValueVar[:] = obsVal

  # hofx group
  hofxGrp = file.createGroup("hofx")
  hofxVar = hofxGrp.createVariable(newvarname, np.float32, ('Location'), fill_value=-3.368795e38)
