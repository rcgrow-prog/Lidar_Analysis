'''
Script created by Robert Grow 4/2025

This Python script automates the extraction of spectral bands, NDVI calculation, NDVI reclassification, and zonal statistics table generation from a multiband raster image using ArcPy and ArcGIS Spatial Analyst.
'''

import arcpy
from arcpy.sa import *

def extract_raster_band(input_raster, output_layer, band_index):
    # Extracts a specific band from a multiband raster and creates a raster layer.
    arcpy.management.MakeRasterLayer(input_raster, output_layer, "", "", band_index=band_index)
    arcpy.AddMessage(f"Raster band {band_index} extracted to {output_layer}")

def calculate_ndvi(red_band, nir_band, output_path):
    # Calculates NDVI from red and NIR bands and saves the output raster.
    ndvi = (Float(Raster(nir_band) - Raster(red_band)) / 
            Float(Raster(nir_band) + Raster(red_band)))
    ndvi.save(output_path)
    arcpy.AddMessage(f"NDVI raster saved to {output_path}")

def reclassify_ndvi(ndvi_raster, output_path):
    # Reclassifies NDVI values into vegetation health classes.
    arcpy.ddd.Reclassify(
        ndvi_raster,
        "VALUE",
        "-1 0 0;0 0.200000 1;0.200000 0.400000 2;0.400000 0.6 3;0.600000 1 4",
        output_path,
        "NODATA"
    )
    arcpy.AddMessage(f"NDVI reclassified raster saved to {output_path}")

def compute_zonal_stats(crop_boundary, crop_field, ndvi_raster, output_table):
    # Computes zonal statistics as a table for NDVI within crop boundaries.
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
    arcpy.AddMessage(f"Zonal statistics table created at {output_table}")

def main():
    # Set overwrite to True
    arcpy.env.overwriteOutput = True

    # Gather input parameters
    Band_1_Input = arcpy.GetParameterAsText(0) # Raster Input
    Band_1_Output = arcpy.GetParameterAsText(1)
    Band_2_Output = arcpy.GetParameterAsText(2)
    Band_3_Output = arcpy.GetParameterAsText(3)
    Band_4_Output = arcpy.GetParameterAsText(4)
    Workspace = arcpy.GetParameterAsText(5)
    Crop_Boundary = arcpy.GetParameterAsText(6)
    Crop_Boundary_Field = arcpy.GetParameterAsText(7)

    # Set workspace
    arcpy.env.workspace = Workspace

    # Output paths
    NDVI_Output = f"{Workspace}\\NDVI"
    NDVI_Reclass = f"{Workspace}\\NDVI_Reclass"
    Zonal_Table_Text = f"{Workspace}\\NDVI_Zonal_Table"

    # Extract bands as raster layers
    extract_raster_band(Band_1_Input, Band_1_Output, 1) # Band 1 (e.g., Blue)
    extract_raster_band(Band_1_Input, Band_2_Output, 2) # Band 2 (e.g., Green)
    extract_raster_band(Band_1_Input, Band_3_Output, 3) # Band 3 (e.g., Red)
    extract_raster_band(Band_1_Input, Band_4_Output, 4) # Band 4 (e.g., NIR)

    # Calculate NDVI (using Red and NIR bands)
    calculate_ndvi(Band_3_Output, Band_4_Output, NDVI_Output)

    # Reclassify NDVI
    reclassify_ndvi(NDVI_Output, NDVI_Reclass)

    # Compute zonal statistics as table
    compute_zonal_stats(Crop_Boundary, Crop_Boundary_Field, NDVI_Output, Zonal_Table_Text)

if __name__ == "__main__":
    main()
