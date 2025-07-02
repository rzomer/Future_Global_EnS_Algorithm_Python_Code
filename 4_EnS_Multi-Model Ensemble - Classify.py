# Purpose:  Ensemble EnS Analysis (ML_Classify) based on Majority of included models:
# Written by Robert Zomer

# Import arcpy module
import arcpy
from arcpy.sa import *
import os
import winsound
arcpy.CheckOutExtension("spatial")
import datetime
import textwrap as tr
# Allow to overwrite previous files
arcpy.env.overwriteOutput = True
# arcpy.env.parallelProcessingFactor = "85%"
# Set the output cell size, the same as climate data
arcpy.env.cellSize = 0.00833

# Set mask extent - need mask or results not good
arcpy.env.mask = ("E:\\CIMP6_EnS_Model_Analysis\\Mask_World_Boundary\\Mask_World_Boundary_Grid\\mask_v3")
#These parameters need to be set by user:



# The directory where you put all climate data for all models (historical and projected)

# in_path = "E:\\CIMP6_EnS_Classifications_2021-2040\\"
in_path = "E:\\CIMP6_EnS_Classifications_2041-2060\\"

# The path where you put your results
# out_path = "E:\\CIMP6_EnS_Ensemble_2021-2040\\"
out_path = "E:\\CIMP6_EnS_Ensemble_2041-2060\\"

year = str(in_path[-11:-1])

