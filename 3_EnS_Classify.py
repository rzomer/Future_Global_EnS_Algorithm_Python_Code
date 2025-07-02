# Written by Robert Zomer, Antonio Trabucco, Mingcheng Wang, Kunming Institute of Botany, CHINA  -

# Import arcpy module
import arcpy
from arcpy.sa import *
import os
import winsound
arcpy.CheckOutExtension("spatial")

# Allow to overwrite previous files
arcpy.env.overwriteOutput = True
# arcpy.env.parallelProcessingFactor = "67%"

# Set the output cell size, the same as climate data
arcpy.env.cellSize = 0.00833

#These parameters need to be set by user:




# # The directory where you put all climate data for all models (historical and projected) - previous results from 1_EnS_Calculate_Variables.py
in_path =  "E:\\CIMP6_Variables_2021-2040\\"
# # The path where you put your results
out_path = "E:\\CIMP6_EnS_Classifications_2021-2040_Copy\\"
# ens_sig = "E:\\CIMP6_EnS_Analysis_2021-2040\\WorldClim_Signature_Analysis\\wc_1_4_ens_sig_v7.gsg"
ens_sig = "E:\\CIMP6_EnS_Model_Analysis\\WorldClim_Signature_Analysis\\wc_1_4_ens_sig_v7.gsg"
ens_table = "E:\\CIMP6_EnS_Model_Analysis\\EnS_v3_Attribute_Table\\ens_v3.dbf"
# ens_table = "F:\\CIMP6_EnS_Model_Analysis\\EnS_v3_Attribute_Table\\ens_v3.dbf"

# The directory where you put all climate data for all models (historical and projected)
# in_path = "E:\\CIMP6_EnS_Analysis_2021-2040\\CIMP6_EnS_Classifications\\"
#

# The path where you put your results
# out_path = "E:\\CIMP6_EnS_Analysis_2021-2040\\CIMP6_Classifications\\"


print("  ")
print("EnS_Classify Projections:")

time_format = '%Y-%m-%d %H:%M:%S'
time_now = datetime.datetime.now()
time_str = time_now.strftime(time_format)
print("        Start Time:  " + str(time_str))
print("")

print("This script will classify a new EnS using Maximum Likelihood from the bioclimatic variables,")
print("for all scenarios found within a directory. Input is the calcuated variables")


print("")
print("     In Directory:   " + in_path)
print("     Out Directory:  " + out_path)
print("     Signature File: " + ens_sig)
print("     EnS Table:      " + ens_table)
print("")
print("Processing EnS Classifications:")
print("")
arcpy.env.workspace = in_path
number = 1

# models = []
models = arcpy.ListFiles("CanESM5_126")
for model in models:
    ens_model = out_path + "ens_" + model + ".tif"
    if os.path.exists(ens_model) == True:
        print("Dataset:  " + str(number))
        time_now = datetime.datetime.now()
        time_str = time_now.strftime(time_format)
        print("        Start Time:  " + str(time_str))
        print("    File Already Exists:  " + ens_model)
        print("")
        number += 1
    else:
        if ("info" in model) == False and (".txt" in model) == False and ("log" in model) == False:
            print("Dataset:  " + str(number))
            time_now = datetime.datetime.now()
            time_str = time_now.strftime(time_format)
            print("        Start Time:  " + str(time_str))
            aridity_index = in_path + model + "\\aridity_index"
            pet_sd = in_path + model + "\\pet_sd"
            tmean_deg_day = in_path + model + "\\tmean_deg_day"
            tmean_sd = in_path + model + "\\tmean_sd"

            var_list = [aridity_index, pet_sd, tmean_deg_day, tmean_sd]

            ens_con = out_path + "con_" + str(number)
            ens_name = ens_model

            print("  Processing Model:  " + ens_model)
            arcpy.gp.MLClassify_sa(var_list, ens_sig, ens_name, "0.0", "EQUAL", "", ens_con)

            print("  Cleaning Directories")
            arcpy.Delete_management(ens_con, "RasterDataset")
            del ens_con
            del aridity_index
            del pet_sd
            del tmean_deg_day
            del tmean_sd
            del var_list

            print("  Joining Table")
            arcpy.JoinField_management(ens_name, "VALUE", ens_table, "ENS_VALUE", "")
            del ens_model

            number = number + 1

            time_now = datetime.datetime.now()
            time_str = time_now.strftime(time_format)
            print("     End Time:  " + str(time_str))
            print("")
print("")
print("All Directories Completed")


