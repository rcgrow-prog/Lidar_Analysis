'''
Script created by Robert Grow 4/2025

Canopy, Irrigation, and Equipment Suitability Analysis Script

This script processes DSM, DEM, Slope, and NDVI rasters to generate canopy height,
canopy cover, irrigation efficiency, obstacles, and equipment suitability outputs.
Intended for agricultural/forestry spatial analysis in ArcGIS.

Inputs:
    0 - DSM Raster
    1 - DEM Raster
    2 - Slope Raster
    3 - Workspace
    4 - NDVI Raster
    5 - NDVI Field Boundary Raster

Outputs:
    Various rasters and polygons saved to the workspace.
'''

import arcpy
from arcpy.sa import *

def check_out_extensions():
    # Check out required ArcGIS extensions
    try:
        arcpy.CheckOutExtension("Spatial")
        arcpy.AddMessage("Spatial Analyst extension checked out successfully.")
    except arcpy.ExecuteError:
        arcpy.AddError("Could not check out Spatial Analyst extension.")
        raise

def check_in_extensions():
    # Check in ArcGIS extensions
    arcpy.CheckInExtension("Spatial")
    arcpy.AddMessage("Spatial Analyst extension checked in.")

def validate_inputs(*paths):
    # Check that all input paths exist
    for path in paths:
        if not arcpy.Exists(path):
            arcpy.AddError(f"Input does not exist: {path}")
            raise FileNotFoundError(f"Input does not exist: {path}")

def calculate_canopy_height(dsm_input, dem_input, output_path):
    # Calculate and save canopy height (DSM - DEM)
    try:
        dsm = Float(Raster(dsm_input))
        dem = Float(Raster(dem_input))
        canopy = dsm - dem
        canopy.save(output_path)
        arcpy.AddMessage(f"Canopy height raster saved to {output_path}")
        return output_path
    except Exception as e:
        arcpy.AddError(f"Error calculating canopy height: {e}")
        raise

def reclassify_canopy_height(canopy_height_raster, output_path):
    # Reclassify canopy height to create canopy cover raster
    try:
        arcpy.ddd.Reclassify(
            canopy_height_raster, "VALUE",
            "-200 0 0;0 0.100000 1;0.100000 0.300000 2;0.300000 0.500000 3;0.500000 0.700000 4;0.700000 300.000000 5",
            output_path, "DATA"
        )
        arcpy.AddMessage(f"Canopy cover raster saved to {output_path}")
        return output_path
    except Exception as e:
        arcpy.AddError(f"Error reclassifying canopy height: {e}")
        raise

def create_obstacles_layer(canopy_height_raster, output_path):
    # Create an obstacle raster by reclassifying canopy height
    try:
        obstacle = arcpy.sa.Reclassify(
            canopy_height_raster, "VALUE",
            "-100.000000 0 0;0 1 1;1 3 2;3 200.000000 3",
            "NODATA"
        )
        obstacle.save(output_path)
        arcpy.AddMessage(f"Obstacles raster saved to {output_path}")
        return output_path
    except Exception as e:
        arcpy.AddError(f"Error creating obstacles layer: {e}")
        raise

def calculate_irrigation_efficiency(ndvi_input, slope_raster, canopy_height_raster, output_path):
    # Calculate irrigation efficiency raster
    try:
        ndvi = Raster(ndvi_input)
        slopes = Float(Raster(slope_raster))
        canopy = Float(Raster(canopy_height_raster))
        irrigation_efficiency = ndvi * (1 - slopes / 100) * canopy
        irrigation_efficiency.save(output_path)
        arcpy.AddMessage(f"Irrigation efficiency raster saved to {output_path}")
        return output_path
    except Exception as e:
        arcpy.AddError(f"Error calculating irrigation efficiency: {e}")
        raise

def reclassify_irrigation_efficiency(irrigation_efficiency_raster, output_path):
    # Reclassify irrigation efficiency raster
    try:
        ir_eff_reclass = arcpy.sa.Reclassify(
            irrigation_efficiency_raster, "VALUE",
            "-50.00000 0 0;0 0.200000 1;0.200000 0.400000 2;0.400000 0.600000 3;0.600000 0.800000 4;0.800000 1 5;1 50.00000 6",
            "NODATA"
        )
        ir_eff_reclass.save(output_path)
        arcpy.AddMessage(f"Irrigation efficiency reclassified raster saved to {output_path}")
        return output_path
    except Exception as e:
        arcpy.AddError(f"Error reclassifying irrigation efficiency: {e}")
        raise

