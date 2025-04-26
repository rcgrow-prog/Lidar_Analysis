'''
Script created by Robert Grow 4/2025

This Python script automates the analysis of canopy structure, irrigation efficiency, obstacles, and equipment suitability in agricultural or forestry fields using ArcPy and the ArcGIS Spatial Analyst extension. It processes DSM, DEM, slope, and NDVI rasters to generate a suite of management and planning layers.
'''

import arcpy
from arcpy.sa import *

def check_out_extensions():
    # Check out required ArcGIS extensions
    arcpy.CheckOutExtension("Spatial")

def check_in_extensions():
    # Check in ArcGIS extensions
    arcpy.CheckInExtension("Spatial")

def calculate_canopy_height(dsm_input, dem_input, output_path):
    # Calculate and save canopy height (DSM - DEM)
    dsm = Float(Raster(dsm_input))
    dem = Float(Raster(dem_input))
    canopy = dsm - dem
    canopy.save(output_path)
    arcpy.AddMessage(f"Canopy height raster saved to {output_path}")
    return canopy

def reclassify_canopy_height(canopy_height_raster, output_path):
    # Reclassify canopy height to create canopy cover raster
    arcpy.ddd.Reclassify(
        canopy_height_raster, "VALUE",
        "-200 0 0;0 0.100000 1;0.100000 0.300000 2;0.300000 0.500000 3;0.500000 0.700000 4;0.700000 300.000000 5",
        output_path, "DATA"
    )
    arcpy.AddMessage(f"Canopy cover raster saved to {output_path}")

def create_obstacles_layer(canopy_height_raster, output_path):
    # Create an obstacle raster by reclassifying canopy height
    obstacle = arcpy.sa.Reclassify(
        canopy_height_raster, "VALUE",
        "-100.000000 0 0;0 1 1;1 3 2;3 200.000000 3",
        "NODATA"
    )
    obstacle.save(output_path)
    arcpy.AddMessage(f"Obstacles raster saved to {output_path}")

def calculate_irrigation_efficiency(ndvi_input, slope_raster, canopy_height_raster, output_path):
    # Calculate irrigation efficiency raster
    ndvi = Raster(ndvi_input)
    slopes = Float(Raster(slope_raster))
    canopy = Float(Raster(canopy_height_raster))
    irrigation_efficiency = ndvi * (1 - slopes / 100) * canopy
    irrigation_efficiency.save(output_path)
    arcpy.AddMessage(f"Irrigation efficiency raster saved to {output_path}")

def reclassify_irrigation_efficiency(irrigation_efficiency_raster, output_path):
    # Reclassify irrigation efficiency raster
    ir_eff_reclass = arcpy.sa.Reclassify(
        irrigation_efficiency_raster, "VALUE",
        "-50.00000 0 0;0 0.200000 1;0.200000 0.400000 2;0.400000 0.600000 3;0.600000 0.800000 4;0.800000 1 5;1 50.00000 6",
        "NODATA"
    )
    ir_eff_reclass.save(output_path)
    arcpy.AddMessage(f"Irrigation efficiency reclassified raster saved to {output_path}")

def convert_canopy_cover_to_polygon(canopy_cover_raster, output_polygon):
    # Convert canopy cover raster to polygon for tree canopy (value = 5)
    # Select canopy cover value = 5 (trees)
    arcpy.management.SelectLayerByAttribute(canopy_cover_raster, "NEW_SELECTION", "Value = 5", None)
    arcpy.conversion.RasterToPolygon(
        canopy_cover_raster, output_polygon, "SIMPLIFY", "Value",
        "MULTIPLE_OUTER_PART", None
    )
    arcpy.AddMessage(f"Canopy cover polygon saved to {output_polygon}")

def extract_ndvi_excluding_trees(ndvi_field_boundary, canopy_cover_polygon, output_path):
    # Extract NDVI values from field boundaries excluding tree canopy
    ndvi_field_raster = arcpy.sa.ExtractByMask(
        ndvi_field_boundary, canopy_cover_polygon, "OUTSIDE", ""
    )
    ndvi_field_raster.save(output_path)
    arcpy.AddMessage(f"NDVI field boundary excluding trees saved to {output_path}")

def reclassify_slope_for_equipment(slope_raster, output_path):
    # Reclassify slope raster for equipment steepness
    slope_reclass = arcpy.sa.Reclassify(
        slope_raster, "VALUE", "0 5 0;5 15 1;15 100 2", "NODATA"
    )
    slope_reclass.save(output_path)
    arcpy.AddMessage(f"Slope steepness raster for equipment saved to {output_path}")

def main():
    check_out_extensions()
    
    try:
        # Set overwrite to True
        arcpy.env.overwriteOutput = True

        # Set the Variables
        DSM_Input = arcpy.GetParameterAsText(0)
        DEM_Input = arcpy.GetParameterAsText(1)
        Slope_Raster = arcpy.GetParameterAsText(2)
        Workspace = arcpy.GetParameterAsText(3)
        NDVI_Input = arcpy.GetParameterAsText(4)
        NDVI_Field_Boundary = arcpy.GetParameterAsText(5)

        # Set workspace
        arcpy.env.workspace = Workspace

        # Set the output file paths
        Canopy_Height = f"{Workspace}\\Canopy_Height"
        Canopy_Cover = f"{Workspace}\\Canopy_Cover"
        Irrigation_Efficiency_Output = f"{Workspace}\\Irrigation_Effeciency"
        Irrigation_Eff_Reclass = f"{Workspace}\\Irrigation_Effeciency_Reclass"
        Canopy_Cover_to_Polygon = f"{Workspace}\\Canopy_Cover_Trees_Polygon"
        NDVI_Field_Boundary_Excluding_Trees = f"{Workspace}\\NDVI_Field_Boundary_Excluding_Trees"
        Obstacles_Reclass = f"{Workspace}\\Equipment_Obstacles"
        Slope_Steepness = f"{Workspace}\\Steepness_For_Equipment"

        # Processing steps
        canopy_height_raster = calculate_canopy_height(DSM_Input, DEM_Input, Canopy_Height)
        reclassify_canopy_height(Canopy_Height, Canopy_Cover)
        create_obstacles_layer(Canopy_Height, Obstacles_Reclass)
        calculate_irrigation_efficiency(NDVI_Input, Slope_Raster, Canopy_Height, Irrigation_Efficiency_Output)
        reclassify_irrigation_efficiency(Irrigation_Efficiency_Output, Irrigation_Eff_Reclass)
        convert_canopy_cover_to_polygon(Canopy_Cover, Canopy_Cover_to_Polygon)
        extract_ndvi_excluding_trees(NDVI_Field_Boundary, Canopy_Cover_to_Polygon, NDVI_Field_Boundary_Excluding_Trees)
        reclassify_slope_for_equipment(Slope_Raster, Slope_Steepness)

    finally:
        check_in_extensions()

if __name__ == "__main__":
    main()
