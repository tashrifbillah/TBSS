#!/usr/bin/env python

# ===============================================================================
# tbss (2019) pipeline is written by-
#
# TASHRIF BILLAH
# Brigham and Women's Hospital/Harvard Medical School
# tbillah@bwh.harvard.edu
#
# ===============================================================================
# See details at https://github.com/pnlbwh/tbss
# Submit issues at https://github.com/pnlbwh/tbss/issues
# View LICENSE at https://github.com/pnlbwh/tbss/blob/master/LICENSE
# ===============================================================================

import argparse
from tbssUtil import FILEDIR, pjoin, move, isfile, makeDirectory, check_call, chdir, getcwd, ConfigParser, Pool
from conversion import read_cases
from conversion.antsUtil import antsReg
from orderCases import orderCases
from glob import glob
from plumbum.cmd import antsApplyTransforms, fslmaths
from plumbum import FG
from skeletonize import skeletonize
from roi_analysis import roi_analysis

config = ConfigParser()
config.read(pjoin(FILEDIR,'config.ini'))
N_CPU= int(config['DEFAULT']['N_CPU'])


def process(args):

    cases= read_cases(args.caselist)

    # organize images into different directories ===========================================================

    # outDir
    #    |
    # -----------------------------------------------------------------------------
    #    |           |       |         |                |        |       |
    #    |           |       |         |                |        |       |
    # transform   template  stats     FA                MD       AD      RD
    #                                  |       (same inner file structure as that of FA)
    #                                  |
    #                     ----------------------------------------
    #                      |         |         |       |        |
    #                     preproc  origdata  warped  skeleton  roi
    #
    # copy all FA into FA directory
    # put all preprocessed data into preproc directory
    # keep all warp/affine in transform directory
    # output all warped images in warped directory
    # output all skeletons in skel directory
    # output ROI based analysis files in roi directory

    # define directories
    modDir = pjoin(args.outDir, f'{args.modality}')
    xfrmDir = pjoin(args.outDir, 'transform')
    statsDir = pjoin(args.outDir, 'stats')
    templateDir = pjoin(args.outDir, 'template/')
    preprocDir= pjoin(modDir, 'preproc')
    warpDir= pjoin(modDir, 'warped')
    skelDir= pjoin(modDir, 'skeleton')
    roiDir= pjoin(modDir, 'roi')

    # force creation of inner directories
    makeDirectory(warpDir, True)
    makeDirectory(skelDir, True)
    makeDirectory(roiDir, True)


    # modality can be one of the diffusionMeasures= ['FA','MD','AD','RD']
    # we could use just listdir(), but the following would be more strict and safe
    modImgs = glob(pjoin(modDir, '*.nii.gz'))
    modImgs = orderCases(modImgs, cases)


    for c, imgPath in zip(cases, modImgs):
        if imgPath is not f'{c}.nii.gz':
            move(imgPath, pjoin(modDir, f'{c}.nii.gz'))

    modImgs = glob(pjoin(modDir, '*.nii.gz'))
    modImgs = orderCases(modImgs, cases)


    # preprocessing ========================================================================================
    if args.modality=='FA':
        print('Preprocessing FA images: eroding them and zeroing the end slices ...')
        modDir= pjoin(args.outDir, args.modality)
        CURRDIR= getcwd()
        chdir(modDir)
        check_call('tbss_1_preproc *.nii.gz', shell= True) # creates 'FA' and 'origdata' folders
        chdir(CURRDIR)
        print('Index file location has changed, see ', pjoin(preprocDir, 'slicesdir', 'index.html'))

        # rename args.modality/FA to args.modality/preproc
        move(pjoin(modDir, 'FA'), preprocDir)
    else:
        print(f'Preprocessing {args.modality} images using FA mask (eroding them and zeroing the end slices) ...')
        modDir = pjoin(args.outDir, args.modality)

        # force creation of inner directories
        makeDirectory(pjoin(modDir, 'origdata'), True)
        makeDirectory(pjoin(modDir, 'preproc'), True)


        pool= Pool(args.ncpu)
        for c, imgPath in zip(cases, modImgs):
            print('Processing ', c)
            FAmask= pjoin(args.outDir, 'FA', 'preproc', f'{c}_FA_mask.nii.gz')
            preprocMod= pjoin(preprocDir, f'{c}_{args.modality}.nii.gz')

            pool.apply_async(fslmaths, (imgPath, '-mas', FAmask, preprocMod))


        pool.close()
        pool.join()

        check_call((' ').join(['mv', pjoin(modDir, '*.nii.gz'), pjoin(modDir, 'origdata')]), shell= True)

    modImgs = glob(pjoin(preprocDir, f'*{args.modality}.nii.gz'))


    # create template ======================================================================================
    if not args.template and args.modality=='FA':
        print('Creating study specific template ...')
        # we could pass modImgs directly to antsMult(), instead saving them to a .txt file for logging
        # modImgs = glob(pjoin(args.outDir, f'{args.modality}', f'*{args.modality}*.nii.gz'))

        makeDirectory(templateDir, args.force)

        antsMultCaselist = pjoin(args.outDir, 'antsMultCaselist.txt')
        check_call((' ').join(['ls', pjoin(preprocDir, f'*{args.modality}.nii.gz'), '>', antsMultCaselist]),
                   shell= True)

        # ATTN: antsMultivariateTemplateConstruction2.sh requires '/' at the end of templateDir
        # antsMult(antsMultCaselist, templateDir)
        # TODO: rename the template
        args.template= pjoin(templateDir, 'template0.nii.gz')

        # warp and affine to template0.nii.gz have been created for each case during template construction
        # so template directory should be the transform directory
        xfrmDir= templateDir

    # register each image to the template ==================================================================
    elif args.template:
        # find warp and affine of FA image to args.template for each case
        if args.modality=='FA':
            pass
            # makeDirectory(xfrmDir, True)
            # pool= Pool(N_CPU)
            # for c, imgPath in zip(cases, modImgs):
            #     pool.apply_async(antsReg, (args.template, None, imgPath, pjoin(xfrmDir, f'{c}_FA')))
            #
            # pool.close()
            # pool.join()

    else:
        # for ANTs template and nonFA, template directory should be the transform directory
        xfrmDir = templateDir
        args.template = pjoin(templateDir, 'template0.nii.gz')

    # register template to a standard space ================================================================
    # useful when you would like to do ROI based analysis using an atlas
    # project the created/specified template to the space of atlas
    if args.space:
        outPrefix = pjoin(args.outDir, 'tmp2space')
        warp2space = outPrefix + '1Warp.nii.gz'
        trans2space = outPrefix + '0GenericAffine.mat'
        if not isfile(warp2space):
            antsReg(args.space, None, args.template, outPrefix)

        # TODO: rename the template
        args.template = outPrefix + 'Warped.nii.gz'


    pool= Pool(args.ncpu)
    for c, imgPath in zip(cases, modImgs):
        # generalize warp and affine
        warp2tmp= glob(pjoin(xfrmDir, f'{c}_FA*[!Inverse]Warp.nii.gz'))[0]
        trans2tmp= glob(pjoin(xfrmDir, f'{c}_FA*GenericAffine.mat'))[0]
        output= pjoin(warpDir, f'{c}_{args.modality}_to_target.nii.gz')

        if not args.space:
            pool.apply_async(antsApplyTransforms, ('-d', '3',
                                                   '-i', imgPath,
                                                   '-o', output,
                                                   '-r', args.template,
                                                   '-t', warp2tmp, trans2tmp))

        else:
            pool.apply_async(antsApplyTransforms, ('-d', '3',
                                                   '-i', imgPath,
                                                   '-o', output,
                                                   '-r', args.template,
                                                   '-t', warp2space, trans2space, warp2tmp, trans2tmp))


    pool.close()
    pool.join()


    # create skeleton for each subject
    modImgsInTarget= glob(pjoin(warpDir, f'*_{args.modality}_to_target.nii.gz'))
    modImgsInTarget= orderCases(modImgsInTarget, cases)

    # obtain modified args from skeletonize() which will be used for other modalities than FA
    args= skeletonize(modImgsInTarget, cases, args, statsDir, skelDir, xfrmDir)

    skelImgsInSub= glob(pjoin(skelDir, f'*_{args.modality}_to_target_skel.nii.gz'))
    skelImgsInSub= orderCases(skelImgsInSub, cases)

    # roi based analysis
    if args.labelMap:
        roi_analysis(skelImgsInSub, cases, args, modDir, roiDir)

    return args

if __name__=='__main__':
    pass
