'''
Step 3 - Terrain Analysis Product Generation Script
----------------------------------------------------
Script created by Robert Grow 4/2025

Automates the generation of a suite of terrain analysis products from a DEM and DSM using ArcPy in ArcGIS Pro.
'''

import os
import arcpy

def log_message(message):
    # Log a message to ArcGIS
    arcpy.AddMessage(message)

def calculate_hillshade(input_raster, output_path):
    # Calculate hillshade for a raster surface.
    arcpy.ddd.HillShade(input_raster, output_path, 315, 45, "NO_SHADOWS", 1)
    log_message(f"Hillshade created: {output_path}")

def calculate_surface_parameters(input_raster, output_path, parameter_type, z_unit="Meter", slope_type="PERCENT_RISE"):
    # Calculate surface parameters (slope, aspect, curvature, etc.) for a raster.
    arcpy.ddd.SurfaceParameters(
        input_raster,
        output_path,
        parameter_type,
        "QUADRATIC",
        "1 Meters",
        "FIXED_NEIGHBORHOOD",
        z_unit,
        slope_type,
        "GEODESIC_AZIMUTHS",
        "NORTH_POLE_ASPECT",
        None
    )
    log_message(f"{parameter_type} raster created: {output_path}")

def process_dem_products(input_raster, workspace, prefix):
    # Generate all DEM/DSM derivative products for a given raster
    calculate_hillshade(input_raster, os.path.join(workspace, f"{prefix}_Hillshade"))
    calculate_surface_parameters(
        input_raster, os.path.join(workspace, f"{prefix}_Slope_Degree"),
        "SLOPE", slope_type="DEGREE"
    )
    calculate_surface_parameters(
        input_raster, os.path.join(workspace, f"{prefix}_Slope_Percent_Rise"),
        "SLOPE", slope_type="PERCENT_RISE"
    )
    calculate_surface_parameters(
        input_raster, os.path.join(workspace, f"{prefix}_Aspect"),
        "ASPECT"
    )
    calculate_surface_parameters(
        input_raster, os.path.join(workspace, f"{prefix}_Mean_Curvature"),
        "MEAN_CURVATURE"
    )
    calculate_surface_parameters(
        input_raster, os.path.join(workspace, f"{prefix}_Profile_Curvature"),
        "PROFILE_CURVATURE"
    )
    calculate_surface_parameters(
        input_raster, os.path.join(workspace, f"{prefix}_Tangential_Curvature"),
        "TANGENTIAL_CURVATURE"
    )
    calculate_surface_parameters(
        input_raster, os.path.join(workspace, f"{prefix}_Plan_Curvature"),
        "CONTOUR_CURVATURE"
    )
    calculate_surface_parameters(
        input_raster, os.path.join(workspace, f"{prefix}_Gaussian_Curvature"),
        "GAUSSIAN_CURVATURE"
    )
    calculate_surface_parameters(
        input_raster, os.path.join(workspace, f"{prefix}_Casorati_Curvature"),
        "CASORATI_CURVATURE"
    )

def main():
    try: 
        # Set overwrite to True
        arcpy.env.overwriteOutput = True

        # Get input parameters
        Input_DEM = arcpy.GetParameterAsText(0)
        Input_DSM = arcpy.GetParameterAsText(1)
        Workspace = arcpy.GetParameterAsText(2)
        arcpy.env.workspace = Workspace

        # Process DEM and DSM products
        process_dem_products(Input_DEM, Workspace, "DEM")
        process_dem_products(Input_DSM, Workspace, "DSM")

        log_message("Terrain analysis product generation complete.")
    
    except Exception as e:
        arcpy.AddError(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
