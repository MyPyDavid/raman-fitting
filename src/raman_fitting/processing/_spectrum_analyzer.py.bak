#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# flake8: noqa


# WARNING this module is not used
# TODO remove this module

class SpectrumAnalyzer:

    def __init__(self,RaSh,Int,FileName,freqMin = 800,freqMax = 2000,Noise_filter = False,
                 plot_Components = True,plot_Annotation = True,plot_Resiudals = True,GammaVary = True,RAMAN_bgCorr_Plot = False):
        self.RaSh = RaSh
        self.Int = Int
        self.FileName = FileName
        self.freqMin,self.freqMax = freqMin,freqMax
        self.Noise_filter = Noise_filter
#        ,DestDir,FileName,SampleID,Pos
#        self.RAMAN_bgCorr_Plot = RAMAN_bgCorr_Plot self.w1,self.i1_blcor
#        self.subtract_bg()
        self.w,self.i_blcor,self.blcor,self.w1,self.i1_blcor = self.subtract_bg()
   
#    def subtract_baseline(self):
#        ind = (self.RaSh > freqMin) & (self.RaSh < freqMax)
#        w1,i1 = self.RaSh[ind],self.Int[ind]
#        bl_lin = linregress(w1[[0,-1]],[np.mean(i1[0:20]),np.mean(i1[-20::])])
#        return self.Int-(bl_lin[0]*self.RaSh+bl_lin[1])

    def subtract_bg(self,RAMAN_bgCorr_Plot = False,output = False):
        w,i,FileName,freqMin,freqMax = self.RaSh,self.Int,self.FileName,self.freqMin,self.freqMax
        Noise_filter = self.Noise_filter
        
#        ,len(i_Bg)
#        i_blcor = self.RAMAN_subtract_baseline()
        if Noise_filter != False:
            filer_win,filter_polyn = Noise_filter
            i = scipy.signal.savgol_filter(i, filer_win,filter_polyn)
            
        ind = (w > freqMin) & (w < freqMax)
        w1,i1= w[ind],i[ind]
        
            
        
        if freqMin > 600 and freqMax <2100:
            bl_lin = linregress(w1[[0,-1]],[np.mean(i1[0:20]),np.mean(i1[-20::])])
        elif freqMin > 2050:
            bl_lin = linregress(w1[[0,-1]],[np.mean(i1[0:5]),np.mean(i1[-5::])])
        else:
            bl_lin = linregress(w1[[0,-1]],[np.mean(i1[0:3]),np.mean(i1[-10::])])
        i_blcor = i-(bl_lin[0]*w+bl_lin[1])
        i1_blcor = i_blcor[ind]
        blcor = pd.DataFrame({'Raman-shift' : w, 'I_bl_corrected' :i_blcor, 'I_raw_data' : i})
        blcor,i_blcor = SpectrumAnalyzer.Despike(blcor,'I_bl_corrected')
        blcor1 = pd.DataFrame({'Raman-shift' : w1, 'I_bl_corrected' :i1_blcor, 'I_raw_data' : i1})
        blcor1, i_blcor1 = SpectrumAnalyzer.Despike(blcor1,'I_bl_corrected')
        
        if output:
            print('DEFINE DESTDIR IN subtract_bg output!')
            blcor.to_excel('%s_Spectrum-bl.xlsx' %os.path.join(DestDir,FileName))
        if RAMAN_bgCorr_Plot:
            fig,ax = plt.subplots(2,1,figsize=(12,12))
            ax[0].set_title(FileName)
            ax[0].plot(w, (bl_lin[0]*w+bl_lin[1]),c='black',ls='-',label='baseline')
    ##        ax.plot(w, (blfit(w)), 'orange')
            ax[0].plot(w, i, 'b.',label='raw data')
            ax[1].plot(w1, i1_blcor, 'b.',label='bl_cor data')
#            plt.show()
            plt.close()
      #    Take detrended difference Serie = dYt, M=median, MAD= median (|dYt-M|)
      #    Zt = ( 0.6745 * (dYt - M)) / MAD
        
        return w,i_blcor,blcor,w1,i_blcor1
    @staticmethod
    def subtract_baseline(x,y,freqMin,freqMax):
        ind = (x > freqMin) & (x < freqMax)
        w1,i1 = x[ind],y[ind]
        if freqMin > 600 and freqMax <2100:
            bl_lin = linregress(w1[[0,-1]],[np.mean(i1[0:20]),np.mean(i1[-20::])])
        elif freqMin > 2050:
            bl_lin = linregress(w1[[0,-1]],[np.mean(i1[0:20]),np.mean(i1[-20::])])
        else:
            bl_lin = linregress(w1[[0,-1]],[np.mean(i1[0:10]),np.mean(i1[-10::])])
#        bl_lin = linregress(w1[[0,-1]],[np.mean(i1[0:20]),np.mean(i1[-20::])])
        return y-(bl_lin[0]*x+bl_lin[1])
    
    @staticmethod
    def Despike(blcor,Ystr): 
        y = blcor[Ystr]
        dYt = y.diff()
        M = dYt.median()
    #    dYt_M =  dYt-M
        MAD = dYt.mad()
        Z_t = (0.6745*(dYt-M)) / MAD
        blcor = blcor.assign(**{'abs_Z_t': Z_t.abs()})
        Zmin = 3.5
        if blcor.query('abs_Z_t > @Zmin').empty:
#            print('No spikes in window')
            i_blcor = blcor[Ystr].values
        else:
            blcor.query('abs_Z_t > @Zmin')
    #        blcor.rolling(on='I_bl-corrected',window=10).mean().plot(x='Raman-shift',y='I_bl-corrected')
            blcor = blcor.assign(**{'I_spike_corr': blcor[Ystr]})
            blcor.loc[blcor['abs_Z_t'] > Zmin, 'I_spike_corr'] = np.nan
            blcor['I_spike_corr'].interpolate(method = 'nearest',inplace=True)
    #        blcor = blcor.assign(**{'I_spike_corr': blcor['I_bl_corrected'].interpolate(method = 'nearest')})
    #        blcor.plot(x='Raman-shift', y=['I_bl_corrected', 'I_spike_corr'])
            i_blcor = blcor['I_spike_corr'].values
#            print('!Spikes are removed!')
#        print(len(w),len(i),len(i_blcor))
        return blcor,i_blcor
   
        
