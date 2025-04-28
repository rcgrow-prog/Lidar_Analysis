"""
Step 5 - Vegetation and Soil Indices Generation Script
------------------------------------------------------
Script created by Robert Grow 4/2025

This script provides a modular, automated workflow for generating multiple
vegetation and soil indices from remote sensing data, facilitating comprehensive
spatial analysis and decision-making.
"""

import os
import arcpy
from arcpy.sa import *

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

def normalize_band(band_raster):
    # Convert band raster to float and normalize to 0-1
    return Float(Raster(band_raster)) / 255.0

def log_message(message):
    # Log messages to ArcGIS
    arcpy.AddMessage(message)

def calculate_evi(nir, red, blue, output_path):
    # Calculate and save the Enhanced Vegetation Index (EVI)
    evi = 2.5 * ((nir - red) / (nir + (6.0 * red) - (7.5 * blue) + 1.0))
    evi_calc = Con(evi < -1, -1, Con(evi > 1, 1, evi))
    evi_calc.save(output_path)
    log_message(f"EVI saved to {output_path}")

def reclassify_evi(evi_raster, output_path):
    # Reclassify EVI raster into vegetation health classes
    reclass_rules = (
        "-1 -0.1 0;"
        "-0.1 0.1 1;"
        "0.1 0.3 2;"
        "0.3 0.5 3;"
        "0.5 0.8 4;"
        "0.8 1 5"
    )
    arcpy.ddd.Reclassify(evi_raster, "VALUE", reclass_rules, output_path, "NODATA")
    log_message(f"EVI reclassified raster saved to {output_path}")

def compare_evi_ndvi(evi_raster, ndvi_raster, output_path):
    # Calculate and save the difference between EVI and NDVI rasters
    compare = Raster(evi_raster) - Raster(ndvi_raster)
    compare.save(output_path)
    log_message(f"EVI-NDVI difference saved to {output_path}")

def calculate_msavi(nir, red, output_path):
    # Calculate and save the MSAVI index
    msavi = (2 * nir + 1 - SquareRoot(Square(2 * nir + 1) - 8 * (nir - red))) / 2
    msavi.save(output_path)
    log_message(f"MSAVI saved to {output_path}")

def calculate_msavi2(nir, red, output_path):
    # Calculate and save the MSAVI2 index
    msavi2 = 0.5 * (2 * (nir + 1) - SquareRoot(Square(2 * nir + 1) - 8 * (nir - red)))
    msavi2.save(output_path)
    log_message(f"MSAVI2 saved to {output_path}")

def calculate_clg(nir, green, output_path):
    # Calculate and save the Chlorophyll Index - Green (CLG)
    clg = (nir / green) - 1
    clg.save(output_path)
    log_message(f"CLG saved to {output_path}")

def calculate_gndvi(nir, green, output_path):
    # Calculate and save the Green NDVI (GNDVI)
    gndvi = (nir - green) / (nir + green)
    gndvi.save(output_path)
    log_message(f"GNDVI saved to {output_path}")

def calculate_iron_oxide_ratio(red, blue, output_path):
    # Calculate and save the Iron Oxide Ratio index
    iron_oxide_ratio = red / blue
    iron_oxide_ratio.save(output_path)
    log_message(f"Iron Oxide Ratio saved to {output_path}")

def calculate_mtvi2(nir, red, green, output_path):
    # Calculate and save the MTVI2 index
    numerator = 1.5 * (1.2 * (nir - green) - 2.5 * (red - green))
    denominator = SquareRoot((2 * nir + 1)**2 - (6 * nir - 5 * SquareRoot(red)) - 0.5)
    mtvi2 = numerator / denominator
    mtvi2.save(output_path)
    log_message(f"MTVI2 saved to {output_path}")

def calculate_ndwi(green, nir, output_path):
    # Calculate and save the NDWI index
    ndwi = (green - nir) / (green + nir)
    ndwi.save(output_path)
    log_message(f"NDWI saved to {output_path}")

