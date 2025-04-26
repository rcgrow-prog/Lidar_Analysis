'''
Script created by Robert Grow 4/2025

This Python script automates the creation of Digital Elevation Models (DEM) and Digital Surface Models (DSM) from LAS (LiDAR) data using ArcPy, the Python package for ArcGIS Pro.
'''

import arcpy

def make_las_dataset_layer(input_las, output_layer, point_filters, return_values):
    # Create a LAS dataset layer with specified filters.
    arcpy.management.MakeLasDatasetLayer(
        input_las,
        output_layer,
        point_filters,
        return_values,
        "INCLUDE_UNFLAGGED",
        "INCLUDE_SYNTHETIC",
        "INCLUDE_KEYPOINT",
        "EXCLUDE_WITHHELD",
        None, # No spatial filter
        "INCLUDE_OVERLAP"
    )
    arcpy.AddMessage(f"LAS Dataset Layer created at: {output_layer}")

def create_raster_from_las(las_layer, out_raster, method):
    # Create a raster (DEM or DSM) from a LAS dataset layer.
    if method == "DEM":
        # Create a Digital Elevation Model using triangulation of ground points
        arcpy.conversion.LasDatasetToRaster(
            las_layer,
            out_raster,
            "ELEVATION",
            "TRIANGULATION LINEAR NO_THINNING", # Interpolation method for DEM
            "FLOAT",
            "CELLSIZE",
            1,
            1
        )
    elif method == "DSM":
        # Create a Digital Surface Model using binning of vegetation points
        arcpy.conversion.LasDatasetToRaster(
            las_layer,
            out_raster,
            "ELEVATION",
            "BINNING MAXIMUM LINEAR", # Interpolation method for DSM
            "FLOAT",
            "CELLSIZE",
            1,
            1
        )
    arcpy.AddMessage(f"{method} created at: {out_raster}")

def main():
    # Set ArcPy to overwrite outputs by default
    arcpy.env.overwriteOutput = True

    # Get user-supplied parameters from the ArcGIS tool interface
    input_las = arcpy.GetParameterAsText(0)
    output_ground_las = arcpy.GetParameterAsText(1)
    output_veg_las = arcpy.GetParameterAsText(2)
    out_dem = arcpy.GetParameterAsText(3)
    out_dsm = arcpy.GetParameterAsText(4)

    # Define classification codes for ground and vegetation
    ground_point_filters = "2"          # Ground class code
    veg_point_filters = "3;4;5"         # Vegetation class codes
    
    # Define return values to include in the filtered layers
    return_values = "LAST;FIRST_OF_MANY;LAST_OF_MANY;SINGLE;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15"

    # Create LAS dataset layer for ground points
    make_las_dataset_layer(input_las, output_ground_las, ground_point_filters, return_values)
    
    # Create LAS dataset layer for vegetation points
    make_las_dataset_layer(input_las, output_veg_las, veg_point_filters, return_values)

    # Create DEM raster from ground LAS dataset layer
    create_raster_from_las(output_ground_las, out_dem, "DEM")
    
    # Create DSM raster from vegetation LAS dataset layer
    create_raster_from_las(output_veg_las, out_dsm, "DSM")

if __name__ == "__main__":
    main()
