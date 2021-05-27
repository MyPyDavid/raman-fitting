#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# flake8: noqa

# WARNING this module is under construction and not used
# TODO update and move this module to a post process package

class RamanPostProcessing:
    def __init__(self,SampleGrp = 'DW'):
        pass
#        pd.read_excel(glob.glob(FileHelper.FindExpFolder('RAMAN').DestDir+'\\%s\\%s_mean_OVV*' %(SampleGrp,SampleGrp))[0])
#        FitRAMAN().DBpath# FitRAMAN.DB_read()AllResult.reset_index().to_hdf(DBpath,key = 'RAMAN/%s/FitPars_OVV' %sGrp, mode = 'a',format = 'table')
#        self.
#        self.s2,self.s3,self.cb = self.DWseries()
#    def DWseries(self):
#        pd.concat([s2,s3,cb]).to_excel(self.destdir+'\\DW_RAMAN_CBseries.xlsx')
#        return s2,s3,cb
    def Make_DB_files(self):
        SampleGrp = 'DW'
        ovv = pd.read_hdf(FitRAMAN().DBpath,'RAMAN/%s/FitPars_OVV' %SampleGrp)
        ovv.drop(['SampleID'],axis=1,inplace=True)
        ovv['SampleID'] = ovv['index'].str.strip('_mean').iloc[0::].values
        
        destdir = FileHelper.FindExpFolder('RAMAN').DestDir / Path('%s'%SampleGrp)

        OutList = ['ID/IG','ID3/IG','G_center','D_center','D4_center','D3_center']
        ParRd = pd.read_excel(list(destdir.rglob('DW*AllPars*'))[0])
        ParRd.loc[:,OutList].to_excel(destdir.joinpath('DW_ParsOrigin.xlsx'))
#        s2 = ovv.iloc[2:8] s3 = ovv.iloc[8:14]  cb = ovv.iloc[18:24]
        sA = pd.read_excel(FileHelper.FindExpFolder('RAMAN').AllDataOVV,'SerieA',skiprows=[1,2,3,4])
        sB = pd.read_excel(FileHelper.FindExpFolder('RAMAN').AllDataOVV,'SerieB',skiprows=[1,2,3,4])
#        header=[0,1,2,3,4]
        sA = pd.merge(s2,sA,on='SampleID')
        sB = pd.merge(s3,sB,on='SampleID')
        cb.to_excel(FileHelper.FindExpFolder('RAMAN').AllDataOVV.parent.joinpath('sCB_AllData.xlsx'))
        sA.to_excel(FileHelper.FindExpFolder('RAMAN').AllDataOVV.parent.joinpath('sA_AllData.xlsx'))
        sB.to_excel(FileHelper.FindExpFolder('RAMAN').AllDataOVV.parent.joinpath('sB_AllData.xlsx'))
#        sA.to_excel(os.path.dirname(FileHelper.FindExpFolder('RAMAN').AllDataOVV)+'\\sA_AllData.xlsx')
#        sB.to_excel(os.path.dirname(FileHelper.FindExpFolder('RAMAN').AllDataOVV)+'\\sB_AllData.xlsx')
        
    
    def PostPlot(self,RamanResultFolder = '',SampleGrp = 'DW'):
#        SampleGrp = 'DW'
#        PPdestdir = FileHelper.FindExpFolder('RAMAN').DestDir / Path('%s'%SampleGrp) / 'PostProcess'
#        PPdestdir.mkdir(parents=True,exist_ok=True)
        PrepOVV = pd.read_excel(FileHelper.FindExpFolder('t').PrepOVV)
#        ovv = pd.read_hdf(FitRAMAN().DBpath,'RAMAN/%s/FitPars_OVV' %SampleGrp)
#        ovvFile = list((FileHelper.FindExpFolder('RAMAN').DestDir /'4pVoigtGammaFixed' / SampleGrp).rglob('*AllPars*xlsx' ))[0]
        ovvFile = list((FileHelper.FindExpFolder('RAMAN').DestDir / RamanResultFolder / SampleGrp).rglob('*AllPars*xlsx' ))[0]
        PPdestdir =ovvFile.parent / 'PostProcess'
        PPdestdir.mkdir(parents=True,exist_ok=True)
        print('Raman Results used: %s' %ovvFile)
        ovv = pd.read_excel(ovvFile)
