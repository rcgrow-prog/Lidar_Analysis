'''
Step 8 - Soil Composition Index Calculation Script
--------------------------------------------------
Script created by Robert Grow 4/2025

This Python script, designed for use in ArcGIS, automates the calculation of a soil composition index raster by 
combining three input rasters-slope, flow accumulation, and curvature-using user-defined weights. 
It leverages the ArcPy and Spatial Analyst extension for raster processing.
'''

import os
import arcpy
from arcpy.sa import *

def log_message(message):
    # Log a message to ArcGIS
    arcpy.AddMessage(message)

def check_out_extensions():
    # Check out required ArcGIS extensions
    try:
        arcpy.CheckOutExtension("Spatial")
        log_message("Spatial Analyst extension checked out successfully.")
    except arcpy.ExecuteError:
        arcpy.AddError("Could not check out Spatial Analyst extension.")
        raise

def check_in_extensions():
    # Check in ArcGIS extensions
    arcpy.CheckInExtension("Spatial")
    log_message("Spatial Analyst extension checked in.")

def calculate_soil_composition(slope_raster, flow_accum, curvature_raster, output_path):
    """
    Calculate soil composition index using weighted combination of:
    - Slope (40%)
    - Flow Accumulation (30%)
    - Curvature (30%)
    """
    slope = Float(Raster(slope_raster))
    flow = Float(Raster(flow_accum))
    curv = Float(Raster(curvature_raster))
    soil_comp = (slope * 0.4) + (flow * 0.3) + (curv * 0.3)
    soil_comp.save(output_path)
    log_message(f"Soil composition raster saved to: {output_path}")
    return soil_comp

def main():
    check_out_extensions()
    try:
        # Set overwrite to True
        arcpy.env.overwriteOutput = True

        # Get parameters
        slope_raster = arcpy.GetParameterAsText(0)
        flow_accum = arcpy.GetParameterAsText(1)
        curvature_raster = arcpy.GetParameterAsText(2)
        workspace = arcpy.GetParameterAsText(3)

        arcpy.env.workspace = workspace
        log_message(f"Workspace set to: {workspace}")

        output_path = os.path.join(workspace, "Soil_Composition")
        log_message(f"Output will be saved to: {output_path}")

        calculate_soil_composition(slope_raster, flow_accum, curvature_raster, output_path)

        log_message("Soil composition index calculation complete.")

    except Exception as e:
        arcpy.AddError(f"Script failed: {e}")
        raise
    finally:
        check_in_extensions()

if __name__ == "__main__":
    main()