import os;

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sympy import *

from database_reader_functions.AddMPIDToManifest import *
import database_reader_functions.structure_reader as sbr;
import settings
from database_reader_functions import battery_base_reader as bbr
from database_reader_functions import materials_project_reader as mbf;
from feature_miner_functions import SymmetryFeatures as BsymF
import sys
'''
SLOWEST FEATURES TO MINE
'''

plt.close("all")

directory = os.path.join(settings.ROOT_DIR,'Battery_Explorer');
structureDir = os.path.join(settings.ROOT_DIR, 'structure_database');

testcounter = 0; datframerows = list(); symmetryMatrix = list();

for filename in os.listdir(directory):
    testcounter+=1;
    try:
        #if(testcounter>2): break;
        print('file no. ' + str(testcounter))
        batterydata = bbr.readBattery(filename);
        #print(data)

        for i in range(len(batterydata['adj_pairs'])):
            dischargeState = batterydata['adj_pairs'][i];

            if(batterydata['adj_pairs'][i]['max_delta_volume'] == 0):
                print(batterydata['battid']);
                continue;

            unlithiatedmpid = batterydata['adj_pairs'][i]['id_charge'];
            lithiatedmpid = batterydata['adj_pairs'][i]['id_discharge']
            mpfile = unlithiatedmpid+'.txt'; mpfile2 = lithiatedmpid+'.txt';

            #try:
            [matdata, structuredata] = mbf.readCompound(mpfile)
            [matdatalith, structuredatalith] = mbf.readCompound(mpfile2)
            structureClassUnLith = sbr.readStructure(unlithiatedmpid);

            ##================SYMMETRY DATA================================#
            [symmetrydata, symmetryLabels] = BsymF.GetAllSymmetries(structureClassUnLith);
            print(symmetrydata)
            symmetryMatrix.append(symmetrydata);
            datframerows.append(filename.strip('+.txt') + ', ' + matdata['pretty_formula'] + ', ' + matdatalith['pretty_formula']
                                + ', ' + matdata['material_id'] + ', ' + matdatalith['material_id'])

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        #raise
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("mpid: " + unlithiatedmpid)
        AddMPIDtoManifest(lithiatedmpid);
        AddMPIDtoManifest(unlithiatedmpid);
        print(exc_type, fname, exc_tb.tb_lineno)




labels = symmetryLabels;
# print(labels);
print(len(labels))
names = labels;

symmetryMatrix = np.array(symmetryMatrix);

TotalData = symmetryMatrix
# Create separate csv files for the structures and for the atomistic

# atomisticMatrix = np.concatenate((atomisticMatrix,np.array(v2).reshape((len(v2),4))), axis = 1)
# BANDGAP IS AN EXCELLENT PREDICTOR!!!!!!!!!!!!!

print('data shape:' + str(TotalData.shape));
print('length of labels: ' + str(len(labels)));

datframe = pd.DataFrame(TotalData, columns=labels, index=datframerows);
datframe.to_csv(os.path.join(settings.ROOT_DIR, 'data_dump', 'SymmetryFeatures.csv'));

