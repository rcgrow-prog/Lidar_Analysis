'''
Step 6 - Canopy, Irrigation, and Equipment Suitability Analysis Script
----------------------------------------------------------------------
Script created by Robert Grow 4/2025

This script processes DSM, DEM, Slope, and NDVI rasters to generate canopy height,
canopy cover, irrigation efficiency, obstacles, and equipment suitability outputs.
Intended for agricultural/forestry spatial analysis in ArcGIS.
'''

import os
import arcpy
from arcpy.sa import *

def log_message(message):
    # Log a message to ArcGIS
    arcpy.AddMessage(message)

def check_out_extensions():
    # Check out required ArcGIS extensions
    try:
        arcpy.CheckOutExtension("Spatial")
        log_message("Spatial Analyst extension checked out successfully.")
    except arcpy.ExecuteError:
        arcpy.AddError("Could not check out Spatial Analyst extension.")
        raise

def check_in_extensions():
    # Check in ArcGIS extensions
    arcpy.CheckInExtension("Spatial")
    log_message("Spatial Analyst extension checked in.")

def validate_inputs(*paths):
    # Check that all input paths exist
    for path in paths:
        if not arcpy.Exists(path):
            arcpy.AddError(f"Input does not exist: {path}")
            raise FileNotFoundError(f"Input does not exist: {path}")

def calculate_canopy_height(dsm_input, dem_input, output_path):
    # Calculate and save canopy height (DSM - DEM)
    dsm = Float(Raster(dsm_input))
    dem = Float(Raster(dem_input))
    canopy = dsm - dem
    canopy.save(output_path)
    log_message(f"Canopy height raster saved to {output_path}")
    return output_path

def reclassify_canopy_height(canopy_height_raster, output_path):
    # Reclassify canopy height to create canopy cover raster
    reclass_rules = (
        "-200 3 0;"
        "3 300 1"
    )
    reclass_raster = Reclassify(canopy_height_raster, "VALUE", reclass_rules, "DATA")
    reclass_raster.save(output_path)
    log_message(f"Canopy height reclass raster saved to {output_path}")
    return output_path

import arcpy
from arcpy.sa import *

def calculate_canopy_cover(chm_raster, threshold_meters, output_path):
    # Create binary canopy mask (1 for canopy, 0 for non-canopy)
    chm = Float(Raster(chm_raster))
    canopy_mask = Con(chm > threshold_meters, 1, 0)
    canopy_mask.save(output_path)
    
    # Convert raster to numpy array to calculate pixel sums
    arr = arcpy.RasterToNumPyArray(canopy_mask, nodata_to_value=0)
    
    canopy_pixels = arr.sum()  # sum of pixels with value 1
    total_pixels = arr.size     # total number of pixels
    
    if total_pixels == 0:
        cover_pct = 0.0
    else:
        cover_pct = (canopy_pixels / total_pixels) * 100
    
    arcpy.AddMessage(f"Canopy Cover: {cover_pct:.1f}%")
    return cover_pct

def create_obstacles_layer(canopy_height_raster, output_path):
    # Create an obstacle raster by reclassifying canopy height
    reclass_rules = (
        "-100 0 0;"
        "0 1 1;"
        "1 3 2;"
        "3 200 3"
    )
    obstacle = Reclassify(canopy_height_raster, "VALUE", reclass_rules, "NODATA")
    obstacle.save(output_path)
    log_message(f"Obstacles raster saved to {output_path}")
    return output_path

def calculate_irrigation_efficiency(ndvi_input, slope_raster, canopy_height_raster, output_path):
    # Calculate irrigation efficiency raster
    ndvi = Raster(ndvi_input)
    slopes = Float(Raster(slope_raster))
    canopy = Float(Raster(canopy_height_raster))
    irrigation_efficiency = ndvi * (1 - slopes / 100) * canopy
    irrigation_efficiency.save(output_path)
    log_message(f"Irrigation efficiency raster saved to {output_path}")
    return output_path

def reclassify_irrigation_efficiency(irrigation_efficiency_raster, output_path):
    # Reclassify irrigation efficiency raster
    reclass_rules = (
        "-50 0 0;"
        "0 0.2 1;"
        "0.2 0.4 2;"
        "0.4 0.6 3;"
        "0.6 0.8 4;"
        "0.8 1 5;"
        "1 50 6"
    )
    ir_eff_reclass = Reclassify(irrigation_efficiency_raster, "VALUE", reclass_rules, "NODATA")
    ir_eff_reclass.save(output_path)
    log_message(f"Irrigation efficiency reclassified raster saved to {output_path}")
    return output_path

