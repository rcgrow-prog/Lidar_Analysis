'''
Script created by Robert Grow 4/2025

This Python script automates the extraction of vegetation points from a LAS (LiDAR) dataset and generates a Digital Surface Model (DSM) raster using ArcPy, the Python library for ArcGIS Pro.
'''

import arcpy

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
    arcpy.AddMessage(f"Vegetation LAS Dataset Created at: {output_las_layer}")

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
    arcpy.AddMessage(f"DSM created at {out_dsm}")

def main():
    # Set overwrite to True
    arcpy.env.overwriteOutput = True

    # Get parameters from user
    input_las = arcpy.GetParameterAsText(0)
    output_veg_las = arcpy.GetParameterAsText(1)
    out_dsm = arcpy.GetParameterAsText(2)

    # Define filters
    return_values = "LAST;FIRST_OF_MANY;LAST_OF_MANY;SINGLE;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15"
    veg_point_filters_updated = "0;1;3;4;5;6;11;17;19;21"

    # Create vegetation LAS dataset layer
    make_vegetation_las_layer(input_las, output_veg_las, veg_point_filters_updated, return_values)

    # Create DSM raster
    create_dsm_from_las(output_veg_las, out_dsm)

if __name__ == "__main__":
    main()
