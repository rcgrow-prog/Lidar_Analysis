'''
Script created by Robert Grow 4/2025

This Python script, automates the processing of LAS (LiDAR point cloud) files using ArcPy, a Python site package for ESRI ArcGIS Pro.
'''
# Import libraries: 

import arcpy


def convert_las(input_las, target_folder, output_las, projection):
    # Converts LAS files to a specified projection and output location.
    # - input_las: Path to the input LAS file(s)
    # - target_folder: Folder where converted LAS files will be placed
    # - output_las: Name for the output LAS dataset
    # - projection: Spatial reference for the output LAS
    arcpy.conversion.ConvertLas(
        input_las,                 # Input LAS dataset
        target_folder,             # Output folder for converted files
        "SAME_AS_INPUT",           # Retain input folder structure
        "",                        # No file pattern filter
        "NO_COMPRESSION",          # Do not compress output files
        "REARRANGE_POINTS",        # Rearrange points for optimal storage
        output_las,                # Output LAS dataset name
        "ALL_FILES",               # Process all files
        projection                 # Output spatial reference
    )

def compute_las_statistics(output_las, stats_text):
    # Computes statistics for the LAS dataset and writes them to a text file.
    # - output_las: The LAS dataset to analyze
    # - stats_text: Path to the output statistics text file
    arcpy.management.LasDatasetStatistics(
        output_las,                # Input LAS dataset
        "OVERWRITE_EXISTING_STATS",# Overwrite existing statistics if present
        stats_text,                # Output text file for statistics
        "DATASET",                 # Scope: entire dataset
        "COMMA",                   # Use comma as delimiter
        "DECIMAL_POINT"            # Use decimal point for decimals
    )

def create_las_rasters(output_las, workspace):
    # Creates raster datasets from the LAS file for various statistics.
    # - output_las: The LAS dataset to analyze
    # - workspace: Folder where rasters will be saved
    rasters = [
        ("LAS_Pulse_Count", "PULSE_COUNT"),                       # Number of pulses per cell
        ("LAS_Point_Count", "POINT_COUNT"),                       # Number of points per cell
        ("LAS_Most_Frequent_Last_Return", "PREDOMINANT_LAST_RETURN"), # Most frequent last return value
        ("Most_Frequent_Class_Code", "PREDOMINANT_CLASS"),        # Most frequent classification code
        ("LAS_Range_Of_Intensity_Values", "INTENSITY_RANGE"),     # Range of intensity values per cell
        ("LAS_Range_Of_Elevation_Values", "Z_RANGE"),             # Range of elevation (Z) values per cell
    ]
    for raster_name, stat_type in rasters:
        out_raster = f"{workspace}\\{raster_name}"                # Construct output raster path
        arcpy.management.LasPointStatsAsRaster(
            output_las,           # Input LAS dataset
            out_raster,           # Output raster path
            stat_type,            # Statistic type to calculate
            "CELLSIZE",           # Use default cell size
            1                     # Cell size value (1 unit)
        )

def main():
    # Set overwrite to True
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
    arcpy.AddMessage("All processing complete.")

if __name__ == "__main__":
    main()
