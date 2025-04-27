'''
Script created by Robert Grow 4/2025

This Python script, designed for use in ArcGIS, automates the calculation of a soil composition index raster by 
combining three input rasters-slope, flow accumulation, and curvature-using user-defined weights. 
It leverages the ArcPy and Spatial Analyst extension for raster processing.
'''

import arcpy
from arcpy.sa import *

def check_out_extensions():
    # Check out required ArcGIS extensions
    try:
        arcpy.CheckOutExtension("Spatial")
        arcpy.AddMessage("Spatial Analyst extension checked out successfully.")
    except arcpy.ExecuteError:
        arcpy.AddError("Could not check out Spatial Analyst extension.")
        raise

def check_in_extensions():
    # Check in ArcGIS extensions
    arcpy.CheckInExtension("Spatial")
    arcpy.AddMessage("Spatial Analyst extension checked in.")

def calculate_soil_composition(slope_raster, flow_accum, curvature_raster, output_path):
    """
    Calculate soil composition index using weighted combination of:
    - Slope (40%)
    - Flow Accumulation (30%)
    - Curvature (30%)
    """
    try:
        # Convert inputs to float rasters
        arcpy.AddMessage("Converting input rasters to float...")
        slope = Float(Raster(slope_raster))
        flow = Float(Raster(flow_accum))
        curv = Float(Raster(curvature_raster))

        # Calculate weighted composition
        arcpy.AddMessage("Calculating soil composition index...")
        soil_comp = (slope * 0.4) + (flow * 0.3) + (curv * 0.3)
        
        # Save output
        soil_comp.save(output_path)
        arcpy.AddMessage(f"Soil composition raster saved to: {output_path}")
        return soil_comp

    except Exception as e:
        arcpy.AddError(f"Error in soil composition calculation: {str(e)}")
        raise

def main():
    check_out_extensions()
    try:
        # Environment setup
        arcpy.env.overwriteOutput = True

        # Get input parameters
        slope_raster = arcpy.GetParameterAsText(0)
        flow_accum = arcpy.GetParameterAsText(1)
        curvature_raster = arcpy.GetParameterAsText(2)
        workspace = arcpy.GetParameterAsText(3)
        
        # Set workspace
        arcpy.env.workspace = workspace
        arcpy.AddMessage(f"Workspace set to: {workspace}")

        # Set output path
        output_path = f"{workspace}\\Soil_Composition"
        arcpy.AddMessage(f"Output will be saved to: {output_path}")

        # Run calculation
        calculate_soil_composition(slope_raster, flow_accum, curvature_raster, output_path)

    except Exception as e:
        arcpy.AddError(f"Script failed: {str(e)}")
    finally:
        check_in_extensions()

if __name__ == "__main__":
    main()
