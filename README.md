# Lidar_Analysis
A series of ArcPy scripts processing LiDAR (LAS) files and derivatives. 

Step 1: 
    
    Purpose:
    
        This Python script, written by Robert Grow in April 2025, automates the processing of LAS (LiDAR point cloud) files using ArcPy, a Python site package for ESRI’s ArcGIS.

    Main Steps:

        1. Convert LAS Files:
            Converts input LAS files to a specified projection and output location using the arcpy.conversion.ConvertLas tool.
        
        2. Compute LAS Statistics:
            Calculates and writes statistical information for the LAS dataset using arcpy.management.LasDatasetStatistics.

        3. Generate LAS Raster Outputs:
            Creates several raster datasets from the LAS file, each representing different statistics (e.g., pulse count, point count, predominant class, intensity range, elevation range) using arcpy.management.LasPointStatsAsRaster.

    How It Works:

        The script takes user input for file paths, projection, statistics output, and workspace through ArcGIS parameters.

        It sets up the workspace and allows overwriting of outputs.

        It sequentially runs the conversion, statistics computation, and raster creation steps.

        On completion, it notifies the user that all processing is complete.

    Intended Use:
        This script is designed for GIS professionals working with LiDAR data in ArcGIS, streamlining the conversion, analysis, and rasterization of LAS datasets.

Step 2: 

    Purpose:
        This Python script automates the creation of Digital Elevation Models (DEM) and Digital Surface Models (DSM) from LAS (LiDAR) data using ArcPy, the Python package for ArcGIS.

    Main Steps:

        1. Create LAS Dataset Layers with Filters:

            The script makes two filtered LAS dataset layers from the input LAS file:

                Ground Layer: Contains only ground points (classification code 2).

                Vegetation Layer: Contains vegetation points (classification codes 3, 4, 5).

            Additional filters specify which return values to include (e.g., last, first, single, etc.).

        2. Generate DEM and DSM Rasters:

            DEM (Digital Elevation Model): Created from the ground layer using triangulation.

            DSM (Digital Surface Model): Created from the vegetation layer using binning with the maximum value.

            Both rasters use elevation values and a cell size of 1 unit.

        3. User Inputs:

            The script is designed to be run as a script tool in ArcGIS, taking user-specified inputs for:

                Input LAS file

                Output ground and vegetation LAS layers

                Output DEM and DSM raster files

    Workflow Overview:

        Set up ArcPy environment to allow overwriting outputs.

        Define classification and return value filters for ground and vegetation.

        Create filtered LAS dataset layers for ground and vegetation.

        Generate DEM and DSM rasters from these layers.

        Output messages inform the user of progress and file locations.

    Intended Use:
        This script is ideal for GIS professionals working with LiDAR data who need to quickly extract ground and vegetation surfaces and convert them into raster elevation models for further analysis or mapping.

Step 3:


Step 4:


Step 5:


Step 6:


Step 7:


Step 8:
