'''
Step 4 - Multiband Raster NDVI Analysis Script
----------------------------------------------
Script created by Robert Grow 4/2025

Automates extraction of spectral bands, NDVI calculation, NDVI reclassification, and zonal statistics table 
generation from a multiband raster image using ArcPy and ArcGIS Spatial Analyst.
'''

import os
import arcpy
from arcpy.sa import *

def log_message(message):
    # Log a message to ArcGIS
    arcpy.AddMessage(message)

def extract_raster_band(input_raster, output_layer, band_index):
    # Extract a specific band from a multiband raster and create a raster layer
    arcpy.management.MakeRasterLayer(
        input_raster, output_layer, "", "", band_index=band_index
    )
    log_message(f"Raster band {band_index} extracted to {output_layer}")

def calculate_ndvi(red_band, nir_band, output_path):
    # Calculate NDVI from red and NIR bands and save the output raster
    ndvi = (Float(Raster(nir_band) - Raster(red_band)) /
            Float(Raster(nir_band) + Raster(red_band)))
    ndvi.save(output_path)
    log_message(f"NDVI raster saved to {output_path}")

def reclassify_ndvi(ndvi_raster, output_path):
    # Reclassify NDVI values into vegetation health classes
    arcpy.ddd.Reclassify(
        ndvi_raster,
        "VALUE",
        "-1 0 0;0 0.200000 1;0.200000 0.400000 2;0.400000 0.6 3;0.600000 1 4",
        output_path,
        "NODATA"
    )
    log_message(f"NDVI reclassified raster saved to {output_path}")

def compute_zonal_stats(crop_boundary, crop_field, ndvi_raster, output_table):
    # Compute zonal statistics as a table for NDVI within crop boundaries
    arcpy.sa.ZonalStatisticsAsTable(
        crop_boundary,
        crop_field,
        ndvi_raster,
        output_table,
        "DATA",
        "ALL",
        "CURRENT_SLICE",
        90,
        "AUTO_DETECT",
        "ARITHMETIC",
        360,
        None
    )
    log_message(f"Zonal statistics table created at {output_table}")

def main():
    try:
        # Set overwrite to true
        arcpy.env.overwriteOutput = True

        # Gather user variables
        band_1_input = arcpy.GetParameterAsText(0)  # Multiband raster input
        band_1_output = arcpy.GetParameterAsText(1)
        band_2_output = arcpy.GetParameterAsText(2)
        band_3_output = arcpy.GetParameterAsText(3)
        band_4_output = arcpy.GetParameterAsText(4)
        workspace = arcpy.GetParameterAsText(5)
        crop_boundary = arcpy.GetParameterAsText(6)
        crop_boundary_field = arcpy.GetParameterAsText(7)

        # Set workspace
        arcpy.env.workspace = workspace

        # Set output paths
        ndvi_output = os.path.join(workspace, "NDVI")
        ndvi_reclass = os.path.join(workspace, "NDVI_Reclass")
        zonal_table_text = os.path.join(workspace, "NDVI_Zonal_Table")

        # Run functions
        extract_raster_band(band_1_input, band_1_output, 1)  # Band 1 (Red)
        extract_raster_band(band_1_input, band_2_output, 2)  # Band 2 (Green)
        extract_raster_band(band_1_input, band_3_output, 3)  # Band 3 (Blue)
        extract_raster_band(band_1_input, band_4_output, 4)  # Band 4 (NIR)

        calculate_ndvi(band_3_output, band_4_output, ndvi_output)
        reclassify_ndvi(ndvi_output, ndvi_reclass)
        compute_zonal_stats(crop_boundary, crop_boundary_field, ndvi_output, zonal_table_text)

        log_message("NDVI analysis and zonal statistics complete.")

    except Exception as e:
        arcpy.AddError(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()