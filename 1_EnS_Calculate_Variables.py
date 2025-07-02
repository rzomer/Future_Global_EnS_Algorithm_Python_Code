# Purpose: Calculate variables for use in EnS Analysis (ML_Classify):  for worldclim
# Written by Robert Zomer,


#These parameters need to be set by user:
# The directory where you put all climate data for all models (historical and projected)
in_path = "E:\\CIMP6_EnS_Files_2021-2040\\"
# The path where you put your results
out_path = "E:\\CIMP6_Variables_2021-2040\\"

# Import arcpy module
import arcpy
from arcpy.sa import *
import os
import winsound
arcpy.CheckOutExtension("spatial")
import datetime
# Allow to overwrite previous files
arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor = "0%"
# Set the output cell size, the same as climate data
arcpy.env.cellSize = 0.00833
 # Set mask extent
arcpy.env.mask = ("E:\\CIMP6_EnS_Model_Analysis\\Mask_World_Boundary\\Mask_World_Boundary_Grid\\mask_v3")
# The path where you put the monthly extraterestrial solar radiation and solar days
sn_path = "E:\\CIMP6_EnS_Model_Analysis\\ET_Solar_Radiation\\"

print("  ")
print("EnS_Calculate_Variables:")
time_format = '%Y-%m-%d %H:%M:%S'
time_now = datetime.datetime.now()
time_str = time_now.strftime(time_format)
time_start_all = time_str
print("        Start Time:  " + str(time_str))
print("")
print("This script will calculate the variables required for the EnS Analysis, including PET_AI:")
print("for all scenarios found within a directory. Input is monthly climate data, i.e. tmean, tmin, tmax, prec:")
print("     ")
print("   in_path  = " + in_path)
print("   out_path = " + out_path)
print("   sn_path =  " + sn_path)
print("")
obj_id = 1
# Set the workspace to the folder containing all model names
arcpy.env.workspace = in_path
 # List the all models in the folder
models = arcpy.ListFiles()

# List of Available Models:
# "ACCESS-CM2", "ACCESS-ESM1-5", "CanESM5", "CanESM5-CanOE", "CMCC-ESM2", "CNRM-CM6-1", "CNRM-CM6-1-HR", "CNRM-ESM2-1",
# "EC-Earth3-Veg", "EC-Earth3-Veg-LR", "FIO-ESM-2-0", "GFDL-ESM4", "GISS-E2-1-G", "GISS-E2-1-H", "HadGEM3-GC31-LL",
# "INM-CM4-8", "INM-CM5-0", "IPSL-CM6A-LR", "MIROC-ES2L", "MIROC6", "MPI-ESM1-2-HR", "MPI-ESM1-2-LR", "MRI-ESM2-0", "UKESM1-0-LL",

