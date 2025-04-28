'''
Step 2.1 - Vegetation DSM Extraction Script
---------------------------------------------
Script created by Robert Grow 4/2025

Automates extraction of vegetation points from a LAS (LiDAR) dataset and generation of a DSM raster using ArcPy.
'''

import arcpy

def log_message(message):
    # Log a message to ArcGIS
    arcpy.AddMessage(message)

def make_vegetation_las_layer(input_las, output_las_layer, point_filters, return_values):
    # Create a vegetation LAS dataset layer with specified filters.
    arcpy.management.MakeLasDatasetLayer(
        input_las,
        output_las_layer,
        point_filters,
        return_values,
        "INCLUDE_UNFLAGGED",
        "INCLUDE_SYNTHETIC",
        "INCLUDE_KEYPOINT",
        "EXCLUDE_WITHHELD",
        None,
        "INCLUDE_OVERLAP"
    )
    log_message(f"Vegetation LAS Dataset created at: {output_las_layer}")

def create_dsm_from_las(las_layer, out_dsm):
    # Create a DSM raster from a LAS dataset layer
    arcpy.conversion.LasDatasetToRaster(
        las_layer,
        out_dsm,
        "ELEVATION",
        "BINNING MAXIMUM LINEAR",
        "FLOAT",
        "CELLSIZE",
        1,
        1
    )
    log_message(f"DSM created at: {out_dsm}")

def main():
    try:
        # Set overwrite to True
        arcpy.env.overwriteOutput = True

        # Get parameters from user
        input_las = arcpy.GetParameterAsText(0)
        output_veg_las = arcpy.GetParameterAsText(1)
        out_dsm = arcpy.GetParameterAsText(2)

        # Define filters
        return_values = "LAST;FIRST_OF_MANY;LAST_OF_MANY;SINGLE;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15"
        veg_point_filters = "0;1;3;4;5;6;11;17;19;21"

        # Run variables
        make_vegetation_las_layer(input_las, output_veg_las, veg_point_filters, return_values)
        create_dsm_from_las(output_veg_las, out_dsm)

        log_message("Vegetation DSM extraction complete.")

    except Exception as e:
        arcpy.AddError(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