#        ovv = ovv.assign(**{'La' : 4.4*(ovv.I_D/ovv.I_G)**-1, 'Leq' : 8.8*(ovv.I_2D/ovv.I_G)})
        ovv.drop(['SampleID'],axis=1,inplace=True)
        ovv['SampleID'] = ovv.index.str.strip('_mean').values
#        s2 = ovv.iloc[2:8] s3 = ovv.iloc[8:14] cb = ovv.iloc[18:24]
        ovv = pd.merge(ovv,PrepOVV.loc[:,['SampleID','Precursor type' ]],how='inner',on='SampleID')
        s2str,s3str,cbstr = ('DW16|DW17|DW18|DW19|DW20|DW21'),('DW24|DW25|DW26|DW27|DW28|DW29'),('DW38A|DW38B|DW38C|DW38D|DW38E|DW38F')
        s2 = ovv.loc[ovv.SampleID.str.contains(s2str),:]
        s3 = ovv.loc[ovv.SampleID.str.contains(s3str),:]
        cb = ovv.loc[ovv.SampleID.str.contains(cbstr),:]
        s2.to_excel(ovvFile.parent / 'OVV_s2.xlsx')
        s3.to_excel(ovvFile.parent / 'OVV_s3.xlsx')
        cb.to_excel(ovvFile.parent / 'OVV_cb.xlsx')
        s2s3 = pd.concat([s2,s3])
        s2s3.loc['Cat_mean'] = s2s3.mean()
        s2s3.loc['CB_mean'] = cb.mean()
        MeanCatCB = s2s3.loc[['Cat_mean','CB_mean']]
        MeanCatCB.loc['Diff_%'] = 100*(s2s3.loc['Cat_mean'] - s2s3.loc['CB_mean'])/s2s3.loc['Cat_mean']
        MeanCatCB.to_excel(PPdestdir.joinpath('MeanCatCB_cor.xlsx'))
        MeanCatCB.loc[:,[i for i in MeanCatCB.columns if 'center' in i]].to_excel(PPdestdir.joinpath('MeanCatCB_CENTER.xlsx'))
        
        s2cb, s3cb = list(zip(s2str.split('|'),cbstr.split('|'))), list(zip(s3str.split('|'),cbstr.split('|')))
        CorrRes = pd.DataFrame(columns=['SampleLinRes'])
        for col in ovv.columns:
#            print(col,cb[col],s2[col],'s2_%s'%col)
            fig,ax = plt.subplots(1,1,figsize=(12,12))
            try:
                ax.scatter(cb[col],s2[col],marker='s',s=120,label='s2_%s'%col)
                ax.scatter(cb[col],s3[col],marker='o',s=120,label='s3_%s'%col)
                ax.plot(cb[col],cb[col],ls='--',lw=2,c='k',label='CB only')
                ax.plot(cb[col],cb[col],marker='.',c='k',label='CB only')
#                ax.annotate(s2.iloc[0].split('_mean')[0], xy=[0.995*x_coord,1.005*y_coord], textcoords='data',fontsize=12)
                ax.legend(), ax.set_xlabel('CB_%s'%col),ax.set_ylabel('CAT_%s'%col)
                
                plt.savefig(PPdestdir.joinpath('%s_CBprec_cor.png'%''.join(col.split('/'))),dpi=100,bbox_inches='tight')
#                plt.close()
            except Exception as e:
