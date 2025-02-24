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

import sys, argparse
from nilearn import image, plotting
from tbssUtil import abspath, dirname, pjoin, makeDirectory
from glob import glob
from orderCases import orderCases
from conversion import read_cases
from multiprocessing import Pool

def write_html(ssDir, cases):

    STDOUT= sys.stdout
    summaryFile= pjoin(ssDir, 'summary.html')
    print('Writing html file, view output at ', summaryFile)
    f= open(summaryFile, 'w')

    # summary html is inspired by MATLAB_QC/QC_FA_SKEL/enigmaDTI_FA_Skel_QC.html

    sys.stdout= f

    # beginning of html
    print('''<html>
<head>
<style type="text/css">
*
{
margin: 0px;
padding: 0px;
}
html,body
{
height: 100%;
}
</style>
</head>
<body>
<pre> This HTML file was generated by  <b>https://github.com/pnlbwh/tbss</b>  pipeline

</pre>''')



    for c in cases:
        # repeat for each case
        print(f'''<table cellspacing="1" style="width:100%;background-color:"white";">
<tr>
<td> <FONT COLOR=BLUE FACE="Geneva, Arial" SIZE=4> {c} </FONT> </td>
</tr>
<tr>
<td><a href="file:{c}.png"><img src="{c}.png"width="100%" ></a></td>
<br>
</tr>
</table>''')


    # ending of html
    print('''</body>
</html>''')

    f.close()

    sys.stdout= STDOUT

def generate_ss(modDir, ssDir, cases, ncpu):

    # reorder both skeleton/* and warped/* according to caseId
    warpedImgs= glob(pjoin(modDir, 'warped', '*_to_target.nii.gz'))
    skelImgs= glob(pjoin(modDir, 'skeleton', '*_to_target_skel.nii.gz'))
    warpedImgs= orderCases(warpedImgs, cases)
    skelImgs= orderCases(skelImgs, cases)

    makeDirectory(ssDir)

    pool= Pool(ncpu)
    for fg,bg,c in zip(image.iter_img(skelImgs), image.iter_img(warpedImgs), cases):
        print('Taking screen shot of ', c)
        output_file = pjoin(ssDir, f'{c}.png')
        pool.apply_async(func= plotting.plot_stat_map, args= (fg, ),
                         kwds= {'bg_img':bg, 'dim':False, 'annotate':False, 'draw_cross':False, 'output_file':output_file, })

    pool.close()
    pool.join()


def main():

    parser = argparse.ArgumentParser(description='Generates an HTML file with skeleton overlaid upon the diffusivity measure '
                                                 'i.e. FA,MD,AD,RD etc', formatter_class= argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-d','--dir', type=str, default=argparse.SUPPRESS,
                        help='TBSS output directory where results are stored in --modality sudirectory; '
                             'you should have write permission into the directories')

    parser.add_argument('-m','--modality', type=str, default='FA', help='Modality={FA,MD,AD,RD,...} of images')
    parser.add_argument('-c','--caselist', type=str, default=argparse.SUPPRESS,
                        help='caseIds from the caselist are used to label screenshots, default: outDir/log/caselist.txt')

    parser.add_argument('-n','--ncpu', type= int, default=4, help='number of threads to use, if other processes in your computer '
                        'becomes sluggish/you run into memory error, reduce --nproc')


    args = parser.parse_args()

    args.outDir= abspath(args.dir)
    modDir= pjoin(args.outDir, args.modality)
    ssDir= pjoin(modDir, 'slicesdir')


    if args.caselist:
        args.caselist= abspath(args.caselist)
    else:
        # use default
        args.caselist= pjoin(args.outDir, 'log', 'caselist.txt')


    cases= read_cases(args.caselist)

    # generate screenshots
    generate_ss(modDir, ssDir, cases, args.ncpu)

    # write summary HTML file
    write_html(ssDir, cases)


if __name__== '__main__':
    main()
