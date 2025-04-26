'''
Script created by Robert Grow 4/2025

This script provides a robust, modular, and automated workflow for generating multiple vegetation and soil indices from remote sensing data, facilitating comprehensive spatial analysis and decision-making.
'''

import arcpy
from arcpy.sa import *

def check_out_extensions():
    # Check out required ArcGIS extensions
    arcpy.CheckOutExtension("Spatial")

def check_in_extensions():
    # Check in ArcGIS extensions.
    arcpy.CheckInExtension("Spatial")

def normalize_band(band_raster):
    # Convert band raster to float and normalize to 0-1
    return Float(Raster(band_raster)) / 255.0

def calculate_evi(nir, red, blue, output_path):
    # Calculate and save the Enhanced Vegetation Index (EVI)
    evi = 2.5 * ((nir - red) / (nir + (6.0 * red) - (7.5 * blue) + 1.0))
    evi_calc = Con(evi < -1, -1, Con(evi > 1, 1, evi))
    evi_calc.save(output_path)
    arcpy.AddMessage(f"EVI saved to {output_path}")

def reclassify_evi(evi_raster, output_path):
    # Reclassify EVI raster into vegetation health classes
    arcpy.ddd.Reclassify(
        evi_raster, "VALUE",
        "-1 -0.1 0;-0.100000 0.1 1;0.100000 0.300000 2;0.300000 0.500000 3;0.500000 0.8 4;0.800000 1 5",
        output_path, "NODATA"
    )
    arcpy.AddMessage(f"EVI reclassified raster saved to {output_path}")

def compare_evi_ndvi(evi_raster, ndvi_raster, output_path):
    # Calculate and save the difference between EVI and NDVI rasters
    compare = Raster(evi_raster) - Raster(ndvi_raster)
    compare.save(output_path)
    arcpy.AddMessage(f"EVI-NDVI difference saved to {output_path}")

def calculate_msavi(nir, red, output_path):
    # Calculate and save the MSAVI index
    msavi = (2 * nir + 1 - SquareRoot(Square(2 * nir + 1) - 8 * (nir - red))) / 2
    msavi.save(output_path)
    arcpy.AddMessage(f"MSAVI saved to {output_path}")

def calculate_msavi2(nir, red, output_path):
    # Calculate and save the MSAVI2 index
    msavi2 = 0.5 * (2 * (nir + 1) - SquareRoot(Square(2 * nir + 1) - 8 * (nir - red)))
    msavi2.save(output_path)
    arcpy.AddMessage(f"MSAVI2 saved to {output_path}")

def calculate_clg(nir, green, output_path):
    # Calculate and save the Chlorophyll Index - Green (CLG)
    clg = (nir / green) - 1
    clg.save(output_path)
    arcpy.AddMessage(f"CLG saved to {output_path}")

def calculate_gndvi(nir, green, output_path):
    # Calculate and save the Green NDVI (GNDVI)
    gndvi = (nir - green) / (nir + green)
    gndvi.save(output_path)
    arcpy.AddMessage(f"GNDVI saved to {output_path}")

def calculate_iron_oxide_ratio(red, blue, output_path):
    # Calculate and save the Iron Oxide Ratio index
    iron_oxide_ratio = red / blue
    iron_oxide_ratio.save(output_path)
    arcpy.AddMessage(f"Iron Oxide Ratio saved to {output_path}")

def calculate_mtvi2(nir, red, green, output_path):
    # Calculate and save the MTVI2 index 
    numerator = 1.5 * (1.2 * (nir - green) - 2.5 * (red - green))
    denominator = SquareRoot((2 * nir + 1)**2 - (6 * nir - 5 * SquareRoot(red)) - 0.5)
    mtvi2 = numerator / denominator
    mtvi2.save(output_path)
    arcpy.AddMessage(f"MTVI2 saved to {output_path}")

def calculate_ndwi(green, nir, output_path):
    # Calculate and save the NDWI index
    ndwi = (green - nir) / (green + nir)
    ndwi.save(output_path)
    arcpy.AddMessage(f"NDWI saved to {output_path}")

def calculate_simple_ratio(nir, red, output_path):
    # Calculate and save the Simple Ratio (SR) index
    sr = nir / red
    sr.save(output_path)
    arcpy.AddMessage(f"Simple Ratio saved to {output_path}")

def calculate_vari(green, red, blue, output_path):
    # Calculate and save the VARI index
    vari = (green - red) / (green + red - blue)
    vari.save(output_path)
    arcpy.AddMessage(f"VARI saved to {output_path}")

def reclassify_ndvi(ndvi_raster, output_path):
    # Reclassify NDVI to show crop available (1) or no crop (0)
    ndvi_reclass = arcpy.sa.Reclassify(ndvi_raster, "VALUE", "-1 0 0;0 0.290000 1;0.290000 1.000000 2", "DATA")
    ndvi_reclass.save(output_path)
    arcpy.AddMessage(f"NDVI reclassified for field boundary saved to {output_path}")

def main():
    check_out_extensions()
    
    try:
        # Get input parameters
        Band_1_Input = arcpy.GetParameterAsText(0)
        Band_2_Input = arcpy.GetParameterAsText(1)
        Band_3_Input = arcpy.GetParameterAsText(2)
        Band_4_Input = arcpy.GetParameterAsText(3)
        NDVI_Input = arcpy.GetParameterAsText(4)
        Workspace = arcpy.GetParameterAsText(5)

        # Set workspace
        arcpy.env.workspace = Workspace

        # Output paths
        EVI_Output = f"{Workspace}\\EVI"
        EVI_NDVI_Output = f"{Workspace}\\EVI_Compared_To_NDVI"
        MSAVI_Output = f"{Workspace}\\MSAVI"
        MSAVI2_Output = f"{Workspace}\\MSAVI2"
        CLG_Output = f"{Workspace}\\CLG"
        EVI_Reclass = f"{Workspace}\\EVI_Reclass"
        GNDVI_Output = f"{Workspace}\\GNDVI"
        Iron_Oxide_Ratio_Output = f"{Workspace}\\Iron_Oxide_Ratio"
        MTVI2_Output = f"{Workspace}\\MTVI2"
        NDWI_Output = f"{Workspace}\\NDWI"
        SR_Output = f"{Workspace}\\Simple_Ratio"
        VARI_Output = f"{Workspace}\\VARI"
        NDVI_Field_Boundary = f"{Workspace}\\NDVI_Field_Boundary"

        # Normalize bands
        nir = normalize_band(Band_4_Input)
        red = normalize_band(Band_1_Input)
        blue = normalize_band(Band_3_Input)
        green = normalize_band(Band_2_Input)

        # Calculate indices and outputs
        calculate_evi(nir, red, blue, EVI_Output)
        reclassify_evi(EVI_Output, EVI_Reclass)
        compare_evi_ndvi(EVI_Output, NDVI_Input, EVI_NDVI_Output)
        calculate_msavi(nir, red, MSAVI_Output)
        calculate_msavi2(nir, red, MSAVI2_Output)
        calculate_clg(nir, green, CLG_Output)
        calculate_gndvi(nir, green, GNDVI_Output)
        calculate_iron_oxide_ratio(red, blue, Iron_Oxide_Ratio_Output)
        calculate_mtvi2(nir, red, green, MTVI2_Output)
        calculate_ndwi(green, nir, NDWI_Output)
        calculate_simple_ratio(nir, red, SR_Output)
        calculate_vari(green, red, blue, VARI_Output)
        reclassify_ndvi(NDVI_Input, NDVI_Field_Boundary)

    finally:
        check_in_extensions()

if __name__ == "__main__":
    main()