def calculate_simple_ratio(nir, red, output_path):
    # Calculate and save the Simple Ratio (SR) index
    sr = nir / red
    sr.save(output_path)
    log_message(f"Simple Ratio saved to {output_path}")

def calculate_vari(green, red, blue, output_path):
    # Calculate and save the VARI index
    vari = (green - red) / (green + red - blue)
    vari.save(output_path)
    log_message(f"VARI saved to {output_path}")

def reclassify_ndvi(ndvi_raster, output_path):
    # Reclassify NDVI to show crop available (1) or no crop (0)
    reclass_rules = "-1 0 0;0 0.29 1;0.29 1 2"
    ndvi_reclass = arcpy.sa.Reclassify(ndvi_raster, "VALUE", reclass_rules, "DATA")
    ndvi_reclass.save(output_path)
    log_message(f"NDVI reclassified for field boundary saved to {output_path}")

def main():
    check_out_extensions()
    try:
        # Get input parameters
        band_1 = arcpy.GetParameterAsText(0)  # Red
        band_2 = arcpy.GetParameterAsText(1)  # Green
        band_3 = arcpy.GetParameterAsText(2)  # Blue
        band_4 = arcpy.GetParameterAsText(3)  # NIR
        ndvi_input = arcpy.GetParameterAsText(4)
        workspace = arcpy.GetParameterAsText(5)

        if not all([band_1, band_2, band_3, band_4, ndvi_input, workspace]):
            raise ValueError("All input parameters must be provided.")

        arcpy.env.workspace = workspace

        # Output paths
        outputs = {
            "evi": os.path.join(workspace, "EVI"),
            "evi_ndvi": os.path.join(workspace, "EVI_Compared_To_NDVI"),
            "msavi": os.path.join(workspace, "MSAVI"),
            "msavi2": os.path.join(workspace, "MSAVI2"),
            "clg": os.path.join(workspace, "CLG"),
            "evi_reclass": os.path.join(workspace, "EVI_Reclass"),
            "gndvi": os.path.join(workspace, "GNDVI"),
            "iron_oxide": os.path.join(workspace, "Iron_Oxide_Ratio"),
            "mtvi2": os.path.join(workspace, "MTVI2"),
            "ndwi": os.path.join(workspace, "NDWI"),
            "sr": os.path.join(workspace, "Simple_Ratio"),
            "vari": os.path.join(workspace, "VARI"),
            "ndvi_field": os.path.join(workspace, "NDVI_Field_Boundary"),
        }

        # Normalize bands
        nir = normalize_band(band_4)
        red = normalize_band(band_1)
        blue = normalize_band(band_3)
        green = normalize_band(band_2)

        # Calculate indices and outputs
        calculate_evi(nir, red, blue, outputs["evi"])
        reclassify_evi(outputs["evi"], outputs["evi_reclass"])
        compare_evi_ndvi(outputs["evi"], ndvi_input, outputs["evi_ndvi"])
        calculate_msavi(nir, red, outputs["msavi"])
        calculate_msavi2(nir, red, outputs["msavi2"])
        calculate_clg(nir, green, outputs["clg"])
        calculate_gndvi(nir, green, outputs["gndvi"])
        calculate_iron_oxide_ratio(red, blue, outputs["iron_oxide"])
        calculate_mtvi2(nir, red, green, outputs["mtvi2"])
        calculate_ndwi(green, nir, outputs["ndwi"])
        calculate_simple_ratio(nir, red, outputs["sr"])
        calculate_vari(green, red, blue, outputs["vari"])
        reclassify_ndvi(ndvi_input, outputs["ndvi_field"])

    except Exception as e:
        arcpy.AddError(f"Error: {e}")
        raise
    finally:
        check_in_extensions()

if __name__ == "__main__":
    main()