#                plt.close()
                print('CB Plot error skipped: %s \n %s'%(col,e))
                continue
            try:
                Corr_s2cb = linregress(cb[col],s2[col])
                Corr_s3cb = linregress(cb[col],s3[col])
                CorrColRes = pd.DataFrame([('s2_%s'%num,i) for num,i in enumerate(Corr_s2cb)] +[('s3_%s'%num,i) for num,i in enumerate(Corr_s3cb)],columns=['SampleLinRes',col])
                CorrRes = pd.merge(CorrColRes,CorrRes,on='SampleLinRes',how='outer')
            except:
                print('No Linregress in PostPlot')
            plt.show()
            
    #                ax.plot(FitData['RamanShift'],FitData['I_model4Voigt'],label='Fit_model4Voigt',lw=3,c='r')
            
            try:            
                fig,ax = plt.subplots(1,1,figsize=(12,12))
                ax.scatter(s2['Precursor type'],s2[col],marker='s',s=120,label='s2_%s'%col)
                ax.scatter(s3['Precursor type'],s3[col],marker='o',s=120,label='s3_%s'%col)
                ax.scatter(cb['Precursor type'],cb[col],marker='D',s=120,label='cb_%s'%col,c='k',alpha=0.5)
                ax.legend(), ax.set_xlabel('SampleID'),ax.set_ylabel('%s'%col)
#                for i,a in pd.concat([s2,s3,cb]).iterrows():
    #            x_coord,y_coord = a['D_fwhm'], a['G_fwhm']
#                    x_coord,y_coord = a[xlbl],a[ylbl]
#                    ax.scatter(x_coord,y_coord,marker='s',s=120)
#                    ax.annotate(a.iloc[0].split('_mean')[0], xy=[0.995*x_coord,1.005*y_coord], textcoords='data',fontsize=12)
                plt.savefig(PPdestdir.joinpath('%s_SampleID_cor.png'%''.join(col.split('/'))),dpi=100,bbox_inches='tight')
                plt.close
            except Exception as e:
                plt.close()
                print('SampleID Plot error skipped: %s \n %s'%(col,e))
                continue
        CorrRes.to_excel((PPdestdir.joinpath('CorrResult.xlsx')))
            #%%
        for t in [('D_fwhm','G_fwhm'),('G_fwhm','D1D1fwhm'),('ID/IG','ID3/IG'),('D_center','G_center'),('D2_center','G_center'),('D2_sigma','G_sigma')]:
            fig, ax = plt.subplots(1,1,figsize=(12,12))
            ax.set_xlabel(xlbl),ax.set_ylabel(ylbl)
            xlbl,ylbl = t[0],t[1]
            s2_fltr = s2[[xlbl,ylbl]][np.abs(s2[[xlbl,ylbl]]-s2[[xlbl,ylbl]].mean()) <= (2*s2[[xlbl,ylbl]].std())]
            s3_fltr = s3[[xlbl,ylbl]][np.abs(s3[[xlbl,ylbl]]-s3[[xlbl,ylbl]].mean()) <= (2*s3[[xlbl,ylbl]].std())]
            cb_fltr = cb[[xlbl,ylbl]][np.abs(cb[[xlbl,ylbl]]-cb[[xlbl,ylbl]].mean()) <= (2*cb[[xlbl,ylbl]].std())]
            
            ax.scatter(s2_fltr[xlbl],s2_fltr[ylbl],marker='s')
            ax.scatter(s3_fltr[xlbl],s3_fltr[ylbl],marker='o')
            ax.scatter(cb_fltr[xlbl],cb_fltr[ylbl],marker='^',c='lightgrey',alpha=0.8)
            
            
#            pd.concat([s2,s3,cb])
            for i,a in ovv.iloc[pd.concat([s2_fltr,s3_fltr,cb_fltr]).index].iterrows():
    #            x_coord,y_coord = a['D_fwhm'], a['G_fwhm']
#                print(i,a)
                x_coord,y_coord = a[xlbl],a[ylbl]
#                ax.scatter(x_coord,y_coord,marker='s',s=120)
                ax.annotate(a.SampleID, xy=[0.995*x_coord,1.005*y_coord], textcoords='data',fontsize=12)
            plt.savefig(PPdestdir.joinpath(str('Compare_%s_%s.png'%(t[0],t[1])).replace('/','_')),dpi=100,bbox_inches='tight')
            plt.show()
            plt.close()
        return print('PostProcessed XD' )
    

