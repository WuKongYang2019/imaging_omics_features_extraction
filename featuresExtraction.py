import argparse
import os

import six
from radiomics import featureextractor
from tqdm import tqdm
from pylab import mpl
import SimpleITK as sitk
import numpy as np
import pandas as pd
from sympy import *
import radiomics


def clearR(re):
    del re['diagnostics_Versions_PyRadiomics']
    del re['diagnostics_Versions_Numpy']
    del re['diagnostics_Versions_SimpleITK']
    del re['diagnostics_Versions_PyWavelet']
    del re['diagnostics_Versions_Python']
    del re['diagnostics_Configuration_Settings']
    #del re['diagnostics_Configuration_EnabledImageTypes']
    del re['diagnostics_Image-original_Hash']
    del re['diagnostics_Image-original_Spacing']
    del re['diagnostics_Image-original_Size']
    #del re['diagnostics_Mask-original_BoundingBox']
    del re['diagnostics_Mask-original_VoxelNum']
    del re['diagnostics_Mask-original_VolumeNum']
    del re['diagnostics_Mask-original_CenterOfMassIndex']
    del re['diagnostics_Mask-original_CenterOfMass']
    del re['diagnostics_Mask-original_Hash']
    del re['diagnostics_Configuration_EnabledImageTypes']
    #del re['diagnostics_Configuration_Settings']
    #del re['diagnostics_Image-original_Hash']
    #del re['diagnostics_Image-original_Size']
    #del re['diagnostics_Image-original_Spacing']
    del re['diagnostics_Mask-original_BoundingBox']
    #del re['diagnostics_Mask-original_CenterOfMass']
    #del re['diagnostics_Mask-original_CenterOfMassIndex']
    #del re['diagnostics_Mask-original_Hash']
    del re['diagnostics_Mask-original_Size']
    del re['diagnostics_Mask-original_Spacing']
    #del re['diagnostics_Versions_Numpy']
    #del re['diagnostics_Versions_PyRadiomics']
    #del re['diagnostics_Versions_PyWavelet']
    #del re['diagnostics_Versions_Python']
    #del re['diagnostics_Versions_SimpleITK']
    return re

def getData(extractor,rootPath='newData'):
    ADCFiles = pd.DataFrame([])
    fl = [name for name in os.listdir(rootPath) if os.path.isdir(os.path.join(rootPath, name))]
    parent_path=[os.path.join(rootPath, i) for i in fl]
    n=0
    allNum=len(parent_path)
    with tqdm(total=len(parent_path), desc=f'FileNum:{allNum}', unit='file') as pbar:
        for PatientData in parent_path:
            listSeries = [name for name in os.listdir(PatientData) ]
            for i in listSeries:
                if 'mask'not in i:
                    imagepath=os.path.join(PatientData,i)
                    (filepath, tempfilename) = os.path.split(imagepath)
                    (filename, extension) = os.path.splitext(tempfilename)
                    maskpath = os.path.join(filepath, filename + '-mask.nii.gz')
                    reader = sitk.ReadImage(maskpath)
                    img1 = sitk.GetArrayFromImage(reader)
                    re = {}
                    re['name'] = filename
                    try:
                        reader = sitk.ReadImage(maskpath)
                        img2 = sitk.GetArrayFromImage(reader)
                        try:
                            result = extractor.execute(imagepath, maskpath)
                            for key, val in six.iteritems(result):
                                re[key] = val
                            re = clearR(re)
                            re['error'] = ''
                            re['ImageMatrix'] = img1.shape
                            re['MaskMatrix'] = img2.shape
                            ADCFiles=ADCFiles.append(pd.DataFrame([re]), ignore_index=True)
                            print('找到%s个特征' % len(re))
                        except:
                            re['error'] = 'Image和Mask尺寸不符合，需要重画'
                            ADCFiles=ADCFiles.append(pd.DataFrame([re]), ignore_index=True)
                        break
                    except:
                        re['name'] = filename
                        re['error'] = '没有找到Mask文件'
                        ADCFiles=ADCFiles.append(pd.DataFrame([re]), ignore_index=True)
                        print('mask文件没有找到')
            pbar.update(1)
            n+=1
    na = ADCFiles['name']
    ADCFiles.drop(labels=['name'], axis=1, inplace=True)
    ADCFiles.insert(0, 'name', na)
    current_path = os.path.abspath(__file__)
    (filepath, tempfilename) = os.path.split(current_path)
    print(ADCFiles)
    dest=os.path.join(filepath,'radiomics1-60.xlsx')
    ADCFiles.to_excel(dest)
    print('extraction down')


def get_args():#get arguments from
    parser = argparse.ArgumentParser(description='Predict masks from input images')
    parser.add_argument('--input', '-i',type=str, default='',help='Directory of input images')
    #parser.add_argument('--dest', '-d', type=str, default='', help='Directory of output file')
    return parser.parse_args()

if __name__ == '__main__':
    mpl.rcParams['font.sans-serif'] = ['FangSong']  # 指定默认字体
    params = 'exampleCT.yaml'
    # RadiomicsFeaturesExtractor has been renamed to RadiomicsFeatureExtractor since pyradiomics2.2.0
    extractor = featureextractor.RadiomicsFeatureExtractor(params)
    # settings = {}
    # settings['binWidth'] = 25
    # settings['resampledPixelSpacing'] = None  # [3,3,3]
    # settings['interpolator'] = sitk.sitkBSpline
    # settings['enableCExtensions'] = True
    #
    # extractor = featureextractor.RadiomicsFeatureExtractor(**settings)
    parser=get_args()
    if(parser.input!=''):
        getData(extractor,parser.input)
    else: getData(extractor)
