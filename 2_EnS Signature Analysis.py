
# Import arcpy module
import arcpy
# Import spatial analysis module from arcpy
from arcpy.sa import *
# Import module for path operation
import os
import sys
import winsound
import datetime
from sklearn.metrics import cohen_kappa_score
# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")
time_format = '%d-%m-%Y- %H:%M:%S'
time_now = datetime.datetime.now()
time_str = time_now.strftime(time_format)
time_start = time_str


# Allow to overwrite previous files
arcpy.env.overwriteOutput = True
print("Maximum Likelihood Classification: Signature Analysis")
print("        Start Time:  " + str(time_str))
print("")
# version number
version = "v7a"
sig_file = "wc_1_4_ens_sig_" + version + ".gsg"

# parameters need to set
input_ens = "E:\\CIMP6_EnS_Analysis_2021-2040\\WorldClim_Signature_Analysis\\GEnSv3\\gens_v3"

in_path = "E:\\CIMP6_EnS_Analysis_2021-2040\\CIMP6_Variables\\WorldClim_1_4_30s\\"
# in_path = "E:\\CIMP6_EnS_Analysis_2021-2040\\CIMP6_Variables_Test\\WorldClim-2_1_30s\\"

table = "E:\\CIMP6_EnS_Analysis_2021-2040\\EnS_v3_Attribute_Table\\ens_v3.dbf"
out_path = "E:\\CIMP6_EnS_Analysis_2021-2040\\WorldClim_Signature_Analysis\\"
input_class_label = "VALUE"
ens_acc = out_path + "ens_acc_" + version

print("    GEnS File:  " + input_ens)
print("    Input Variables:  " + in_path)

# # should be ok from here
out_ens = out_path + "ens_sig_" + version
aridity_index = in_path + "aridity_index"
pet_sd = in_path + "pet_sd"
tmean_deg_day = in_path + "tmean_deg_day"
tmean_sd = in_path + "tmean_sd"


vr_list = [aridity_index, pet_sd, tmean_deg_day, tmean_sd]

out_con = out_path + "ens_con"
out_sig = out_path + sig_file

print("    Out_EnS:  " + out_ens)
print("    Signature File Name:  " + sig_file)
print("    Overall Accuracy Grid:  " + ens_acc)
print("")

arcpy.AddMessage("     Creating Signature File:  " + sig_file)
arcpy.gp.CreateSignatures_sa(vr_list, input_ens, out_sig, "COVARIANCE", input_class_label)
#CreateSignatures(vr_list, input_ens, out_sig, "COVARIANCE", input_class_label)

arcpy.AddMessage("     Creating New Ens:  " + out_ens)
arcpy.gp.MLClassify_sa(vr_list, out_sig, out_ens, "0.0", "EQUAL", "", "")

del aridity_index
del pet_sd
del tmean_deg_day
del tmean_sd
del out_con
arcpy.JoinField_management(out_ens, "VALUE", table, "ENS_VALUE", "")

arcpy.AddMessage("Calculating Overall Accuracy")

acc_grid = Con(Raster(input_ens) == Raster(out_ens), 1, 0)
acc_grid.save(ens_acc)

print( "   Updating Table:")
srows = arcpy.UpdateCursor(ens_acc)
for srow in srows:
    if srow.VALUE == 1:
        a = srow.COUNT
    else:
        b = srow.COUNT

sum = a + b
overall_acc = str(round(float(a) / float(sum), 3))
arcpy.AddMessage("Overall Accuracy is " + overall_acc)

arcpy.AddMessage("Calculating Kappa Coefficient (cohen k)")
kappa_table = out_path + "kappa_table_" + version + ".dbf"
arcpy.gp.ZonalStatisticsAsTable_sa(out_ens, "VALUE", ens_acc, kappa_table, "DATA", "SUM")
del out_ens
srows = arcpy.UpdateCursor(kappa_table)

for srow in srows:
    a1 = srow.COUNT
    b1 = srow.SUM
    # p_0 = float(b1) / float(sum)
    p_0 = (b1) / (sum)
nrows = arcpy.UpdateCursor(input_ens)
a2 = 0
for nrow in nrows:
    if nrow.VALUE == srow.VALUE:
        a2 = nrow.COUNT
p_c = (a1 * a2) / (sum * sum)
# p_c = float(a1 * a2) / float(sum * sum)
kappa = (p_0 - p_c) / (1 - p_c)


del input_ens
del kappa_table

kappa = str(round(kappa, 4))
arcpy.AddMessage("Kappa Coefficient is " + kappa)



arcpy.env.workspace = out_path
xmlfiles = arcpy.ListFiles("*.xml")
for xmlfile in xmlfiles:
    os.remove(out_path + xmlfile)
del xmlfile


arcpy.AddMessage("Finished Maximum Likelihood Classification")

log_txt = "Ens Signature Analysis: " + sig_file + "\n"
log_txt = log_txt + "Start time is:       " + time_start + "\n"
log_txt = log_txt + "Input path is:   " + in_path + "\n" + "Output path is:   " + out_path + "\n"
log_txt = log_txt + "overall accuracy = " + overall_acc + "\n" + "cohen kappa = " + kappa + "\n"

log_name = sig_file.rstrip(".gsg") + ".txt"
log_file = open(out_path + log_name, "w")
log_file.write(log_txt)

print("     End Time:  " + str(datetime.datetime.now()))
print("")
print("Finished")
winsound.Beep(500, 1000)
winsound.Beep(500, 1000)