def convert_canopy_cover_to_polygon(canopy_cover_raster, output_polygon):
    # Convert canopy cover raster to polygon for tree canopy (value = 5)
    # Create a raster layer for selection
    raster_layer = "canopy_cover_layer"
    arcpy.management.MakeRasterLayer(canopy_cover_raster, raster_layer)
    arcpy.management.SelectLayerByAttribute(raster_layer, "NEW_SELECTION", "Value = 5")
    arcpy.conversion.RasterToPolygon(
        raster_layer,
        output_polygon,
        "SIMPLIFY",
        "Value",
        "MULTIPLE_OUTER_PART",
        None
    )
    log_message(f"Canopy cover polygon saved to {output_polygon}")
    return output_polygon

def extract_ndvi_excluding_trees(ndvi_field_boundary, canopy_cover_polygon, output_path):
    # Extract NDVI values from field boundaries excluding tree canopy
    ndvi_field_raster = ExtractByMask(ndvi_field_boundary, canopy_cover_polygon, "OUTSIDE")
    ndvi_field_raster.save(output_path)
    log_message(f"NDVI field boundary excluding trees saved to {output_path}")
    return output_path

def reclassify_slope_for_equipment(slope_raster, output_path):
    # Reclassify slope raster for equipment steepness
    reclass_rules = "0 5 0;5 15 1;15 100 2"
    slope_reclass = Reclassify(slope_raster, "VALUE", reclass_rules, "NODATA")
    slope_reclass.save(output_path)
    log_message(f"Slope steepness raster for equipment saved to {output_path}")
    return output_path

def main():
    check_out_extensions()
    try:
        # Set overwrite to True
        arcpy.env.overwriteOutput = True

        # Get parameters
        dsm_input = arcpy.GetParameterAsText(0)
        dem_input = arcpy.GetParameterAsText(1)
        slope_raster = arcpy.GetParameterAsText(2)
        workspace = arcpy.GetParameterAsText(3)
        ndvi_input = arcpy.GetParameterAsText(4)
        ndvi_field_boundary = arcpy.GetParameterAsText(5)

        # Validate inputs
        validate_inputs(dsm_input, dem_input, slope_raster, ndvi_input, ndvi_field_boundary)

        arcpy.env.workspace = workspace

        # Define output paths
        canopy_height_path = os.path.join(workspace, "Canopy_Height")
        reclass_canopy_height = os.path.join(workspace, "Canopy_Height_Reclass")
        canopy_cover = os.path.join(workspace, "Canopy_Cover")
        irrigation_efficiency_path = os.path.join(workspace, "Irrigation_Efficiency")
        irrigation_eff_reclass_path = os.path.join(workspace, "Irrigation_Efficiency_Reclass")
        canopy_cover_polygon_path = os.path.join(workspace, "Canopy_Cover_Trees_Polygon")
        ndvi_excl_trees_path = os.path.join(workspace, "NDVI_Field_Boundary_Excluding_Trees")
        obstacles_reclass_path = os.path.join(workspace, "Equipment_Obstacles")
        slope_steepness_path = os.path.join(workspace, "Steepness_For_Equipment")

        # Processing steps
        canopy_height = calculate_canopy_height(dsm_input, dem_input, canopy_height_path)
        canopy_height_reclass = reclassify_canopy_height(canopy_height, reclass_canopy_height)
        cover_pct = calculate_canopy_cover(canopy_height, 3, canopy_cover)
        obstacles = create_obstacles_layer(canopy_height, obstacles_reclass_path)
        irrigation_eff = calculate_irrigation_efficiency(ndvi_input, slope_raster, canopy_height, irrigation_efficiency_path)
        irrigation_eff_reclass = reclassify_irrigation_efficiency(irrigation_eff, irrigation_eff_reclass_path)
        canopy_polygon = convert_canopy_cover_to_polygon(canopy_cover, canopy_cover_polygon_path)
        ndvi_excl_trees = extract_ndvi_excluding_trees(ndvi_field_boundary, canopy_polygon, ndvi_excl_trees_path)
        slope_steepness = reclassify_slope_for_equipment(slope_raster, slope_steepness_path)

        log_message("Step 6 processing complete.")

    except Exception as e:
        arcpy.AddError(f"Error: {e}")
        raise
    finally:
        check_in_extensions()

if __name__ == "__main__":
    main()
