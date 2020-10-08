#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 14:49:50 2020

@author: zmg
"""
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import matplotlib.lines as mlines
import matplotlib
matplotlib.rcParams.update({'font.size': 14})

#%%

# TODO FIX PLOTTING PER PEAK MODEL
def plotting_info(windowname):
    axes = {'full' : (0,0), 'low' : (0,1), '1st_order' : (0,2),'mid' : (1,1), '2nd_order' : (1,2),
        'normalization' : (1,0)}
    return axes.get(windowname)

def raw_data_export(fitting_specs):
    current_sample = fitting_specs[0].windowname, fitting_specs[0].sIDmean_col
    try:
        raw_data_spectra_plot(fitting_specs)    
    except Exception as e:
        print('no extra Raw Data plots for {1} \n {0}'.format(e,current_sample))    
    try:
        raw_data_spectra_export(fitting_specs)
    except Exception as e:
        print('no extra Raw Data plots for {1} \n {0}'.format(e,current_sample))
        
    

def raw_data_spectra_plot(fitting_specs):
#    fitting_specs
    try:
        fig,ax = plt.subplots(2,3,figsize=(18,12))
        ax_wn = []
        
        for spec in fitting_specs:
            try:
                ax_wn = ax[plotting_info(spec.windowname)]    
#                spec.windowname
                _legend = True if 'full' == spec.windowname else False
                spec.mean_spec.plot(y = spec.sID_rawcols ,ax= ax_wn, alpha = 0.5, legend = _legend)
                spec.mean_spec.plot(y = spec.sIDmean_col ,ax= ax_wn, c= 'k', alpha = 0.7, lw=3, legend = _legend)
    
                ax_wn.set_title(spec.windowname)
#                _legend = True if 'full' in spec.windowname else False
                if _legend:
                    ax_wn.legend(fontsize=10)
                    
            except:
                pass
        
        plt.suptitle(spec.sIDmean_col,fontsize=16)
        plt.savefig(spec.mean_info.DestRaw.unique()[0].joinpath(f'{spec.sIDmean_col}.png'),dpi=300,bbox_inches='tight')
        plt.close()
    except Exception as e:
        print('no extra Raw Data plots: {0}'.format(e))    
    
def raw_data_spectra_export(fitting_specs):
#    fitting_specs
    try:
        for spec in fitting_specs:
#            spec.windowname, spec.sIDmean_col
            wnxl_outpath_info = spec.mean_info.DestRaw.unique()[0].joinpath(f'info_{spec.sIDmean_col}_{spec.windowname}.xlsx')
            wnxl_outpath_spectra = spec.mean_info.DestRaw.unique()[0].joinpath(f'spectra_{spec.sIDmean_col}_{spec.windowname}.xlsx')
            spec.mean_info.to_excel(wnxl_outpath_info)
            spec.mean_spec.to_excel(wnxl_outpath_spectra)
#            ax_wn = ax[plotting_info(spec.windowname)]
    except Exception as e:
        print('no extra Raw Data plots: {0}'.format(e))    
    
#
def fit_spectrum_plot(peak1,res1_peak_spec,res2_peak_spec, plot_Annotation = True, plot_Residuals = True):
    
    #%%
    sID = res1_peak_spec.extrainfo.SampleID.unique()[0]
    SampleBgmean_col = f'int_{sID}_mean'
         
#    sID, DestPlotDir, SampleBgmean_col, FitData, FitModPeaks, FitData_2nd,comps, comps_2nd,out, out_2nd, 
    FitData_1st = res1_peak_spec.FitComponents
    Model_peak_col_1st = res1_peak_spec.peak_model
    Model_data_col_1st = f'Model_{Model_peak_col_1st}' 
    compscols_1st = [i for i in FitData_1st.columns if i.endswith('_')]
#    FitReport_1st = res1_peak_spec.FitReport
    
    FitData_2nd = res2_peak_spec.FitComponents
    Model_peak_col_2nd = res2_peak_spec.peak_model
    Model_data_col_2nd = f'Model_{Model_peak_col_2nd}' 
    compscols_2nd = [i for i in FitData_2nd.columns if i.endswith('_')]
    
    FitPars, FitPars_2nd = res1_peak_spec.FitParameters, res2_peak_spec.FitParameters
    
    fig = plt.figure(figsize=(28,24))
    gs = gridspec.GridSpec(4, 1,height_ratios=[4,1,4,1])
    ax = plt.subplot(gs[0])
    axRes = plt.subplot(gs[1])
#                axAnn = plt.subplot(gs[1])
    ax2nd = plt.subplot(gs[2])
    ax2ndRes = plt.subplot(gs[3])
    ax2ndRes.grid(True),axRes.grid(True,'both')
    ax2nd.grid(True),ax.grid(True,'both')
    ax.get_yaxis().set_tick_params(direction='in')
    ax.get_xaxis().set_tick_params(direction='in')
    ax.set_title(SampleBgmean_col)
#                             '%s' %FileName)
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.tick_params(which='both',direction='in')
    ax2nd.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax2nd.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax2nd.tick_params(which='both',direction='in')
    ax.set_facecolor('oldlace'),ax2nd.set_facecolor('oldlace')
    axRes.set_facecolor('oldlace'),ax2ndRes.set_facecolor('oldlace')
#                for FitN in [PosInts_Bg,PosInts_Bg_2nd]:         
#                    fig,ax = plt.subplots(1,1,figsize=(12,12))
#                if FitN.RamanShift.max() > 2300:
    ax2nd.plot(FitData_2nd['RamanShift'],FitData_2nd[Model_data_col_2nd],label=Model_data_col_2nd,lw=3,c='r')
    ax2nd.plot(FitData_2nd['RamanShift'],FitData_2nd[res2_peak_spec.raw_data_col],label='Data',lw=3,c='grey',alpha=0.5)
    ax2ndRes.plot(FitData_2nd['RamanShift'],FitData_2nd[res2_peak_spec.raw_data_col]-FitData_2nd[Model_data_col_2nd],label='Residual',lw=3,c='k',alpha=0.8)
    
    for fit_comp_col_2nd in compscols_2nd: # automatic color cycle 'cyan' ...
        ax2nd.plot(FitData_2nd['RamanShift'], FitData_2nd[fit_comp_col_2nd],ls='--',lw=4,label=fit_comp_col_2nd)
        center_col, height_col = fit_comp_col_2nd+'center', fit_comp_col_2nd+'height'
        ax2nd.annotate(f'{fit_comp_col_2nd}\n {FitPars_2nd[center_col].round(0).iloc[0]:.0f}',xy=(FitPars_2nd[center_col].iloc[0]*0.97,0.8*FitPars_2nd[height_col].iloc[0]),xycoords='data')
#    ax2nd.plot(FitData_2nd['RamanShift'], comps_2nd['D1D1_'], color='lime',ls='--',lw=4,label='2*D')
#    ax2nd.plot(FitData_2nd['RamanShift'], comps_2nd['D4D4_'], color='purple',ls='--',lw=4,label='2*D4')
#    ax2nd.plot(FitData_2nd['RamanShift'], comps_2nd['GD1_'], color='pink',ls='--',lw=4,label='G+D1')
    ax2nd.set_ylim(-0.02,FitData_2nd[Model_data_col_2nd].max()*1.5)
#                else:
    ax.plot(FitData_1st['RamanShift'],FitData_1st[Model_data_col_1st],label=Model_data_col_1st,lw=3,c='r')
    ax.plot(FitData_1st['RamanShift'],FitData_1st[res1_peak_spec.raw_data_col],label='Data',lw=3,c='grey',alpha=0.8)
    axRes.plot(FitData_1st['RamanShift'],FitData_1st[res1_peak_spec.raw_data_col]-FitData_1st[Model_data_col_1st],label='Residual',lw=3,c='k',alpha=0.8)
    
    for fit_comp_col_1st in compscols_1st: # automatic color cycle 'cyan' ...
        ax.plot(FitData_1st['RamanShift'], FitData_1st[fit_comp_col_1st],ls='--',lw=4,label=fit_comp_col_1st)
        center_col, height_col = fit_comp_col_1st+'center', fit_comp_col_1st+'height'
        ax.annotate(f'{fit_comp_col_1st}:\n {FitPars[center_col].round(0).iloc[0]:.0f}',xy=(FitPars[center_col].iloc[0]*0.97,0.7*FitPars[height_col].iloc[0]),xycoords='data')
        
#    ax.plot(FitData_1st['RamanShift'], FitData_1st['D_'], color='lime',ls='--',lw=4,label='D')
#                ax.plot(FitData['RamanShift'], comps['D2_'], color='grey',ls='--',lw=4,label='D2')
#    ax.plot(FitData_1st['RamanShift'], FitData_1st['D3_'], 'b--',lw=4,label='D3')
#    ax.plot(FitData_1st['RamanShift'], FitData_1st['D4_'], color='purple',ls='--',lw=4,label='D4')
    if 'peaks' in peak1:
#        ax.plot(FitData_1st['RamanShift'], FitData_1st['D2_'], color='magenta',ls='--',lw=4,label='D2')
#        ax.annotate('D2:\n %.0f'%FitPars['D2_center'],xy=(FitPars['D2_center']*0.97,0.8*FitPars['I_D2']),xycoords='data')
        if 'Si_substrate' in peak1:
            ax.plot(FitData_1st['RamanShift'], FitData_1st['Si_substrate_'], 'b--',lw=4,label='Si_substrate')
            ax.annotate('Si_substrate:\n %.0f'%FitPars['Si_substrate_center'],xy=(FitPars['Si_substrate_center']*0.97,0.8*FitPars['I_Si_substrate']),xycoords='data')
#        if '6peaks' in FitModPeaks:
#            ax.plot(FitData_1st['RamanShift'], FitData_1st['D5_'],  color='darkorange',ls='--',lw=4,label='D5')
#            ax.annotate('D5:\n %.0f'%FitPars['D5_center'],xy=(FitPars['D5_center']*0.97,0.8*FitPars['I_D5']),xycoords='data')
##                    for colN,col in FitN.iteritems():
#                        if 'RamanShift' in colN or colN.split('_')[-1] == 'count' or colN.split('_')[-1] == 'std' :
#                            continue
#                        w,i = FitN['RamanShift'].values,col.values
#                        if 'mean' in colN:
#                            ax.plot(w[::],i[::],label=colN)
#                        else:
#                            ax.scatter(w[::],i[::],label=colN)
    if plot_Annotation:
        frsplit = res1_peak_spec.FitReport.split()
        if len(frsplit) > 200:
            fr = res1_peak_spec.FitReport.replace("prefix='D3_'", "prefix='D3_' \n")
        else:
            fr = res1_peak_spec.FitReport
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        Report1 = ax.text(1.01, 1,fr, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=props)
        Report2 = ax2nd.text(1.01, 0.7,res2_peak_spec.FitReport, transform=ax2nd.transAxes, fontsize=11,
            verticalalignment='top', bbox=props)

    ax.legend(loc=1), ax.set_xlabel('Raman shift (cm$^{-1}$)'),ax.set_ylabel('normalized I / a.u.')
    ax2nd.legend(loc=1), ax2nd.set_xlabel('Raman shift (cm$^{-1}$)'),ax2nd.set_ylabel('normalized I / a.u.')
#                plt.show()
    peak_destdir = res1_peak_spec.extrainfo.DestFittingComps.unique()[0].joinpath(f'{Model_data_col_1st}_{sID}')
#    plt.show()
    plt.savefig(peak_destdir.with_suffix('.png'),dpi=100,box_extra_artists=(Report1,Report2), bbox_inches='tight')
    plt.close()
    
#%%  
    return peak_destdir
        # place a text box in upper left in axes coords
#                    axAnn.text(1.05, 1, out.fit_report(min_correl=0.95), transform=ax.transAxes, fontsize=12,
#                        verticalalignment='top', bbox=props)
        
#        ax.annotate('D:\n %.0f'%FitPars['D_center'],xy=(FitPars['D_center']*0.97,0.8*FitPars['I_D']),xycoords='data')
#        ax.annotate('G:\n %.0f'%FitPars['G_center'],xy=(FitPars['G_center']*0.97,0.8*FitPars['I_G']),xycoords='data')
#        ax.annotate('$\mathrm{D_{3}: %.0f}$'%FitPars['D3_center'],xy=(FitPars['D3_center']*0.96,FitPars['I_D3']),xycoords='data')
#        ax.annotate('$\mathrm{D_{4}: %.0f}$'%FitPars['D4_center'],xy=(FitPars['D4_center']*0.96,FitPars['I_D4']*1.05),xycoords='data')
#        ax.annotate('$\mathrm{A_{D} / A_{G}: %.3f}$\n$\mathrm{A_{D3} / A_{G}: %.3f}$'%(FitPars['AD/AG'],FitPars['AD3/AG']),xy=(1800,0.4*FitPars['I_D']),xycoords='data')
#        ax.annotate('$\mathrm{L_{a} : %.3f nm}$\n$\mathrm{L_{eq} : %.3f nm}$'%(FitPars['L_a'],FitPars['L_eq']),xy=(1800,0.2*FitPars['I_D']),xycoords='data')
#                    ['GD1', 'D4D4', 'D1D1', '2D1'], ['GD1_center', 'D4D4_center', 'D1D1_center', 'D1D1center']
#        ax2nd.annotate('G+D1: %.0f'%FitPars_2nd['GD1_center'],xy=(FitPars_2nd['GD1_center']*0.97,1.1*FitPars_2nd['I_GD1']),xycoords='data')
#        ax2nd.annotate('2*D4: %.0f'%FitPars_2nd['D4D4_center'],xy=(FitPars_2nd['D4D4_center']*0.97,1.1*FitPars_2nd['I_D4D4']),xycoords='data')
#        ax2nd.annotate('2*D2: %.0f'%FitPars_2nd['D2D2_center'],xy=(FitPars_2nd['D2D2_center']*0.97,1.1*FitPars_2nd['I_D2D2']),xycoords='data')
#        ax2nd.annotate('2*D1: %.0f'%FitPars_2nd['D1D1_center'],xy=(FitPars_2nd['D1D1_center']*0.97,1.1*FitPars_2nd['I_D1D1']),xycoords='data')
#                    ax.annotate('$\mathrm{I_{D} / I_{G}: %.3f}$\n$\mathrm{I_{D3} / I_{G}: %.3f}$'%(FitPars['ID/IG'],FitPars['ID3/IG']),xy=(1800,0.4*FitPars['I_G']),xycoords='data')
        # these are matplotlib.patch.Patch properties
       
#        out_2nd.fit_report(min_correl=0.95)
#        ax.annotate('%.0f'%popt_bl[1],xy=(popt_bl[1]+50,0.57*(ypeak1+ypeak2)),xycoords='data')
#                if plot_Residuals:
#        #        axRes = fig.add_subplot(2,1,2)
#        #        axRes = plt.subplot(313, sharex=ax)
##                    axRes = plt.subplot(gs[1])
#                    axRes.plot(x,out.residual)
#                    axRes.plot(x,x*0,ls='--',c='grey')
#                    axRes.set_ylabel('Residuals')       

#    try:
#        plt.savefig(DestPlotDir.joinpath('%s%s_Baseline_mean.png'%(sID,EXT_2nd)),dpi=100,box_extra_artists=(Report1,Report2), bbox_inches='tight')
#        plt.close()
#        
#    except Exception as e:
#        print(sID,EXT_2nd)
##                    '%s%s_Baseline_mean.png'%(sID,EXT_2nd)
##                    print(Report1,Report2)
#        print('No Baseline mean plot, bbox extra; %s' %e)
#        try:
#            plt.savefig(DestPlotDir.joinpath('%s%s_Baseline_mean.png'%(sID,EXT_2nd)),dpi=100, bbox_inches='tight')
#            print('Second try fitted succes: %s%s'%(sID,EXT_2nd))
#            plt.close()
#        except:
#            print('%s%s_Baseline_mean.png'%(sID,EXT_2nd))
#            print('No Baseline mean plot; %s' %e)
##                        print('No Baseline mean plot')
#    plt.close()
#    sID,sGrp,FS,PosInts_Bg,PosInts_Bg_low,PosInts_Bg_mid,PosInts_Bg_2nd,DestExtraPlots
#        ax0,ax1 = ax[0,0],ax[0,1]
#        FS.plot(x='RamanShift',y=[i for i in FS.columns if sGrp in i and 'despiked' in i and 'norm' not in i and not 'mean' in i],ax=ax0)
##               ax.plot(FitData['RamanShift'],FitData['I_model4Voigt'],label='Fit_model4Voigt',lw=3,c='r')
#        ax0.legend(fontsize=10,ncol=2), ax0.set_xlabel('Raman shift (cm$^{-1}$)'),ax0.set_ylabel('I / a.u.')
##                    fig,ax = plt.subplots(1,1,figsize=(12,12))
#        FS.plot(x='RamanShift',y=[i for i in FS.columns if sGrp in i and 'norm' in i and not 'raw' in i and 'despiked_norm' in i and not 'mean' in i],ax=ax1,alpha=0.5)
#        FS.plot(x='RamanShift',y=[i for i in FS.columns if sGrp in i and 'norm' in i and not 'raw' in i and not 'despiked' in i and 'mean' in i and not 'out' in i],ax=ax1,c='grey',alpha=0.8)
#        FS.plot(x='RamanShift',y=[i for i in FS.columns if sGrp in i and 'norm' in i and not 'raw' in i and not 'despiked' in i and 'mean' in i and 'out' in i],ax=ax1,c='k',alpha=0.7)
##                    FS.plot(x='RamanShift',y=[i for i in FS.columns if sGrp in i and 'mean_raw_norm' in i],ax=ax)
##            ax.plot(FitData['RamanShift'],FitData['I_model4Voigt'],label='Fit_model4Voigt',lw=3,c='r')
#        ax2 = ax[1,0]
#        PosInts_Bg.plot(x='RamanShift',y=[i for i in PosInts_Bg.columns if '_Bg' in i and not 'mean' in i],ax=ax2,alpha=0.5)
#        PosInts_Bg.plot(x='RamanShift',y=[i for i in PosInts_Bg.columns if '_Bg_mean' in i],c='k',ax=ax2)
#        ax2.legend(loc=0,fontsize=10), ax2.set_xlabel('Raman shift (cm$^{-1}$)'),ax2.set_ylabel('normalized I / a.u.'),ax2.set_title('%s' %sID)  
#
#        ax_low = ax[0,2]
#        PosInts_Bg_low.plot(x='RamanShift',y=[i for i in PosInts_Bg_low.columns if '_Bg' in i and not 'mean' in i],ax=ax_low,alpha=0.5)
#        PosInts_Bg_low.plot(x='RamanShift',y=[i for i in PosInts_Bg_low.columns if '_Bg_mean' in i],c='k',ax=ax_low)
#        ax_low.legend(loc=0,fontsize=10),ax_low.set_title('low range')
#        ax_low.set_ylim(-0.05,0.5)   
##        , ax4.set_xlabel('Raman shift (cm$^{-1}$)'),ax4.set_ylabel('normalized I / a.u.')
#        ax_mid = ax[1,1]
#        PosInts_Bg_mid.plot(x='RamanShift',y=[i for i in PosInts_Bg_mid.columns if '_Bg' in i and not 'mean' in i],ax=ax_mid,alpha=0.5)
#        PosInts_Bg_mid.plot(x='RamanShift',y=[i for i in PosInts_Bg_mid.columns if '_Bg_mean' in i],c='k',ax=ax_mid)
#        ax_mid.legend(loc=0,fontsize=10), ax_mid.set_title('%s mid range' %sID)
#        ax_mid.set_ylim(-0.04,0.03)   
#        # ax4.set_xlabel('Raman shift (cm$^{-1}$)'),ax4.set_ylabel('normalized I / a.u.')
#
#        ax1.set_ylim(-0.2,2) 
#        ax1.set_title('despiked raw')
#        ax1.legend(fontsize=10), ax1.set_xlabel('Raman shift (cm$^{-1}$)'),ax1.set_ylabel('normalized I / a.u.'),ax1.set_title('%s, norm-baseline' %sID)
#      
#        ax3 = ax[1,2]
#        PosInts_Bg_2nd.plot(x='RamanShift',y=[i for i in PosInts_Bg_2nd.columns if '_Bg' in i and not 'mean' in i],ax=ax3,alpha=0.5)
#        PosInts_Bg_2nd.plot(x='RamanShift',y=[i for i in PosInts_Bg_2nd.columns if '_Bg_mean' in i],c='k',ax=ax3)
#        ax3.legend(loc=0,fontsize=10), ax3.set_xlabel('Raman shift (cm$^{-1}$)'),ax3.set_ylabel('normalized I / a.u.'),ax3.set_title('2nd order')
    
#        plt.savefig('%s.png' %os.path.join(Rdir,Rpng),dpi=300,bbox_inches='tight' )
#        plt.show()
#def plot_fit_output(self,out,comps,FitPars,FitData,DestDir,SampleID,Pos,plot_Components = True,plot_Annotation = True,plot_Residuals = True):
#    x,y,FileName,blcor = self.w1,self.i1_blcor,self.FileName,self.blcor    
##        'DestDir' : DestDir
#    FitPars.to_excel('%s_FitPars.xlsx' %os.path.join(DestDir,FileName))
#    FitData.to_excel('%s_FitSpectrum.xlsx' %os.path.join(DestDir,FileName))
#    
#    fig = plt.figure(figsize=(12,12))
#    gs = gridspec.GridSpec(2, 1,height_ratios=[4, 1])
##    fig.subplots_adjust(hspace=0.25, wspace=0.3)
##    ax = fig.add_subplot(3, 1, 2)
#    ax = plt.subplot(gs[0])
#
##    ax = plt.subplot(211)
##    ,figsize=(12,12))
#    ax.plot(x, y, 'k')
##    ax.plot(x, out.init_fit, 'm--',lw=1)
#    ax.plot(x, out.best_fit, 'm-',lw=6)
#    
#    XminorLocator = MultipleLocator(100)
#    YminorLocator = MultipleLocator(1)
#    ax.get_yaxis().set_tick_params(direction='in')
#    ax.get_xaxis().set_tick_params(direction='in')
#    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
#    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
#    ax.tick_params(which='both',direction='in')
#    
#    ax.set_xlabel('Raman shift (cm$^{-1}$)')
#    ax.set_ylabel('I / a.u.')
#    ax.set_title('%s' %FileName)
#    
#    if plot_Components:
#        comps = out.eval_components(x=x)
#        if x.max() > 2200:
#            ax.plot(x, comps['2G_'],color='cyan',ls='--',lw=4,label='2*G')
#            ax.plot(x, comps['2D_'], color='lime',ls='--',lw=4,label='2*D')
#            ax.plot(x, comps['D4D4_'], color='purple',ls='--',lw=4,label='2*D4')
#            ax.plot(x, comps['GD1_'], color='pink',ls='--',lw=4,label='G+D1')
#        if x.max() > 300 and x.max() < 2200:
#            ax.plot(x, comps['G_'],color='cyan',ls='--',lw=4,label='G')
#            ax.plot(x, comps['D_'], color='lime',ls='--',lw=4,label='D')
#            ax.plot(x, comps['D4_'], 'r--',lw=4,label='D4')
#            ax.plot(x, comps['D3_'], 'b--',lw=4,label='D3')
##        plt.plot(x, comps['exp_'], 'k--',lw=4)
#    if plot_Annotation:
#        ax.annotate('D:\n %.0f'%FitPars['D_center'],xy=(FitPars['D_center']*0.97,0.8*FitPars['I_D']),xycoords='data')
#        ax.annotate('G:\n %.0f'%FitPars['G_center'],xy=(FitPars['G_center']*0.97,0.8*FitPars['I_D']),xycoords='data')
#        ax.annotate('$\mathrm{D_{3}: %.0f}$'%FitPars['D3_center'],xy=(FitPars['D3_center']*0.96,FitPars['I_D3']),xycoords='data')
#        ax.annotate('$\mathrm{D_{4}: %.0f}$'%FitPars['D4_center'],xy=(FitPars['D4_center']*0.96,FitPars['I_D4']*1.05),xycoords='data')
#        ax.annotate('$\mathrm{I_{D} / I_{G}: %.3f}$\n$\mathrm{I_{D3} / I_{G}: %.3f}$'%(FitPars['ID/IG'],FitPars['ID3/IG']),xy=(1800,0.4*FitPars['I_G']),xycoords='data')
#        # these are matplotlib.patch.Patch properties
#        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
#        # place a text box in upper left in axes coords
#        ax.text(1.05, 1, out.fit_report(min_correl=0.95), transform=ax.transAxes, fontsize=15,
#            verticalalignment='top', bbox=props)
##        ax.annotate('%.0f'%popt_bl[1],xy=(popt_bl[1]+50,0.57*(ypeak1+ypeak2)),xycoords='data')
#    if plot_Residuals:
##        axRes = fig.add_subplot(2,1,2)
##        axRes = plt.subplot(313, sharex=ax)
#        axRes = plt.subplot(gs[1])
#        axRes.plot(x,out.residual)
#        axRes.plot(x,x*0,ls='--',c='grey')
#        axRes.set_ylabel('Residuals')
#    
##        plt.savefig('%s_Fit.png' %os.path.join(DestDir,FileName),dpi=300,bbox_inches='tight' )
#    plt.show()
#    plt.close()
##        return out