for i in range(3):
    if i == 0:
        included_models = ["ACCESS-CM2", "CanESM5", "CanESM5-CanOE", "HadGEM3-GC31-LL", "UKESM1-0-LL"]
        out_file = "EnS_High-Risk" + year

    if i == 1:
        included_models = ["ACCESS-ESM1-5", "CMCC-ESM2", "CNRM-CM6-1", "CNRM-CM6-1-HR", "CNRM-ESM2-1", \
                           "GISS-E2-1-G", "GISS-E2-1-H", "INM-CM4-8", "INM-CM5-0", "IPSL-CM6A-LR", "MIROC-ES2L", "MIROC6", \
                           "MPI-ESM1-2-HR", "MPI-ESM1-2-LR", "MRI-ESM2-0"]

        out_file = "EnS_Consensus" + year
    if i == 2:
        included_models = ["ACCESS-CM2", "ACCESS-ESM1-5", "CanESM5", "CanESM5-CanOE", "CMCC-ESM2", "CNRM-CM6-1", "CNRM-CM6-1-HR", \
                           "CNRM-ESM2-1", "FIO-ESM-2-0", "GFDL-ESM4", "GISS-E2-1-G", "GISS-E2-1-H", "HadGEM3-GC31-LL", "INM-CM4-8", \
                           "INM-CM5-0", "IPSL-CM6A-LR", "MIROC-ES2L", "MIROC6", "MPI-ESM1-2-HR", "MPI-ESM1-2-LR", "MRI-ESM2-0", "UKESM1-0-LL"]
        out_file = "EnS_All" + year

    number_of_included_models = len(included_models)
    ens_table = "E:\\CIMP6_EnS_Model_Analysis\\EnS_v3_Attribute_Table\\ens_v3.dbf"
    print("  ")
    print("Processing Multi_Model Ensemble:  " + out_file)

    time_format = '%d-%m-%Y- %H:%M:%S'
    time_now = datetime.datetime.now()
    time_str = time_now.strftime(time_format)
    time_start_all = time_str

    print("        Start Time:  " + str(time_str))

    print("")
    print(" ** This script will calculate a multi-model EnS ensemble using the Majority of Classifications per pixel of all the models included in the ensemble")

    print("     ")
    print("   in_path  = " + in_path)
    print("   out_path = " + out_path)
    print("   out_file = " + out_file)
    print("     ")

    # Set the workspace to the folder containing all model names
    arcpy.env.workspace = in_path

    print(tr.fill("Included Models: " + str(included_models), width=800, initial_indent="              "))
    print("    Number of Included Models: " + str(number_of_included_models))
    print("")

    # create scenario dictionaries
    ssp_126 = []
    ssp_245 = []
    ssp_370 = []
    ssp_585 = []
    ssps = [ssp_126, ssp_245, ssp_370, ssp_585]

    scenarios = arcpy.ListRasters("*", "TIF")
    # add included scenarios to the scenario dictionary
    for scenario in scenarios:
        no_ens_model = str(scenario.lstrip("ens_"))
        # print("ens_model: " + no_ens_model)
        model_name = no_ens_model.rsplit("_")
        # print("model_name: " + model_name[0])
        # print("model: " + model)
        if (model_name[0]) in (included_models):
            # print("  Model included: " + scenario)
            if "_126" in scenario:
                ssp_126.append(scenario)
            elif "_245" in scenario:
                ssp_245.append(scenario)
            elif "_370" in scenario:
                ssp_370.append(scenario)
            elif "_585" in scenario:
                ssp_585.append(scenario)
    ssp_126.sort()
    ssp_245.sort()
    ssp_370.sort()
    ssp_585.sort()

    # loop thru the scenario dictionaries
    for ssp in ssps:
        # set out_file names
        if ssp == ssp_126:
            out_scenario = out_file + "_126"
            ens_intermediate_file = "sem_126"
        elif ssp == ssp_245:
            out_scenario = out_file + "_245"
            ens_intermediate_file = "sem_245"
        elif ssp == ssp_370:
            out_scenario = out_file + "_370"
            ens_intermediate_file = "sem_370"
        elif ssp == ssp_585:
            out_scenario = out_file + "_585"
            ens_intermediate_file = "sem_585"

        print("Processing Scenario:  " + out_scenario)
        time_now = datetime.datetime.now()
        time_str = time_now.strftime(time_format)
        print("   Start Time:  " + str(time_str))
        number_of_scenarios = len(ssp)
        print("       Number Included Scenarios: " + str(number_of_scenarios))
        print(tr.fill("       Included Scenarios: " + str(ssp), width=172))

        if os.path.exists(out_path + out_scenario + ".tif") == True:
            print("        File already exists: " + out_scenario)
            print("")
        elif len(ssp) != 0:
            # arcpy.env.mask = ssp[0]
            # Set the workspace to the folder containing all model names
            arcpy.env.workspace = in_path
            print("  Calculating Majority:  ")
            print("       CellStatistics")

            ens_unfill = CellStatistics(ssp[0:len(ssp)], "MAJORITY", "DATA")
            ens_unfill.save(out_path + ens_intermediate_file + "_un")

            print("       Set Null")
            ens_fill = Con(IsNull(ens_unfill), 0, ens_unfill)
            ens_fill.save(out_path + ens_intermediate_file + "_fil")

            print("       Nibble")
            ens_file = Nibble(ens_fill, ens_unfill, "DATA_ONLY")
            ens_file.save(out_path + out_scenario + ".tif")

            print("       Clean Directories")
            arcpy.Delete_management(ens_fill, "RasterDataset")
            arcpy.Delete_management(ens_unfill, "RasterDataset")
            del ens_fill
            del ens_unfill


            print("  Joining Attribute Table")
            arcpy.JoinField_management(out_path + out_scenario + ".tif", "VALUE", ens_table, "ENS_VALUE", "")

            print("  Processing Prevalence:")
            print("       Comparison with:")
            times = 1
            for i in ssp:
                ens_model = arcpy.Raster(i)
                # log_txt = log_txt + model + "  "
                arcpy.gp.EqualTo_sa(ens_model, ens_file, out_path + "ps_" + str(times))
                print('\r' "          Model #" + str(times), end="")
                times = times + 1
            del ens_file
            print("")
            print("       CellStatistics")
            arcpy.env.workspace = out_path
            p_ens_models = arcpy.ListRasters("ps_*", "GRID")
            p_ens = CellStatistics(p_ens_models[0:len(p_ens_models)], "MEAN", "DATA")
            p_ens = Float(p_ens * 100)
            p_ens.save(out_path + "p_" + out_scenario + ".tif")

            print("       Cleaning Directories")
            for p_ens_model in p_ens_models:
                arcpy.Delete_management(p_ens_model)
            del p_ens
            del p_ens_models

            xmlfiles = arcpy.ListFiles("*.xml")
            for xmlfile in xmlfiles:
                os.remove(out_path + xmlfile)
            del xmlfiles

            # create readme.txt
            log_txt = "Multi-Model Ensemble using Majority Classification: " + out_file + "\n"
            log_txt = log_txt + "  Script:  Multi-Model Ensemble - Classifications.py" + "\n"
            log_txt = log_txt + "    Start time is:       " + str(time_start_all) + "\n" + "\n"
            log_txt = log_txt + "Input path is:   " + in_path + "\n"
            log_txt = log_txt + "Output path is:   " + out_path + "\n"

            log_txt = log_txt + " Number of Included Models: " + str(number_of_included_models) + "\n"
            log_txt = log_txt + "   Included Models: " + "\n"
            for m in included_models:
                log_txt = log_txt + "         " + str(m) + "\n"
            log_txt = log_txt + "\n"

            log_txt = log_txt + "Out_file is:   " + out_scenario.rstrip("\\") + ".tif" + "\n" + "\n"
            log_txt = log_txt + "\n"
            log_txt = log_txt + " Number of Included Scenarios: " + str(len(ssp)) + "\n"
            log_txt = log_txt + "   Included Scenarios: " + "\n"
            for i in ssp:
                log_txt = log_txt + "         " + str(i) + "\n"
            log_name = out_scenario.rstrip("\\") + ".txt"
            log_file = open(out_path + log_name, "w")
            log_file.write(log_txt)
            log_file.close()
            del log_txt
            del log_file
        else:
            print("  No models in ssp")
            print("")
            print("    End Time:  " + str(datetime.datetime.now()))


        print("    Finished Calculation for Scenario:  " + out_scenario)
        time_now = datetime.datetime.now()
        time_str = time_now.strftime(time_format)
        print("        End Time:  " + str(time_str))
        print("     ")

print("Finished Calculation for All Datasets: " + out_file)
time_now = datetime.datetime.now()
time_str = time_now.strftime(time_format)
print("      Start Time:  " + str(time_start_all))
print("        End Time:  " + str(time_str))
