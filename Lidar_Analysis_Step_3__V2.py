'''
Script created by Robert Grow 4/2025

This Python script automates the generation of a comprehensive suite of terrain analysis products from both a Digital Elevation Model (DEM) and a Digital Surface Model (DSM) using ArcPy in ArcGIS Pro.
'''

import arcpy

def calculate_hillshade(input_raster, output_path):
    # Calculate hillshade for a raster surface.
    arcpy.ddd.HillShade(input_raster, output_path, 315, 45, "NO_SHADOWS", 1)
    arcpy.AddMessage(f"Hillshade created: {output_path}")

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
    arcpy.AddMessage(f"{parameter_type} raster created: {output_path}")

def process_dem_products(input_raster, workspace, prefix):
    # Generate all DEM/DSM derivative products for a given raster.
    
    # Hillshade
    calculate_hillshade(input_raster, f"{workspace}\\{prefix}_Hillshade")
    
    # Slope Degree
    calculate_surface_parameters(input_raster, f"{workspace}\\{prefix}_Slope_Degree", "SLOPE", slope_type="DEGREE")
    
    # Slope Percent Rise
    calculate_surface_parameters(input_raster, f"{workspace}\\{prefix}_Slope_Percent_Rise", "SLOPE", slope_type="PERCENT_RISE")
    
    # Aspect
    calculate_surface_parameters(input_raster, f"{workspace}\\{prefix}_Aspect", "ASPECT")
    
    # Mean Curvature
    calculate_surface_parameters(input_raster, f"{workspace}\\{prefix}_Mean_Curvature", "MEAN_CURVATURE")
    
    # Profile Curvature
    calculate_surface_parameters(input_raster, f"{workspace}\\{prefix}_Profile_Curvature", "PROFILE_CURVATURE")
    
    # Tangential Curvature
    calculate_surface_parameters(input_raster, f"{workspace}\\{prefix}_Tangential_Curvature", "TANGENTIAL_CURVATURE")
    
    # Plan Curvature (Contour Curvature)
    calculate_surface_parameters(input_raster, f"{workspace}\\{prefix}_Plan_Curvature", "CONTOUR_CURVATURE")
    
    # Gaussian Curvature
    calculate_surface_parameters(input_raster, f"{workspace}\\{prefix}_Gaussian_Curvature", "GAUSSIAN_CURVATURE")
    
    # Casorati Curvature
    calculate_surface_parameters(input_raster, f"{workspace}\\{prefix}_Casorati_Curvature", "CASORATI_CURVATURE")

def main():
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

if __name__ == "__main__":
    main()
