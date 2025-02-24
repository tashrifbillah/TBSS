![](doc/pnl-bwh-hms.png)

[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.2662497.svg)](https://doi.org/10.5281/zenodo.2662497) [![Python](https://img.shields.io/badge/Python-3.6-green.svg)]() [![Platform](https://img.shields.io/badge/Platform-linux--64%20%7C%20osx--64-orange.svg)]()

*TBSS* repository is developed by Tashrif Billah, Sylvain Bouix, and Ofer Pasternak, Brigham and Women's Hospital (Harvard Medical School).

If this repository is useful in your research, please cite as below: 

Billah, Tashrif; Bouix, Sylvain; Pasternak, Ofer; Generalized Tract Based Spatial Statistics (TBSS) pipeline,
https://github.com/pnlbwh/tbss, 2019, DOI: https://doi.org/10.5281/zenodo.2662497

See installation instruction [here](./README.md)


Table of Contents
=================
    
   * [Useful commands](#useful-commands)
      * [1. Run ENIGMA TBSS](#1-run-enigma-tbss)
      * [2. Run user template based TBSS](#2-run-user-template-based-tbss)
      * [3. Minimum TBSS](#3-minimum-tbss)
      * [4. ROI analysis](#4-roi-analysis)
      * [5. Check progress](#5-check-progress)
      * [6. Create summary](#6-create-summary)
   * [Overview](#overview)
      * [Step-1: Preprocessing](#step-1-preprocessing)
      * [Step-2: Registration](#step-2-registration)
      * [Step-3: Skeleton creation](#step-3-skeleton-creation)
      * [Step-4: Projection](#step-4-projection)
      * [Step-5: View images](#step-5-view-images)
      * [Step-6: ROI/Voxelwise analysis](#step-6-roivoxelwise-analysis)
   * [Branches/Templates](#branchestemplates)
      * [1. --enigma](#1---enigma)
      * [2. --fmrib](#2---fmrib)
      * [3. --studyTemplate](#3---studytemplate)
      * [4. User template](#4-user-template)
   * [Caselist](#caselist)
   * [Input images](#input-images)
      * [1. With dwi/mask image list](#1-with-dwimask-image-list)
      * [2. With diffusivity image list](#2-with-diffusivity-image-list)
      * [3. With diffusivity image directory](#3-with-diffusivity-image-directory)
   * [Space](#space)
   * [List of outputs](#list-of-outputs)
      * [1. Folders](#1-folders)
      * [2. Files](#2-files)
         * [i. FA/MD/AD/RD](#i-famdadrd)
            * [a. preproc](#a-preproc)
            * [b. origdata](#b-origdata)
            * [c. warped](#c-warped)
            * [d. skeleton](#d-skeleton)
            * [e. roi](#e-roi)
         * [ii. transform/template](#ii-transformtemplate)
         * [iii. log](#iii-log)
         * [iv. stats](#iv-stats)
   * [multi-modality TBSS](#multi-modality-tbss)
   * [List creation](#list-creation)
      * [1. imagelist](#1-imagelist)
      * [2. caselist](#2-caselist)
   * [Analysis](#analysis)
      * [1. ROI analysis](#1-roi-analysis)
         * [i. --lut](#i---lut)
         * [ii. --space](#ii---space)
      * [2. Voxelwise analysis](#2-voxelwise-analysis)
   * [QC](#qc)
   * [Multi threading](#multi-threading)
   * [NRRD support](#nrrd-support)
   * [Reference](#reference)


Table of Contents created by [gh-md-toc](https://github.com/ekalinin/github-markdown-toc)

# Useful commands

## 1. Run ENIGMA TBSS

See details on [ENIGMA](http://enigma.ini.usc.edu/wp-content/uploads/DTI_Protocols/ENIGMA_TBSS_protocol_USC.pdf) TBSS.
    
     lib/tbss_all -i IMAGELIST.csv \
    -c CASELIST.txt \
    --modality FA,MD,AD,RD 
    --enigma \
    -o ~/enigmaTemplateOutput/
    
`IMAGELIST.csv` is a list of FA,MD,AD,RD images in separate columns. A particular diffusivity images for all cases need 
not to be in the same directory. Rather, they can be anywhere in your machine. Just make sure to specify absolute 
path to the diffusivity image in designated column of `IMAGELIST.csv`. See details in [ENIGMA branch](#1---enigma).

**NOTE** For multi-modality like above, make sure to have FA as the first one.

**NOTE** If you don't specify a `CASELIST.txt`, base names for image files are used as caseIDs. However, if you are doing multi-modality TBSS, 
you wouldn't have the luxury of omitting the caselist.

    
## 2. Run user template based TBSS
    
    lib/tbss_all -i FAimageDIR,MDimageDIR \
    --modality FA,MD \
    -c CASELIST.txt \
    --template your_FA.nii.gz \
    --skeleton your_skeleton_FA.nii.gz \
    -o ~/userTemplateOutput/

Alternative to the `IMAGELIST.csv`, you can specify a directory corresponding to each modality you want to analyze. 
However, you have to copy your diffusivity images in a directory. In the very least, the images across `FAimageDIR,MDimageDIR` 
should have caseID from `CASELIST.txt` somewhere in their file names. But it doesn't need to have keyword "FA/MD" in their file names.

On the other hand, `your_FA.nii.gz` and `your_skeleton_FA.nii.gz` are the templates you should provide. 
See details in [User template branch](#4-user-template).


## 3. Minimum TBSS
    
    lib/tbss_all -i FAimageDIR \
    -o ~/fmribuserTemplateOutput
    
Voila! The pipeline will create a study specific template. Default `--modality` is assumed to be **FA**. See details in 
[study template branch](#3---studytemplate).


## 4. ROI analysis

With all the above, you may provide an atlas and a [space](#-space) of the atlas defining image. Then, [ROI based statistics](#roi-analysis) 
will be calculated.

    --labelMap JHU-ICBM-labels-1mm.nii.gz \
    --lut data/ENIGMA_look_up_table.txt \
    --space $FSLDIR/standard/FMRIB58_FA*.nii.gz

Even better, [ENGIMA](#1---enigma) branch does ROI based analysis as default.


## 5. Check progress

If you have a good number of cases to process, and you would like to know how far the pipeline has progressed, 
do the following:

    lib/tbss_all --status --outDir ~/userTemplateOutput/

The `--status` command uses information from `outDir/log/config.ini` to collect information about the ongoing TBSS study. It will print a dashboard like below:

    Output directory:               ~/my_output_directory
    Number of cases to process:     228
    
    Progress of FA TBSS:
    
    origdata obtained:              228
    pre-processed:                  228
    registered to template space:   228
    skeletonized:                   228
    roi-based stat calculated:      228
    
    Time taken so far: 2 days, 17 hours, 54 minutes and 3 seconds

Amazing, isn't it! 

 
## 6. Create summary

Finally, TBSS pipeline can generate an HTML file with skeleton overlaid upon the diffusivity measure for all cases.

    lib/writeHtml.py --dir tbss/output/directory
    
    

# Overview

This is Generalized Tract Based Spatial Statistics (TBSS) pipeline,
encompassing different protocols such as [ENIGMA](http://enigma.ini.usc.edu/wp-content/uploads/DTI_Protocols/ENIGMA_TBSS_protocol_USC.pdf) 
and [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/TBSS/UserGuide). It is elegantly designed so you no longer have to 
deal with naming your folders/files according to a protocol. It uses some command line tools relevant to 
skeleton creation from FSL while replacing all FSL (i.e `flirt`, `applyWarp` etc) registration steps by [ANTs](https://github.com/ANTsX/ANTs). 
In a nutshell, this pipeline should facilitate an user in running TBSS study by giving more liberty with inputs. 
Moreover, it harnesses multiprocessing capability from Python making the program significantly faster than any 
job scheduling framework (i.e lsf).

![](doc/tbss-flowchart.png)


## Step-1: Preprocessing

`tbss_1_preproc *.nii.gz` pre-processes the FA images. It essentially zeros the end slices and erodes the image a little bit. 
It also creates `caseid_FA_mask.nii.gz` that can be used to pre-process non-FA images. `tbss_1_preproc` puts the given FA 
images in [origdata](#origdata) and pre-processed FA images in `FA` directory. The pipeline renames the latter to [preproc](#a-preproc).

As explained above, non-FA images are pre-processed by applying `caseid_FA_mask.nii.gz` directly.


## Step-2: Registration

Each `caseid_FA.nii.gz` are registered to template space. The `caseid_*1Warp.nii.gz` and `caseid_*0GenericAffine.mat` 
transform files are stored in [transform/template](#ii-transformtemplate) directory.

The warp and affine are used to warp `caseid_FA.nii.gz` to template space: `caseid_FA_to_target.nii.gz`. The warped images 
are saved in [warped](#c-warped) directory. Same warp and affine are used to warp non-FA images.


## Step-3: Skeleton creation

If a skeleton is not provided, it is created by `tbss_skeleton` command. `stats/meanFA.nii.gz` is used to create skeleton. 
The `stats/meanFA.nii.gz` is obtained from all the warped images in `warped` directory.

## Step-4: Projection

Each subject diffusivity image is projected upon provided/created skeleton: `{modality}/skeleton/caseid_{modality}_to_target_skel.nii.gz`. 
See `tbss_skeleton --help` for more details about how FA and non-FA images are projected upon skeleton. Also, read [Smith's 
TBSS 2006](https://www.ncbi.nlm.nih.gov/pubmed/16624579) paper to know more about it.

## Step-5: View images

TBSS pipeline can generate an HTML file with skeleton overlaid upon the diffusivity measure for all cases.

    lib/writeHtml.py --dir tbss/output/directory
    
The `tbss/output/directory` is where you have results stored in different subdirectories named after modalities. The 
above script will create a `slicesdir` inside each modality directory while `slicedir/summary.html` file has skeleton 
overlaid upon the diffusivity image for all the cases in `caselist.txt`.



## Step-6: ROI/Voxelwise analysis

Finally, we would like to do analysis on skeletonized data. ROI-based analysis can be done as noted in the [ENIGMA protocol](http://enigma.ini.usc.edu/wp-content/uploads/DTI_Protocols/ENIGMA_ROI_protocol_USC.pdf).
In brief, each `caseid_FA_to_target_skel.nii.gz` is compared against an atlas. The atlas has multiple segments. We calculate
average diffusivity (FA,MD etc.) of each segment and note them in a csv file: `{modality}/roi/caseid_{modality}_roi*.csv`.

Summary of ROI analysis is saved in `stats/{modality}_combined_roi*csv`. The process is detailed in [ROI analysis](#roi-analysis).

On the other hand, skeletonized 4D data `stats/all{modality}_skeletonized.nii.gz` can be used to do [voxelwise analysis](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/TBSS/UserGuide#voxelwise_statistics_on_the_skeletonised_FA_data). 
 

# Branches/Templates

The pipeline has four branches:


## 1. --enigma

ENIGMA provided templates are used with this argument:
    
    enigmaDir= pjoin(LIBDIR, 'data', 'enigmaDTI')
    args.template = pjoin(enigmaDir, 'ENIGMA_DTI_FA.nii.gz')
    args.templateMask = pjoin(enigmaDir, 'ENIGMA_DTI_FA_mask.nii.gz')
    args.skeleton = pjoin(enigmaDir, 'ENIGMA_DTI_FA_skeleton.nii.gz')
    args.skeletonMask = pjoin(enigmaDir, 'ENIGMA_DTI_FA_skeleton_mask.nii.gz')
    args.skeletonMaskDst = pjoin(enigmaDir, 'ENIGMA_DTI_FA_skeleton_mask_dst.nii.gz')
    args.lut = pjoin(enigmaDir, 'ENIGMA_look_up_table.txt')
    
In addition, the following atlas is used for ROI based analysis:
    
    args.labelMap = pjoin(fslDataDir, 'atlases', 'JHU', 'JHU-ICBM-labels-1mm.nii.gz')

## 2. --fmrib

FSL provided templates are used with this argument:
    
    args.template= pjoin(fslDataDir, 'standard', 'FMRIB58_FA_1mm.nii.gz')
    args.skeleton= pjoin(fslDataDir, 'standard', 'FMRIB58_FA-skeleton_1mm.nii.gz')

However, [FreeSurferColorLUT.txt](https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/AnatomicalROI/FreeSurferColorLUT) is used in this branch.
    
On the other hand, this branch does not do ROI based analysis by default. If wanted, the 
user should specify an atlas and corresponding space (if atlas and templates are in different space) 
as follows:

    --labelMap atlas.nii.gz --space MNI.nii.gz
    

Unlike [original TBSS](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/TBSS/UserGuide) approach, we use the [ENIGMA](http://enigma.ini.usc.edu/wp-content/uploads/DTI_Protocols/ENIGMA_ROI_protocol_USC.pdf) approach 
that identifies the direction of projection onto the skeleton based on the individual FA maps rather than on the mean FA map.


## 3. --studyTemplate

With this branch, a study-specific template is created using `antsMultivariateTemplateConstruction2.sh`. 
`tbss_1_preproc INPUTDIR/*.nii.gz` pre-processes the given FA images. 
The pre-processed FA images are used in template construction. Again, the use should provide 
a set of FA images for study specific template construction. 

## 4. User template

Finally, the user can specify any or all of the following:
    
    --template TEMPLATE                 an FA image template (i.e ENIGMA, IIT), 
                                        if not specified, ANTs template will be created from provided images, 
                                        for ANTs template creation, you must provide FA images, 
                                        once ANTs template is created, you can run TBSS on 
                                        non FA images using that template
                                        
    --templateMask TEMPLATEMASK         mask of the FA template, if not provided, one will be created
        
    --skeleton SKELETON                 skeleton of the FA template, if not provided, one will be created
                                        
    --skeletonMask SKELETONMASK         mask of the provided skeleton
    
    --skeletonMaskDst SKELETONMASKDST   skeleton mask distance map
    

** NOTE ** Attributes provided as user templates are mutually exclusive to the ones default with branches specified above. 
In other words, branch specific templates have precedence over user template. 
For example, if `--enigma` is specified, it will override `--template`, `--skeleton` etc specified again.
However, since `--fmrib` comes with only `--template` and `--skeleton`, 
you may specify `--templateMask`, `--skeletonMask` etc. with it. 


# Caselist

Files in each subdirectory start with a caseid obtained from `--caselist`. If a caselist is not specified, then one 
is created from the input images. Such caselist comprise the basenames of images without extension. For example, if 
image path is: `/path/to/001/image001.nii.gz`, then created caseid would be `image001` only.

# Input images

The TBSS pipeline requires input images i.e. FA, MD etc. You may specify the input images as a list 
or as a directory which contains them.

### 1. With dwi/mask image list

For convenience, TBSS can start by creating diffusivity measures: FA, MD, AD, and RD. To let the pipeline create them, 
specify your input DWI/Mask in a text file as follows:

    -i INPUT.csv            a txt/csv file
                            with dwi1,mask1\ndwi2,mask2\n...

In addition, provide the `--generate` flag.

Then, FA, MD, AD, RD are created using either DIPY/FSL diffusion tensor models. Then, TBSS is done for 
specified `--modality`.


### 2. With diffusivity image list 

Alternatively, you can specify a list of diffusivity images sitting in different directories:

                            a txt/csv file with
    -i INPUT.csv            ModImg1\nModImg2\n... ; TBSS will be done for specified Modalities

The pipeline will organize them in proper [directory structure](#1-folders).


### 3. With diffusivity image directory

Finally, to be compatible with FSL/ENGIMA protocols, you may organize your diffusivity images in separate directories. 
Then, you can provide the directories to run TBSS on:
    
    --modality FA,MD,... dir/of/FA/images,dir/of/MD/images,...
    
**NOTE** When specifiying multiple modalities at a time, make sure to correspond your directory to the right modality.


# Space

Provided or created template can be projected to a standard space. For human brain, it should be projected to MNI space. 
However, for rat/other brains, it may be some other standard space. 

If ROI based analysis is to be done using a White-Matter atlas, the template should be projected to the space of the atlas.


# List of outputs

Several files are created down the pipeline. They are organized with following folder hierarchy and naming:
    
## 1. Folders
    
    outDir
       |
    ------------------------------------------------------------------------------------------------------
       |           |             |                |        |       |                   |           |
       |           |             |                |        |       |                   |           |
    transform   template        FA                MD       AD      RD                 log        stats
                                 |       (same inner file structure as that of FA)
                                 |
                    ----------------------------------------
                     |         |         |       |        |
                    preproc  origdata  warped  skeleton  roi
    
    copy all FA into FA directory
    put all preprocessed data into preproc directory
    keep all warp/affine in transform directory
    output all warped images in warped directory
    output all skeletons in skel directory
    output ROI based analysis files in roi directory
    save all ROI statistics, mean, and combined images
    
        
    
## 2. Files
    
The following directories are created inside user specified output directory. Files residing in the nested directories 
are explained below:

### i. FA/MD/AD/RD

TBSS run on one or more specified modalities. The FA, MD, .. directories correspond to the modalities. In each modality 
directory, there are five sub-directories:
    
                FA
                 |
                 |
    ----------------------------------------
     |         |         |       |        |
    preproc  origdata  warped  skeleton  roi
    
    copy all FA into FA directory
    put all preprocessed data into preproc directory
    keep all warp/affine in transform directory
    output all warped images in warped directory
    output all skeletons in skel directory
    output ROI based analysis files in roi directory
    

Files in each subdirectory start with a caseid obtained from `--caselist`.

#### a. preproc

Contains all [`tbss_1_preproc`] processed data.

#### b. origdata

Contains raw diffusivity data. 

In fact `tbss_1_preproc` categorizes raw and preprocessed data into `origdata` and `FA` directories, respectively. 
The pipeline renames `FA` as `preproc` to be harmonious with the genre of data contained within.

#### c. warped

Preprocessed data are warped to template/standard space applying warp and affine obtained from registering each subject 
to the template. `warped` directory contains warped data.

#### d. skeleton

Each subject diffusivity image is projected upon provided/created skeleton. This directory contains projected skeletons in subject space.

#### e. roi

If you choose to do ROI based analysis providing a `--labelMap`, then a `*_roi.csv` file is created for each case containing 
region based statistics. Additionally, if you use `--avg` flag, RIGHT/LEFT regions in the ROIs are averaged. The averaged 
statistics are saved in `*_roi_avg.csv` file.


Several files are created down the pipeline. They are organized with proper folder hierarchy and naming:


    outDir
       |
    -------------------------------------------------------------------------
       |           |          |       |       |       |        |        |
       |           |          |       |       |       |        |        |
    transform   template     FA       MD      AD      RD      log     stats
    
### ii. transform/template

If a template is given, input images are registered with the template. On the other hand, if a template is not 
given/`--studyTemplate` branch is specified, a template is created in the pipeline at `template` directory. 
Corresponding transform files: `*0GenericAffine.mat` and `*1Warp.nii.gz` are created in `transform/template` directory.

Moreover, same directory is used to store transform files if a template is further registered to another space (i.e. MNI).

### iii. log

ANTs registration logs are stored in this directory for each case starting with a caseid. However, the user can print 
all the outputs to `stdout` by `--verbose` option.


### iv. stats

As the name suggests, all statistics are saved in this directory. Statistics include mean and combined modality images, 
csv file containing summary of region based statistics etc.


# multi-modality TBSS

Unlike requiring to save FA TBSS files with a particular name as directed by some protocol, this pipeline is capable of 
running multi-modality TBSS. All you have to do is to make sure, first modality in the specified modalities is FA and 
corresponding input images are FA.

    --modality MODALITY         Modality={FA,MD,AD,RD ...} of images to run TBSS on
            
                                (i) single modality analysis:
                                you must run --modality FA first, then you can run for other modalities such as --modality AD
            
                                (ii) multi modality analysis:
                                first modality must be FA, and then the rest i.e --modality FA,MD,AD,RD,...
                                files from FA TBSS analysis are used in rest of the modalities
                                
    -i INPUT, --input INPUT
                                (i) DWI images and masks:
                                a txt/csv file with dwi1,mask1\ndwi2,mask2\n... ; TBSS will start by creating FA, MD, AD, and RD;
                                additionally, use --generate flag
            
                                (ii) single modality analysis:
                                a directory with one particular Modality={FA,MD,AD,RD,...} images, or
                                a txt/csv file with ModImg1\nModImg2\n...
                                TBSS will be done for specified Modality
            
                                (iii) multi modality analysis:
                                comma-separated multiple input directories corresponding to the sequence of --modality, or
                                a txt/csv file with Mod1_Img1,Mod2_Img1,...\nMod1_Img2,Mod2_Img2,...\n... ;
                                TBSS will be done for FA first, and then for other modalities.
    
                                (iv) separate nonFA TBSS:
                                if you wish to run TBSS for other modalities in future, files created during FA TBSS will be 
                                integrated into the nonFA TBSS. Provide --xfrmDir, --output from previous FA TBSS. 
                                In addition, provide any templates created during FA TBSS. On the other hand, specification of 
                                --input and --modality are same as above.


However, if you wish to run FA first and then other modalities in future, use option (iv) from above. There, you should 
provide the directory containing warp/affine obtained during registration of subject FA to the template/standard space. 
This way, we bypass doing the same non-linear registration once again. In addition, provide any templates created 
during FA TBSS.Here are a few sample commands for running separate nonFA TBSS:

    
**partial** `--engima` TBSS
    
    $libDir/tbss_all -i MD/origdata,RD/origdata \
    -c $CASELIST \                                      # same caselist that was used for FA TBSS
    --xfrmDir $testDir/enigmaTemplateOutput/transform \ # transform files are obtained from here
    --modality MD,RD --enigma \                         # --enigma tells to use enigma templates
    --avg                                               # -o is not required



**partial** `--studyTemplate` TBSS

    $libDir/tbss_all -i AD/origdata \
    -c $CASELIST \
    --xfrmDir $testDir/studyTemplateOutput/template \
    --modality AD \
    --template $testDir/studyTemplateOutput/template/template0.nii.gz \     # provide created templates 
    --templateMask $testDir/studyTemplateOutput/stats/mean_FA_mask.nii.gz \
    --skeleton $testDir/studyTemplateOutput/stats/mean_FA_skeleton.nii.gz \
    --skeletonMask $testDir/studyTemplateOutput/stats/mean_FA_skeleton_mask.nii.gz \
    --skeletonMaskDst $testDir/studyTemplateOutput/stats/mean_FA_skeleton_mask_dst.nii.gz \
    -s $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz \                        # provide space defining image if wanted
    -l $FSLDIR/data/atlases/JHU/JHU-ICBM-labels-1mm.nii.gz \                # provide atlas if wanted


# List creation

## 1. imagelist

You can easily generate list of your FA images as follows:

    cd projectDirectory
    ls `pwd`/000????/eddy/FA/*_FA.nii.gz > imagelist.txt

Here, we have a bunch of cases in the project directory whose IDs start with `000` and is followed by 
four alphanumeric characters. The directory structure to obtain FA images is `000????/eddy/FA/`. Inside the 
directory, we have an FA image ending with `_FA.nii.gz`.

**NOTE**: `pwd` is used to obtain absolute path


Similarly, you can generate a list of your dwis,masks as follows:
    
    cd projectDirectory
    touch dwi_mask_list.txt
    for i in GT_????
    do 
        echo `pwd`/$i/${i}_dwi_xc.nii.gz,`pwd`/$i/${i}_dwi_xc_mask.nii.gz >> dwi_mask_list.txt;
    done
    
In the above example, we have a bunch of cases with IDs GT_???? having separate folders.  
The dwis of the cases follow the pattern `ID_dwi_xc.nii.gz` and corresponding masks follow the pattern  
`ID_dwi_xc_mask.nii.gz`.

In the same way, you can define your file structure and file names to obtain an image/case list.


## 2. caselist

For just caselist, you can do:

    cd projectDirectory
    ls 000???? > caselist.txt 
    
Use of `????` is detailed above.
 

# Analysis

## 1. ROI analysis

`--enigma` and `--fmrib` branch of the pipeline performs ROI based analysis as default. The way it works is, each of the 
projected skeleton in subject space is superimposed upon a binary label map. The binary label map of each ROI is obtained from 
each segment in the specified `--labelMap` (atlas). The segments are labelled with an integer in the atlas. 
Two information from each ROI is obtained: Average{FA/MD/RD/AD} and number of voxels. Such info from all the ROI for each 
case is saved in a `caseid_roi.csv` file. Additionally, if you use `--avg` flag, RIGHT/LEFT regions in the ROIs are 
averaged. The averaged statistics are saved in `caseid_roi_avg.csv` file.

Again, ROI statistics of all the subjects are summarized in `{modality}_combined_roi.csv` and 
`{modality}_combined_roi_avg.csv` files in the `stats` folder.

Other optional arguments for ROI-based analysis are

### i. `--lut`

A look up table for names of each integer labels in the atlas

### ii. `--space`

If you create a study-specific template or provide a template that is not in the same space of the atlas, 
you must provide a T1/T2/FA image in the space of the atlas so the subject image can be warped to the same space.    
    
## 2. Voxelwise analysis

You may perform voxelwise statistics on 4D skeletonised FA image `all_FA_skeletonised.nii.gz` following [this](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/TBSS/UserGuide#voxelwise_statistics_on_the_skeletonised_FA_data) instruction.
All 4D data are saved in [stats](#iv-stats) folder.


# QC

Another merit of *TBSS* pipeline is automatic integration of quality checked/registration corrected data. 
Each diffusivity image is warped to template space. The pipeline lets the user visually check the quality of registration. 
Enable the `--qc` flag and the program will halt until you are done with QC-ing.

Warped images are in [warped](#c-warped) directory. Merged 4D data are in [stats](#iv-stats) directory, corresponding 
seqFile for index of volumes are also there. You may use fsleyes/fslview to scroll through the volumes. 

If re-running registration is required for any case, save the re-registered images in [warped](#c-warped) directory 
with the same name as before.

Press Enter, and the program will resume with your corrected data.

For re-registration of any subject, output the transform files to a temporary directory:
    
    mkdir /tmp/badRegistration/
    
    antsRegistrationSyNQuick.sh -d 3 \
    -f TEMPLATE \
    -m FA/preproc/caseid_FA.nii.gz \
    -o /tmp/badRegistration/caseid_FA
    
    antsApplyTransforms -d 3 \
    -i FA/preproc/caseid_FA.nii.gz \
    -o FA/warped/caseid_{FA/MD/AD/RD}_to_target.nii.gz \
    -r TEMPLATE \
    -t /tmp/badRegistration/caseid_FA1Warp.nii.gz /tmp/badRegistration/caseid_FA0GenericAffine.mat

Finally, if needed, you can copy the transform files in the [transform](#ii-transformtemplate) directory.

**NOTE** Replace all the above directories with absolute paths.

# Multi threading

Processing can be multi-threaded over the cases. Besides, `antsMultivariateTemplateConstruction2.sh` utilizes 
multiple threads to speed-up template construction. 

    --ncpu 8 # default is 4, use -1 for all available
   
However, multi-threading comes with a price of slowing down other processes that may be running in your system. So, it 
is advisable to leave out at least two cores for other processes to run smoothly.



# NRRD support

The pipeline is written for NIFTI image format. However, NRRD support is incorporated through [NIFTI --> NRRD](https://github.com/pnlbwh/dMRIharmonization/blob/parallel/lib/preprocess.py#L78) 
conversion on the fly.

See Billah, Tashrif; Bouix, Sylvain, Rathi, Yogesh; Various MRI Conversion Tools, 
https://github.com/pnlbwh/conversion, 2019, DOI: 10.5281/zenodo.2584003 for more details on the conversion method.

# Reference


S.M. Smith, M. Jenkinson, H. Johansen-Berg, D. Rueckert, T.E. Nichols, C.E. Mackay, K.E. Watkins, 
O. Ciccarelli, M.Z. Cader, P.M. Matthews, and T.E.J. Behrens. 
Tract-based spatial statistics: Voxelwise analysis of multi-subject diffusion data. NeuroImage, 31:1487-1505 


E. Garyfallidis, M. Brett, B. Amirbekian, A. Rokem, S. Van Der Walt, M. Descoteaux, 
I. Nimmo-Smith and DIPY contributors, "DIPY, a library for the analysis of diffusion MRI data", 
Frontiers in Neuroinformatics, vol. 8, p. 8, Frontiers, 2014.


Billah, Tashrif; Bouix, Sylvain, Rathi, Yogesh; Various MRI Conversion Tools, 
https://github.com/pnlbwh/conversion, 2019, DOI: 10.5281/zenodo.2584003.
