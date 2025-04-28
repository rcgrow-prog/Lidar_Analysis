'''
Step 1 - Process LiDAR point clouds
------------------------
Script created by Robert Grow, April 2025

This script automates the processing of LAS (LiDAR point cloud) files using ArcPy for ESRI ArcGIS Pro.
It handles LAS file conversion, statistics computation, and raster generation.
'''

import os
import arcpy

def log_message(message):
    # Log a message to ArcGIS
    arcpy.AddMessage(message)

def convert_las(input_las, target_folder, output_las, projection):
    # Convert LAS files to a specified projection and output location
    arcpy.conversion.ConvertLas(
        input_las,
        target_folder,
        "SAME_AS_INPUT",
        "",
        "NO_COMPRESSION",
        "REARRANGE_POINTS",
        output_las,
        "ALL_FILES",
        projection
    )
    log_message(f"LAS files converted and saved to {target_folder}")

def compute_las_statistics(output_las, stats_text):
    # Compute statistics for the LAS dataset and write them to a text file
    arcpy.management.LasDatasetStatistics(
        output_las,
        "OVERWRITE_EXISTING_STATS",
        stats_text,
        "DATASET",
        "COMMA",
        "DECIMAL_POINT"
    )
    log_message(f"LAS statistics saved to {stats_text}")

def create_las_rasters(output_las, workspace):
    # Create raster datasets from the LAS file for various statistics
    rasters = [
        ("LAS_Pulse_Count", "PULSE_COUNT"),
        ("LAS_Point_Count", "POINT_COUNT"),
        ("LAS_Most_Frequent_Last_Return", "PREDOMINANT_LAST_RETURN"),
        ("Most_Frequent_Class_Code", "PREDOMINANT_CLASS"),
        ("LAS_Range_Of_Intensity_Values", "INTENSITY_RANGE"),
        ("LAS_Range_Of_Elevation_Values", "Z_RANGE"),
    ]

    for raster_name, stat_type in rasters:
        out_raster = os.path.join(workspace, raster_name)
        arcpy.management.LasPointStatsAsRaster(
            output_las,
            out_raster,
            stat_type,
            "CELLSIZE",
            1  # Cell size value (1 unit)
        )
        log_message(f"Raster {raster_name} created at {out_raster}")

def main():
    try:
        arcpy.env.overwriteOutput = True

        # Get parameters from user
        input_las = arcpy.GetParameterAsText(0)
        target_folder = arcpy.GetParameterAsText(1)
        output_las = arcpy.GetParameterAsText(2)
        projection = arcpy.GetParameterAsText(3)
        stats_text = arcpy.GetParameterAsText(4)
        workspace = arcpy.GetParameterAsText(5)

        arcpy.env.workspace = workspace

        # Run processing steps
        convert_las(input_las, target_folder, output_las, projection)
        compute_las_statistics(output_las, stats_text)
        create_las_rasters(output_las, workspace)

        log_message("All processing complete.")

    except Exception as e:
        arcpy.AddError(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()