print("   Included Models: =  " + str(models))
print("")
for model in models:
    print("Processing Model: " + model)
    time_now = datetime.datetime.now()
    time_str = time_now.strftime(time_format)
    print("    Start Time:  " + str(time_str))
    print("")
    # Set the workspace to the folder containing all scenario names
    arcpy.env.workspace = in_path + model
    scenarios = arcpy.ListFiles("*126")
    for scenario in scenarios:
        print("Dataset #" + str(obj_id))
        time_now = datetime.datetime.now()
        time_str = time_now.strftime(time_format)
        time_start = time_str
        print("        Start Time:  " + str(time_str))
        print("Model:  " + model)
        print("Scenario:  " + scenario)
        out_dir_name = model + "_" + scenario.lstrip("ssp")
        out_dir_path = out_path + out_dir_name + "\\"
        print("Out_Directory:  " + model + "_" + scenario.lstrip("ssp"))
        if os.path.exists(out_dir_path) == True:
            obj_id += 1
            print("    Directory Already Exists:")
            print("")
        else:
            os.mkdir(out_dir_path)
            print("       Processing Monthly Temperature:")
            # Calculate monthly mean temperature and monthly PET
            for i in range(1,13):
                if i < 10:
                    month = "0" + str(i)
                else:
                    month = str(i)
                # Calculate monthly mean temperature, tmean = (tmax + tmin) / 2
                tmax_month = arcpy.Raster(in_path + model + "\\" + scenario + "\\wc2.1_30s_tmax_" + month + ".tif")
                tmin_month = arcpy.Raster(in_path + model + "\\" + scenario + "\\wc2.1_30s_tmin_" + month + ".tif")
                tmean_month = (tmax_month + tmin_month) * 0.5
                tmean_month.save(out_dir_path + "tmean_" + str(i))
                # Calculate monthly temperature range, td = tmax - tmin
                td_month = (tmax_month - tmin_month)
                # Delete tmax_month and tmin_month
                del tmax_month
                del tmin_month
                # Calculate monthly PET with the Hargreaves method
                nday_month = arcpy.Raster(sn_path + "ndays\\nday_" + str(i))
                solrad_month = arcpy.Raster(sn_path + "solrad\\solrad_" + str(i))
                pet_month = (nday_month * 0.0023 * solrad_month * (tmean_month + 17.8) * (td_month**0.5))
                pet_month = Con(pet_month > 0, pet_month, 0)
                pet_month.save(out_dir_path + "pet_" + str(i))
                # Delete td_month, tmean_month, nday_month, solrad_month
                del td_month
                del tmean_month
                del nday_month
                del solrad_month
                del pet_month
                print('\r' "          Month_" + str(i), end="")
            print("")
            print("       Processing Annual Temperature:")
            arcpy.env.workspace = out_dir_path
            # print("Workspace"  + str(arcpy.env.workspace))
            # print("Out Directory Path:   " + out_dir_path)
            tmean_files = arcpy.ListRasters("tmean*", "GRID")
            print("               Temperature Seasonality")
            # Temperature seasonality - tmean_sd is calculated as the standard deviation of the monthly distribution of mean temperature
            tmean_sd = CellStatistics(tmean_files, "STD", "DATA")
            tmean_sd.save(out_dir_path + "tmean_sd")
            print("               Annual Mean Temperature")
            # Annual mean temperature - tmean_yr is the average of mean temperature for the 12 months
            tmean_yr = CellStatistics(tmean_files, "MEAN", "DATA")
            # print("tmean_yr cell statistics processed")
            tmean_yr.save(out_dir_path + "tmean_yr")
            # Delete variables
            del tmean_yr
            del tmean_files
            del tmean_sd
            print("       Processing Growing Degree Days")
            #  Growing degree days on a 0 base (GDD) is calculated as the sum of days in a year when the mean monthly temperature is higher than 0
            for j in range(1,13):
                # if j < 10:
                #     out_month = "0" + str(j)
                # else:
                #     out_month = str(j)
                arcpy.gp.Con_sa(out_dir_path + "tmean_" + str(j), \
                                out_dir_path + "\\" + "tmean_" + str(j), out_dir_path + "gdd_" + str(j), "0", "\"VALUE\" > 0")
                print('\r' "          Month_" + str(j), end="")
            print("       Processing Annual Growing Degree Days")
            gdd_1 = arcpy.Raster(out_dir_path + "gdd_1")
            gdd_2 = arcpy.Raster(out_dir_path + "gdd_2")
            gdd_3 = arcpy.Raster(out_dir_path + "gdd_3")
            gdd_4 = arcpy.Raster(out_dir_path + "gdd_4")
            gdd_5 = arcpy.Raster(out_dir_path + "gdd_5")
            gdd_6 = arcpy.Raster(out_dir_path + "gdd_6")
            gdd_7 = arcpy.Raster(out_dir_path + "gdd_7")
            gdd_8 = arcpy.Raster(out_dir_path + "gdd_8")
            gdd_9 = arcpy.Raster(out_dir_path + "gdd_9")
            gdd_10 = arcpy.Raster(out_dir_path + "gdd_10")
            gdd_11 = arcpy.Raster(out_dir_path + "gdd_11")
            gdd_12 = arcpy.Raster(out_dir_path + "gdd_12")
            print("       Calculating Degree Days")
            tmean_deg_day = gdd_1 * 31 + gdd_2 * 28 + gdd_3 * 31 + gdd_4 * 30 + gdd_5 * 31 + gdd_6 * 30 \
                            + gdd_7 * 31 + gdd_8 * 31 + gdd_9 * 30 + gdd_10 * 31 + gdd_11 * 30 + gdd_12 * 31
            print("          Creating Integer - Degree Days")
            tmean_deg_day_int = Int(tmean_deg_day)
            print("          Saving - Degree Days")
            tmean_deg_day_int.save(out_dir_path + "tmean_deg_day")
            print("          Cleaning Directories")
            # Delete gdd_month and tmean_deg_day
            del gdd_1
            del gdd_2
            del gdd_3
            del gdd_4
            del gdd_5
            del gdd_6
            del gdd_7
            del gdd_8
            del gdd_9
            del gdd_10
            del gdd_11
            del gdd_12
            del tmean_deg_day
            del tmean_deg_day_int
            print("       Processing PET files")
            # List the PET of 12 months
            arcpy.env.workspace = out_dir_path
            pet_files = arcpy.ListRasters("pet_*", "GRID")
            print("          Annual PET")
            # Calculate annual PET - pet_yr
            pet_year = Int(CellStatistics(pet_files, "SUM", "DATA"))
            pet_year.save(out_dir_path + "pet_yr")
            print("          PET Seasonality")
            # Calculate PET seasonality - pet_sd
            pet_sd = Int(CellStatistics(pet_files, "STD", "DATA"))
            pet_sd.save(out_dir_path + "pet_sd")
            # Delete pet_files and pet_sd
            del pet_files
            del pet_sd
            # Calculate annual precipitation
            print("       Calculating Annual Precipitation")
            arcpy.env.workspace = in_path + model + "\\" + scenario + "\\"
            prec_files = arcpy.ListRasters("wc2.1_30s_prec_*", "")
            prec_year = (CellStatistics(prec_files[0:len(prec_files)], "SUM", "DATA"))
            prec_year.save(out_dir_path + "prec_yr")
            # Delete prec_files
            del prec_files
            print("       Processing Aridity Index")
            # Calculate aridity index, which is the ratio of annual precipitation over annual PET
            aridity_index = (prec_year / pet_year)
            aridity_index.save(out_dir_path + "aridity_index")
            # Delete prec_year, pet_year, aridity_index
            del prec_year
            del pet_year
            del aridity_index
            print("       Processing Annual Max Temp")
            # List maximum temperature of 12 months
            # arcpy.env.workspace = in_path + model + "\\"
            tmax_files = arcpy.ListRasters("wc2.1_30s_tmax_*", "")
            # Calculate annual mean maximum temperature
            tmax_year = CellStatistics(tmax_files[0:len(tmax_files)], "MEAN", "DATA")
            tmax_year.save(out_dir_path + "tmax_yr")
            # Delete tmax_files
            del tmax_files
            del tmax_year
            print("       Processing Annual Min Temp")
            # List minimum temperature of 12 months
            tmin_files = arcpy.ListRasters("wc2.1_30s_tmin_*", "")
            # Calculate annual mean minimum temperature
            tmin_year = CellStatistics(tmin_files[0:len(tmin_files)], "MEAN", "DATA")
            tmin_year.save(out_dir_path + "tmin_yr")
            print("       Cleaning Directories")
            # Delete tmin_files
            del tmin_files
            del tmin_year
            # Delete monthly PET, tmean, gdd
            for i in range(1,13):
                arcpy.Delete_management(out_dir_path + "pet_" + str(i), "RasterDataset")
                arcpy.Delete_management(out_dir_path + "gdd_" + str(i), "RasterDataset")
                arcpy.Delete_management(out_dir_path + "tmean_" + str(i), "RasterDataset")
            tif_files = arcpy.ListRasters("*", "TIFF")
            for tif in tif_files:
                arcpy.Delete_management(tif)
            print("Finished Calculation for Dataset:  " + model + " : " + scenario)
            time_now = datetime.datetime.now()
            time_str = time_now.strftime(time_format)
            print("      Start Time:  " + str(time_start))
            print("        End Time:  " + str(time_str))
            print("     ")
            obj_id += 1
print("")
print("Process finished successfully.   All variables have been calculated for " + str(obj_id - 1) + " datasets")
print("     ")
print("All datasets completed")
print("   Start Time:  " + str(time_start_all))
time_now = datetime.datetime.now()
time_str = time_now.strftime(time_format)
print("     End Time:  " + str(time_str))
print("")
print("Finished")
winsound.Beep(500, 1000)
winsound.Beep(500, 1000)

