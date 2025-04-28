'''
Step 7 - Hydrologic Terrain Analysis Script
-------------------------------------------
Created by Robert Grow, 4/2025

This script automates hydrologic terrain analysis using ArcPy and the ArcGIS Spatial Analyst extension.
It processes a DEM to generate filled elevation, flow direction, flow accumulation, and stream order rasters
using both D8 and DINF flow algorithms.
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

def validate_inputs(*paths):
    # Validate that all input paths exist
    for path in paths:
        if not arcpy.Exists(path):
            arcpy.AddError(f"Input does not exist: {path}")
            raise FileNotFoundError(f"Input does not exist: {path}")

def fill_dem(input_dem, output_path):
    # Fill sinks in a DEM using the Fill tool
    filled_dem = Fill(input_dem)
    filled_dem.save(output_path)
    log_message(f"Filled DEM saved to {output_path}")
    return filled_dem

def calculate_flow_direction(filled_dem, output_prefix, method):
    # Calculate flow direction (D8 or DINF) with drop raster
    drop_raster = f"{output_prefix}_{method}_Drop"
    flow_dir = FlowDirection(filled_dem, "NORMAL", drop_raster, method)
    output_path = f"{output_prefix}_{method}_Flow_Direction"
    flow_dir.save(output_path)
    log_message(f"{method} flow direction saved to {output_path}")
    return flow_dir

def calculate_flow_accumulation(flow_dir, output_prefix, method):
    # Calculate flow accumulation for a given flow direction raster
    flow_accum = FlowAccumulation(flow_dir, None, "FLOAT", method)
    output_path = f"{output_prefix}_{method}_Flow_Accumulation"
    flow_accum.save(output_path)
    log_message(f"{method} flow accumulation saved to {output_path}")
    return flow_accum

def reclassify_flow_accumulation(flow_accum, output_path):
    # Reclassify flow accumulation into stream classes
    arcpy.ddd.Reclassify(
        flow_accum, "VALUE",
        "0 200 1;200 400 2;400 10000000 3",
        output_path, "NODATA"
    )
    log_message(f"Reclassified flow accumulation saved to {output_path}")

def calculate_stream_order(flow_accum_reclass, flow_dir, output_prefix, method):
    # Calculate Strahler stream order
    stream_order = StreamOrder(flow_accum_reclass, flow_dir, "STRAHLER")
    output_path = f"{output_prefix}_{method}_Stream_Order"
    stream_order.save(output_path)
    log_message(f"{method} stream order saved to {output_path}")

def main():
    check_out_extensions()
    try:
        # Set overwrite to True
        arcpy.env.overwriteOutput = True

        # Get parameters
        dem_input = arcpy.GetParameterAsText(0)
        fill_output = arcpy.GetParameterAsText(1)
        workspace = arcpy.GetParameterAsText(2)
        arcpy.env.workspace = workspace

        validate_inputs(dem_input, workspace)

        filled_dem = fill_dem(dem_input, fill_output)
        flow_dir_prefix = os.path.join(workspace, "Hydro")

        # Calculate flow directions
        d8_flow = calculate_flow_direction(filled_dem, flow_dir_prefix, "D8")
        dinf_flow = calculate_flow_direction(filled_dem, flow_dir_prefix, "DINF")

        # Calculate flow accumulations
        d8_accum = calculate_flow_accumulation(d8_flow, flow_dir_prefix, "D8")
        dinf_accum = calculate_flow_accumulation(dinf_flow, flow_dir_prefix, "DINF")

        # Reclassify accumulations
        d8_accum_reclass = os.path.join(workspace, "Hydro_D8_Flow_Accumulation_Reclass")
        reclassify_flow_accumulation(d8_accum, d8_accum_reclass)

        dinf_accum_reclass = os.path.join(workspace, "Hydro_DINF_Flow_Accumulation_Reclass")
        reclassify_flow_accumulation(dinf_accum, dinf_accum_reclass)

        # Calculate stream orders
        calculate_stream_order(d8_accum_reclass, d8_flow, flow_dir_prefix, "D8")
        calculate_stream_order(dinf_accum_reclass, d8_flow, flow_dir_prefix, "DINF")

        log_message("Hydrologic terrain analysis complete.")

    except Exception as e:
        arcpy.AddError(f"Error: {e}")
        raise
    finally:
        check_in_extensions()

if __name__ == "__main__":
    main()