'''
Step 2 - LiDAR LAS File Processing Script
---------------------------------------------
Script created by Robert Grow 4/2025

Automates the creation of DEM and DSM rasters from LAS (LiDAR) data using ArcPy for ArcGIS Pro.
'''
import arcpy

def log_message(message):
    # Log a message to ArcGIS
    arcpy.AddMessage(message)

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
    log_message(f"LAS Dataset Layer created at: {output_layer}")

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
    log_message(f"{method} created at: {out_raster}")

def main():
    try:
        arcpy.env.overwriteOutput = True

        # Gather variables from user
        input_las = arcpy.GetParameterAsText(0)
        output_ground_las = arcpy.GetParameterAsText(1)
        output_veg_las = arcpy.GetParameterAsText(2)
        out_dem = arcpy.GetParameterAsText(3)
        out_dsm = arcpy.GetParameterAsText(4)

        # Set LAS filters
        ground_point_filters = "2"
        veg_point_filters = "3;4;5"
        return_values = (
            "LAST;FIRST_OF_MANY;LAST_OF_MANY;SINGLE;"
            "1;2;3;4;5;6;7;8;9;10;11;12;13;14;15"
        )

        # Run the functions
        make_las_dataset_layer(input_las, output_ground_las, ground_point_filters, return_values)
        make_las_dataset_layer(input_las, output_veg_las, veg_point_filters, return_values)
        create_raster_from_las(output_ground_las, out_dem, "DEM")
        create_raster_from_las(output_veg_las, out_dsm, "DSM")

        log_message("LiDAR LAS processing complete.")

    except Exception as e:
        arcpy.AddError(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