def convert_canopy_cover_to_polygon(canopy_cover_raster, output_polygon):
    # Convert canopy cover raster to polygon for tree canopy (value = 5)
    try:
        arcpy.management.SelectLayerByAttribute(canopy_cover_raster, "NEW_SELECTION", "Value = 5", None)
        arcpy.conversion.RasterToPolygon(
            canopy_cover_raster, output_polygon, "SIMPLIFY", "Value",
            "MULTIPLE_OUTER_PART", None
        )
        arcpy.AddMessage(f"Canopy cover polygon saved to {output_polygon}")
        return output_polygon
    except Exception as e:
        arcpy.AddError(f"Error converting canopy cover to polygon: {e}")
        raise

def extract_ndvi_excluding_trees(ndvi_field_boundary, canopy_cover_polygon, output_path):
    # Extract NDVI values from field boundaries excluding tree canopy
    try:
        ndvi_field_raster = arcpy.sa.ExtractByMask(
            ndvi_field_boundary, canopy_cover_polygon, "OUTSIDE", ""
        )
        ndvi_field_raster.save(output_path)
        arcpy.AddMessage(f"NDVI field boundary excluding trees saved to {output_path}")
        return output_path
    except Exception as e:
        arcpy.AddError(f"Error extracting NDVI excluding trees: {e}")
        raise

def reclassify_slope_for_equipment(slope_raster, output_path):
    # Reclassify slope raster for equipment steepness
    try:
        slope_reclass = arcpy.sa.Reclassify(
            slope_raster, "VALUE", "0 5 0;5 15 1;15 100 2", "NODATA"
        )
        slope_reclass.save(output_path)
        arcpy.AddMessage(f"Slope steepness raster for equipment saved to {output_path}")
        return output_path
    except Exception as e:
        arcpy.AddError(f"Error reclassifying slope for equipment: {e}")
        raise

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

        # Validate inputs
        validate_inputs(DSM_Input, DEM_Input, Slope_Raster, Workspace, NDVI_Input, NDVI_Field_Boundary)

        # Set workspace
        arcpy.env.workspace = Workspace

        # Set the output file paths
        Canopy_Height = f"{Workspace}\\Canopy_Height"
        Canopy_Cover = f"{Workspace}\\Canopy_Cover"
        Irrigation_Efficiency_Output = f"{Workspace}\\Irrigation_Efficiency"
        Irrigation_Eff_Reclass = f"{Workspace}\\Irrigation_Efficiency_Reclass"
        Canopy_Cover_to_Polygon = f"{Workspace}\\Canopy_Cover_Trees_Polygon"
        NDVI_Field_Boundary_Excluding_Trees = f"{Workspace}\\NDVI_Field_Boundary_Excluding_Trees"
        Obstacles_Reclass = f"{Workspace}\\Equipment_Obstacles"
        Slope_Steepness = f"{Workspace}\\Steepness_For_Equipment"

        # Processing steps
        canopy_height = calculate_canopy_height(DSM_Input, DEM_Input, Canopy_Height)
        canopy_cover = reclassify_canopy_height(canopy_height, Canopy_Cover)
        obstacles = create_obstacles_layer(canopy_height, Obstacles_Reclass)
        irrigation_eff = calculate_irrigation_efficiency(NDVI_Input, Slope_Raster, canopy_height, Irrigation_Efficiency_Output)
        irrigation_eff_reclass = reclassify_irrigation_efficiency(irrigation_eff, Irrigation_Eff_Reclass)
        canopy_polygon = convert_canopy_cover_to_polygon(canopy_cover, Canopy_Cover_to_Polygon)
        ndvi_excl_trees = extract_ndvi_excluding_trees(NDVI_Field_Boundary, canopy_polygon, NDVI_Field_Boundary_Excluding_Trees)
        slope_steepness = reclassify_slope_for_equipment(Slope_Raster, Slope_Steepness)

    finally:
        check_in_extensions()

if __name__ == "__main__":
    main()