def run_selection():
    run = input('Want to start the fitting run?')
    sys.path.append(Path(__file__).parent.parent)
    try:
        FindExpText = str(inspect.getsource(FileHelper.FindExpFolder)).encode('utf-8')
#    pytext =
        pytext = FileHelper.FileOperations.mylocal_read_text(Path(__file__)) + str(FindExpText)
    except Exception as e:
        pytext = 'test'
        
    FileHash = hashlib.md5(str(pytext).encode('utf-8')).hexdigest()
    force_reindex = 0
    print('Hash:', FileHash)
    if 'y' in run or run == 'yes':
        PostProcess = False
        orgRFs = OrganizeRAMANFiles().ovv()
      
        recent_groups =[i for i in run.split() if i in orgRFs.SampleGroup.unique()]  

        print(f'Running groups: {recent_groups}')
        org_recent = orgRFs.loc[orgRFs.SampleGroup.str.contains(('|'.join)(recent_groups))]
        if run == 'yall':
            org_recent = orgRFs
        FitRAMAN().plot_RAMAN(org_recent)

        if PostProcess == True:
            RamanPostProcessing('DW').PostPlot()
    elif 'index'in run:
        orgRFs = OrganizeRAMANFiles().ovv()
        print(orgRFs.SampleGroup.unique())  
    
 
#            ovv.plot(x=,y='',kind='scatter')
def XCorrDW(sA):
    #%%
    lst = []
    for colA in sA.columns:
        for colX in sA.columns:
            try:
                slope, intercept, r_value, p_value, std_err = linregress(sA[colA],sA[colX])
                if r_value > 0.95 and r_value < 1 and colA != colX:
                    lst.append([colX,colA,rvalue,p_value,std_err])        
                    print(colA,colX,rvalue)
                    sA.plot(colA,colX,kind=scatter)
#                    plt.show()
#                    plt.close()
                
            except Exception as e:
                continue
        #%%
   
def PostReadResults(self,groups, result_type = 'AllPars',compare_sample = 'VGC12_mean'):
    DestDir = self.DestDir
    outpath = DestDir.joinpath('Comparison_{0}_{1}.xlsx'.format(result_type,'_'.join(groups)))
    cols = SampleSelection.RAMAN_cols_corr[0:5]+['AD/AG','AD3/AG']
    l = []
    for gr in groups:
        result_f = list(DestDir.rglob('{0}/*{1}_{0}*'.format(gr,result_type)))[0]
        result_file  = pd.read_excel(result_f,index_col=[0])
        l.append(result_file)
    res_merged = pd.concat([i for i in l])
    for c in cols:
        res_merged[c] = res_merged[c].astype(float)
    VG = res_merged.loc[compare_sample]
    diff_out = []
    for n,i in res_merged.iterrows():
        diff = pd.concat([i for i in [VG,i]],axis=1).T[cols].diff()
        diff['sum'] = diff.sum(axis=1)
        diff['abs_sum'] = diff.abs().sum(axis=1)
        diff_out.append(diff.iloc[-1])
        
    res_diff = pd.concat([i for i in diff_out],axis=1).T
    res_diff.sort_values(by='abs_sum')
    
    res_diff.sort_values(by='sum').to_excel(outpath)



