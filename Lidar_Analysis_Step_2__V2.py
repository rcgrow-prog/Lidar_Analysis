'''
This Python script automates the creation of Digital Elevation Models (DEM) and Digital Surface Models (DSM) from LAS (LiDAR) data using ArcPy, the Python package for ArcGIS.

'''

import arcpy

def make_las_dataset_layer(input_las, output_layer, point_filters, return_values):
    """Create a LAS dataset layer with specified filters."""
    arcpy.management.MakeLasDatasetLayer(
        input_las,            # Input LAS dataset
        output_layer,         # Output LAS dataset layer name
        point_filters,        # Classification codes to include (e.g., ground or vegetation)
        return_values,        # Return values to include (e.g., last, first, single, etc.)
        "INCLUDE_UNFLAGGED",  # Include unflagged points
        "INCLUDE_SYNTHETIC",  # Include synthetic points
        "INCLUDE_KEYPOINT",   # Include key points
        "EXCLUDE_WITHHELD",   # Exclude withheld points
        None,                 # No spatial filter
        "INCLUDE_OVERLAP"     # Include overlapping points
    )
    arcpy.AddMessage(f"LAS Dataset Layer created at: {output_layer}")

def create_raster_from_las(las_layer, out_raster, method):
    """Create a raster (DEM or DSM) from a LAS dataset layer."""
    if method == "DEM":
        # Create a Digital Elevation Model using triangulation of ground points
        arcpy.conversion.LasDatasetToRaster(
            las_layer,                          # Input LAS dataset layer
            out_raster,                         # Output raster path
            "ELEVATION",                        # Use elevation values
            "TRIANGULATION LINEAR NO_THINNING", # Interpolation method for DEM
            "FLOAT",                            # Output raster type
            "CELLSIZE",                         # Use default cell size
            1,                                  # Cell size value (1 unit)
            1                                   # Z factor (vertical exaggeration)
        )
    elif method == "DSM":
        # Create a Digital Surface Model using binning of vegetation points
        arcpy.conversion.LasDatasetToRaster(
            las_layer,                          # Input LAS dataset layer
            out_raster,                         # Output raster path
            "ELEVATION",                        # Use elevation values
            "BINNING MAXIMUM LINEAR",           # Interpolation method for DSM
            "FLOAT",                            # Output raster type
            "CELLSIZE",                         # Use default cell size
            1,                                  # Cell size value (1 unit)
            1                                   # Z factor (vertical exaggeration)
        )
    arcpy.AddMessage(f"{method} created at: {out_raster}")

def main():
    # Set ArcPy to overwrite outputs by default
    arcpy.env.overwriteOutput = True

    # Get user-supplied parameters from the ArcGIS tool interface
    input_las = arcpy.GetParameterAsText(0)         # Input LAS file
    output_ground_las = arcpy.GetParameterAsText(1) # Output ground LAS dataset layer
    output_veg_las = arcpy.GetParameterAsText(2)    # Output vegetation LAS dataset layer
    out_dem = arcpy.GetParameterAsText(3)           # Output DEM raster
    out_dsm = arcpy.GetParameterAsText(4)           # Output DSM raster

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