#        print(self.s2)
#        for col in self.s2.columns:
#            print(col)
#            fig,ax = plt.subplots(1,1,figsize=(12,12))
#            ax.scatter(self.cb[col],self.s2[col],marker='s',s=80,label='s2_%s'%col)
#            try:
#                linregress(self.cb[col],self.s2[col])
#                linregress(self.cb[col],self.s3[col])
#            except:
#                print('No Linregress in PostPlot')
#            ax.scatter(self.cb[col],self.s3[col],marker='o',s=80,label='s3_%s'%col)
#            ax.plot(self.cb[col],self.cb[col],ls='--',lw=2,c='k',label='CB only')
#    #                ax.plot(FitData['RamanShift'],FitData['I_model4Voigt'],label='Fit_model4Voigt',lw=3,c='r')
#            ax.legend(), ax.set_xlabel('CB_%s'%col),ax.set_ylabel('CAT_%s'%col)
#            plt.savefig(self.destdir+'\\%s_CBprec_cor.png'%''.join(col.split('/')),dpi=300,bbox_inches='tight')
#            plt.close()
#            
#            fig,ax = plt.subplots(1,1,figsize=(12,12))
#            ax.scatter(self.s2['SampleID'],self.s2[col],marker='s',s=80,label='s2_%s'%col)
#            ax.scatter(self.s3['SampleID'],self.s3[col],marker='o',s=80,label='s3_%s'%col)
#            ax.legend(), ax.set_xlabel('SampleID'),ax.set_ylabel('%s'%col)
#            plt.savefig(self.destdir+'\\%s_SampleID_cor.png'%''.join(col.split('/')),dpi=300,bbox_inches='tight')
#            plt.close
            
def Old_Post(self): 
    ovv = ovv.assign(**{'SampleIDc' :[i[0] for i in ovv.SampleID.str.split('_')],'Pos#' : [i[-1].split('.txt')[0].split('pos')[-1] for i in ovv.SampleID.str.split('_')]})
    ovv.columns
    for NAME in ['DW','PT','SS']:
        ovvstd = ovv.loc[ovv.SampleID.str.contains(NAME),:].query('(Std_fit1_2 > 0) & (Std_fit2_2 > 0) & (Std_fit2_2 < 250)').groupby(by='SampleIDc').describe()
        ovvstd = ovvstd.fillna(0)
        ovvstd.to_csv(RAMAN_dir+'\\RAMAN_%s-series.csv' %NAME)
        ovvstd.to_excel(RAMAN_dir+'\\RAMAN_%s-series.xlsx' %NAME)
    
        ovvstd['Ratio_DG'].plot(kind='bar',y='mean',yerr='std',ylim=(0,1),x=ovvstd.index,title='Ratio D/G',label='')
        plt.savefig(RAMAN_dir+'\\RAMAN_%s-DG-ratio.png' %NAME,dpi=300,bbox_inches='tight')
        ovvstd['Peak_center_1'].plot(kind='bar',y='mean' ,yerr='std',x=ovvstd.index,title='Peak D Raman shift (cm$^{-1}$)',label='',ylim=(1340,1370),logy=False) 
        plt.savefig(RAMAN_dir+'\\RAMAN_%s-D-band_peak.png'%NAME,dpi=300,bbox_inches='tight' )
        ovvstd['Peak_center_2'].plot(kind='bar',y='mean',yerr='std',x=ovvstd.index,title='Peak G Raman shift (cm$^{-1}$)',label='',ylim=(1575,1590),logy=False)
        plt.savefig(RAMAN_dir+'\\RAMAN_%s-G-band_peak.png' %NAME,dpi=300,bbox_inches='tight' )
        ovvstd['Area_1'].plot(kind='bar',y='mean',yerr='std',x=ovvstd.index,title='Area peak 1',label='',logy=False)
        plt.savefig(RAMAN_dir+'\\RAMAN_%s-Area1.png' %NAME,dpi=300,bbox_inches='tight' )
        ovvstd['Area_2'].plot(kind='bar',y='mean',yerr='std',x=ovvstd.index,title='Area peak 2',label='',logy=False)
        plt.savefig(RAMAN_dir+'\\RAMAN_%s-Area2.png' %NAME,dpi=300,bbox_inches='tight' )
    #plt.savefig(RAMAN_dir+'\\RAMAN_PT-series_.png')
    #ovvstd['Peak_center_2'].plot(kind='bar',y='mean',yerr='std',x=ovvstd.index,title='Peak G wavenumber',label='',ylim=(1575,1590),logy=False)