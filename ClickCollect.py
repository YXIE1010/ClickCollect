#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 12:33:18 2023

@author: yanxieyx
"""

#%%
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import MouseButton
import netCDF4 as nc
import numpy.ma
import datetime
import matplotlib.cm as cm
import glob
import time as time_module
import sys

#%%
class InteractiveDrawing:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(12,6), dpi=200)
        self.lines, = self.ax.plot([], [], '-o', linewidth=0.4, markersize=0.6, color='#EB455F')  # Initial empty line with marker 'o'
        self.linesnew, = self.ax.plot([], [], '-^', linewidth=0.4, markersize=0.6, color='#005B41')  
        self.xdata, self.ydata = [], []
        self.xdatanew, self.ydatanew = [], []
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.cid_move = self.fig.canvas.mpl_connect('motion_notify_event', self.onmove)
        self.cid_del = self.fig.canvas.mpl_connect('button_release_event', self.ondel)
        self.cid_end = self.fig.canvas.mpl_connect('key_press_event', self.onkey)
        self.prev_point = None
        self.background = None
        self.active_point = None
        self.dragging_point = None
        self.last_click_time = 0
        self.CLICK_DRAG_THRESHOLD = 5

    def distance(self, x1, y1, x2, y2):
        return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    def onclick(self, event):
        current_time = time_module.time()
        # Prevent processing if the click is too soon after the last
        if current_time - self.last_click_time < 0.2:  # 0.2 second delay
            return
        self.last_click_time = current_time  # Update the last click timestamp

        # Check if the click is near any existing point
        self.dragging_point = None
        for idx, (x, y) in enumerate(zip(self.xdata, self.ydata)):
            if abs(x - event.xdata) < self.CLICK_DRAG_THRESHOLD and abs(y - event.ydata) < self.CLICK_DRAG_THRESHOLD:  # threshold to check "closeness"
                self.dragging_point = idx                
                return  # exit once we find a nearby point

        # If we reached here, then it's a new point addition
        if (event.button is MouseButton.LEFT) and event.xdata:
            self.xdata.append(event.xdata)
            self.ydata.append(event.ydata)
            self.prev_point = (event.xdata, event.ydata)
            
            self.lines.set_xdata(self.xdata)
            self.lines.set_ydata(self.ydata)
            self.blit()
    
    
    def onmove(self, event):               
        # If we're dragging an existing point
        if self.dragging_point is not None:
            self.xdata[self.dragging_point] = event.xdata
            self.ydata[self.dragging_point] = event.ydata
            
            #self.xdatanew = [self.xdata[self.dragging_point-1], event.xdata, self.xdata[self.dragging_point+1]]
            #self.ydatanew = [self.ydata[self.dragging_point-1], event.ydata, self.ydata[self.dragging_point+1]]
            #self.xdatanew = [self.xdata[self.dragging_point-1:self.dragging_point+2]]
            #self.ydatanew = [self.ydata[self.dragging_point-1:self.dragging_point+2]]            
                        
            #self.linesnew.set_xdata(self.xdatanew)
            #self.linesnew.set_ydata(self.ydatanew)
            
            self.lines.set_xdata(self.xdata)
            self.lines.set_ydata(self.ydata)
            self.blit()
            
            #self.blitnew()
            return

        # For adding a new point
        if self.prev_point and event.xdata and event.ydata:
            tmp_xdata = self.xdata + [event.xdata]
            tmp_ydata = self.ydata + [event.ydata]

            self.lines.set_xdata(tmp_xdata)
            self.lines.set_ydata(tmp_ydata)
            self.blit()
    
    
    def mouse_move(self, event):
        xm, ym = event.xdata, event.ydata
        for idx, (x, y) in enumerate(zip(self.xdata, self.ydata)):
            if abs(x - xm) < self.CLICK_DRAG_THRESHOLD and abs(y - ym) < self.CLICK_DRAG_THRESHOLD:  # threshold to check "closeness"
                self.xdatanew = [self.xdata[-1], xm ]
                self.ydatanew = [self.ydata[-1], ym ]
                self.linesnew.set_xdata(self.xdatanew)
                self.linesnew.set_ydata(self.ydatanew)
                self.blitnew() 


    def blit(self):
        # If background is None, capture the canvas state
        if self.background is None:
            self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        else:
            # Restore the canvas state
            self.fig.canvas.restore_region(self.background)
        
        # Redraw just the changed artist (line in this case)
        self.ax.draw_artist(self.lines)
        
        # Blit the affected area
        self.fig.canvas.blit(self.ax.bbox)
    
        
    def blitnew(self):
        # If background is None, capture the canvas state
        if self.background is None:
            self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        else:
            # Restore the canvas state
            self.fig.canvas.restore_region(self.background)
        
        # Redraw just the changed artist (line in this case)
        self.ax.draw_artist(self.lines)
        self.ax.draw_artist(self.linesnew)
        
        # Blit the affected area
        self.fig.canvas.blit(self.ax.bbox)
    
    
    def ondel(self, event):
        if event.button == 1:  # If the left mouse button is released
            self.dragging_point = None

        if (event.button is MouseButton.RIGHT) and self.prev_point:
            # If we're dragging an existing point, remove it
            if self.dragging_point is not None:
                del self.xdata[self.dragging_point]
                del self.ydata[self.dragging_point]
                self.dragging_point = None  # Reset the dragging point

                self.lines.set_xdata(self.xdata)
                self.lines.set_ydata(self.ydata)
                self.ax.figure.canvas.draw()
                return

            # Delete the current data points (for new point addition)
            self.xdata.pop(-1)
            self.ydata.pop(-1)

            self.lines.set_xdata(self.xdata)
            self.lines.set_ydata(self.ydata)
            self.ax.figure.canvas.draw()
            
    def onkey(self, event):
        plt.close()
        return
        ###### This part needs further improvements ######
        # Ideal output:                                  #
        # If xdata & ydata are not empty list, return    # 
        # filled values as a mask                        #
        # Otherwise if no melting layer was picked       #
        # return a mask filled with zeros                #
        ##################################################
                                        
    
    def show(self, isec, time, rag, dVd, hrstr):
        # Plot the doppler velocity gradient figure: Top level
        #plt.figure(figsize=(10,6), dpi=200)    
        plt.pcolormesh(time, rag, dVd, cmap = cm.RdBu_r, vmin = -0.02, vmax =0.02)
        plt.colorbar(label = 'm $\mathregular{s^{-1}}$')        
        plt.title('Doppler velocity gradient', fontsize=10)
        plt.xticks(np.arange(isec*60*60, (isec+6)*60*60+1, 60*60), hrstr,\
                   fontsize = 9)
        plt.xlim([isec*60*60, (isec+6)*60*60+1])
        plt.ylabel('Height AGL (km)', fontsize=10) #height above ground level
        plt.yticks(np.arange(2,10,2))
        
        plt.connect('motion_notify_event', self.mouse_move)
        
        plt.show()



#%%
def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).
    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


#%%
if __name__ == '__main__':     # used to excute the code when the file is run directly, and not imported as a module
    # load KAZR data for one day
    fpathin = '/your/input/filepath/'          # filepath
    
    # filepath for output data
    fpathout = '/your/output/filepath/'
    
    ########## Info of chosen dates ##########
    # each row stands for one chosen date
    # there are three columns standing for (1)iyear; (2)imonth; (3)iday  
    dinfo = np.zeros((15,3))
    
    # load the date info      
    # take May 2015 for an example
    dinfo[:,0] = 2015
    dinfo[:,1] = 5
    dinfo[:,2] = np.array([9, 11, 12, 15, 16,\
                                 17, 18, 19, 21, 22,\
                                 25, 26, 28, 29, 31])

    
    ##########################################
    #for icase in range(0, dinfo.shape[0]):
    for icase in range(0, 15):
        iyear = int( dinfo[icase, 0] )
        imon = int( dinfo[icase, 1] )
        iday = int( dinfo[icase, 2] )
        
        flagday = 0
        
        if iyear < 2019:
            fname = 'nsakazrgeC1.a1.' + '{:4d}'.format(iyear) + '{:02d}'.format(imon)\
                    + '{:02d}'.format(iday) + '.??????'+'.cdf'
        elif iyear > 2019:
            fname = 'nsakazrcfrgeC1.a1.' + '{:4d}'.format(iyear) + '{:02d}'.format(imon)\
                    + '{:02d}'.format(iday) + '.??????'+'.nc'
            flagday = 1
        elif iyear == 2019:
            if imon < 10:
                fname = 'nsakazrgeC1.a1.' + '{:4d}'.format(iyear) + '{:02d}'.format(imon)\
                        + '{:02d}'.format(iday) + '.??????'+'.cdf'
            elif imon > 10:
                fname = 'nsakazrcfrgeC1.a1.' + '{:4d}'.format(iyear) + '{:02d}'.format(imon)\
                        + '{:02d}'.format(iday) + '.??????'+'.nc'
                flagday = 1
            elif imon == 10:
                if iday < 28:
                    fname = 'nsakazrgeC1.a1.' + '{:4d}'.format(iyear) + '{:02d}'.format(imon)\
                        + '{:02d}'.format(iday) + '.??????'+'.cdf'   
                elif iday >= 28:
                    fname = 'nsakazrcfrgeC1.a1.' + '{:4d}'.format(iyear) + '{:02d}'.format(imon)\
                            + '{:02d}'.format(iday) + '.??????'+'.nc'
                    flagday = 1
        
        # KAZR filename '??????' refers to Hours/Minutes/Seconds 'HHMMSS'
        flist = glob.glob( fpathin + fname )          # return a list of file
        filenum = len(flist)
        if filenum == 1:
            f = nc.Dataset(flist[0], 'r') 
            # Variables
            if flagday == 0:
                base_time = f.variables['base_time'][:]
                time = f.variables['time_offset'][:]                           # seconds since YYYY-MM-DD base_time
                rag = f.variables['range'][:]                                  # range(center of radar sample volume), units: m
                Ze_cp = f.variables['reflectivity_copol'][:]                   # Reflectivity, copolar, units: dBZ
                Vd_cp = f.variables['mean_doppler_velocity_copol'][:]          # Mean doppler velocity, copolar, units: m/s Positive values indicate motion away from the radar
                SNR_cp = f.variables['signal_to_noise_ratio_copol'][:]         # Signal to noise ratio, copolar, unit: dB
                lat = f.variables['lat'][:]                                    # North latitude
                lon = f.variables['lon'][:]                                    # East longitude
            elif flagday ==1:
                base_time = f.variables['base_time'][:]
                time = f.variables['time_offset'][:]
                rag = f.variables['range'][:]
                Ze_cp = f.variables['reflectivity'][:]
                Vd_cp = f.variables['mean_doppler_velocity'][:]
                SNR_cp = f.variables['signal_to_noise_ratio_copolar_h'][:]
                lat = f.variables['lat'][:]
                lon = f.variables['lon'][:]
            # Define falling towards the radar as positive
            Vd_cp = -Vd_cp
            
            # Absolute time     
            time_abs = base_time + time
            # tstr = datetime.datetime.utcfromtimestamp(time_abs[0]).strftime('%Y-%m-%d %H:%M:%S')   # time string
            
        elif filenum > 1:
            # Sort the list of files according to filenames
            flist.sort()  # sort the list in ascending order
            
            # Combine all the separate data files
            for ifname in range(0, filenum):
                f = nc.Dataset(flist[ifname], 'r')
                # Variables
                if flagday == 0:
                    base_time0 = f.variables['base_time'][:]
                    time0 = f.variables['time_offset'][:]                             # seconds since YYYY-MM-DD base_time
                    rag0 = f.variables['range'][:]                             # range(center of radar sample volume), units: m
                    Ze_cp0 = f.variables['reflectivity_copol'][:]              # Reflectivity, copolar, units: dBZ
                    Vd_cp0 = f.variables['mean_doppler_velocity_copol'][:]     # Mean doppler velocity, copolar, units: m/s Positive values indicate motion away from the radar
                    SNR_cp0 = f.variables['signal_to_noise_ratio_copol'][:]    # Signal to noise ratio, copolar, unit: dB
                    lat0 = f.variables['lat'][:]                               # North latitude
                    lon0 = f.variables['lon'][:]                               # East longitude
                elif flagday == 1:
                    base_time0 = f.variables['base_time'][:]
                    time0 = f.variables['time_offset'][:]
                    rag0 = f.variables['range'][:]
                    Ze_cp0 = f.variables['reflectivity'][:]
                    Vd_cp0 = f.variables['mean_doppler_velocity'][:]
                    SNR_cp0 = f.variables['signal_to_noise_ratio_copolar_h'][:]
                    lat0 = f.variables['lat'][:]
                    lon0 = f.variables['lon'][:]
                
                # Define falling towards the radar as positive
                Vd_cp0 = -Vd_cp0
            
                # Absolute time     
                time_abs0 = base_time0 + time0 
                
                if ifname == 0:
                    base_time = base_time0
                    rag = rag0
                    lat = lat0
                    lon = lon0
                    
                    time = time0.copy()
                    Ze_cp = Ze_cp0.copy()
                    Vd_cp = Vd_cp0.copy()
                    SNR_cp = SNR_cp0.copy()
                    time_abs = time_abs0.copy()
                    
                elif ifname > 0:
                    time = np.append(time, time0, axis=0)
                    Ze_cp = np.append(Ze_cp, Ze_cp0, axis=0)
                    Vd_cp = np.append(Vd_cp, Vd_cp0, axis=0)
                    SNR_cp = np.append(SNR_cp, SNR_cp0, axis=0)
                    time_abs = np.append(time_abs, time_abs0, axis=0)
                    
            del base_time0, time0, rag0, Ze_cp0, Vd_cp0, SNR_cp0, lat0, lon0, time_abs0
                              
                
        elif filenum < 1:
            print('Data missing: ' + fname)
            continue                                                       # If data missing, continue on the next iteration    

              
        date = datetime.datetime.utcfromtimestamp(time_abs[0]) 
        year = date.year
        mon = date.month
        day = date.day
    
        # Melting-level height detection
        """
        Steps of the melting level height detection

        (1) Check quality control of the input data: missing value= -9999.0
        filling on, default _FillValue of 9.9692e+36 used
        mask=False, fill_value=1e+20
        
        (2) Determine the background noise mask: Using the threshold of signal to noise
        ratio 
        
        (3) Divide one day into 6hr-sections
        
        (4) Annotate precipitation occurrence: Ze >= -10 dBz at the fourth range bins,
        i.e., at the height of 190.6 m
        
        (5) Annotate rainfall occurrence: Doppler velocity Vd >= 3 m/s at the fourth 
        range bin, i.e., at the height of 190.6 m
        
        (6) Sanity check: plot the manually picked melting level height back on the figure

        (7) !!! To be implemented !!! Ask for used input of status, i.e., rain / snow /
        mixed / non-preci / rain with multiple melting layers for each section
        
        """
        
        # Step (1): Check invalid values
        MaskZe0 = np.ma.masked_where( (Ze_cp<=-9999)|(Ze_cp>=1e+10), Ze_cp ).mask
        MaskVd0 = np.ma.masked_where( (-Vd_cp<=-9999)|(-Vd_cp>=1e+10), Vd_cp ).mask
        Ze_cp = np.where( np.logical_not(MaskZe0), Ze_cp, np.nan )
        Vd_cp = np.where( np.logical_not(MaskVd0), Vd_cp, np.nan )

        # Step (2): Remove background noise using signal to noise ratio
        #           And replace the noises with NaN values 
        MaskNoi = np.ma.masked_less(SNR_cp, -15).mask 
        noMaskNoi = np.logical_not(MaskNoi)
        Ze_new = np.where(noMaskNoi, Ze_cp, np.nan)
        Vd_new = np.where(noMaskNoi, Vd_cp, np.nan)
        

        id_preci = np.where( Ze_new[:,3] >= -10 )[0]     # index for precipitation
        maskPre = np.ma.masked_less(Ze_new[:,3], -10).mask
        MaskPre = np.repeat( np.reshape(maskPre, (maskPre.size,1)), rag.size, axis=1 )
        noMaskPre = np.logical_not(MaskPre)
        Ze_pre = np.where(noMaskPre, Ze_new, np.nan)
        Vd_pre = np.where(noMaskPre, Vd_new, np.nan)

        id_rain = np.intersect1d( id_preci, np.where( (Vd_new[:,3] >=3) | (Vd_new[:,3]<-3) )[0])   # index for rainfall

        # Compute the Doppler Velocity gradient: bin height 30 m
        dVdpre = np.gradient(Vd_pre, axis=1) / 30
        dVd = np.gradient(Vd_new, axis=1) / 30
        
        # Step (3): Divide into 6hr-sections
        """
        ! Consider including both Ze and Vd as the input variables !
        """
        hourstr = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00',\
                   '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',\
                   '12:00', '13:00', '14:00', '15:00', '16:00', '17:00',\
                   '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '24:00']
        
        for isec in range(0, 24, 6): #range(0,24,6):
            idtime = np.where( (time>=isec*60*60) & (time<(isec+6)*60*60) )[0]
            timesec = time[idtime]
            timeabssec = time_abs[idtime]
            #timepreci = time[ np.intersect1d(idtime, id_preci) ]
            #timerain = time[ np.intersect1d(idtime, id_rain) ]
            id_precisec = np.intersect1d(idtime, id_preci)
            ragsec = rag[3:265] / 1000.    
            hrstrsec = hourstr[isec:(isec+7)]
            dVdsec = np.transpose(dVd[idtime,3:265])
            dVdpresec = np.transpose(dVdpre[idtime, 3:265])
            MaskNoisec = np.transpose(MaskNoi[idtime, 3:265])
            
            # Plot the Ze and Vd to determine whether the melting layer exists
            Zesec = np.transpose( Ze_new[idtime,3:265] )
            Vdsec = np.transpose( Vd_new[idtime,3:265] )
            
            fig, axes = plt.subplots(2,1, figsize=(6,5), gridspec_kw={'height_ratios':[1,1]}, dpi=300)
            fig.subplots_adjust(right=0.85)
            fig.suptitle('{:4d}'.format(year) + '-' + '{:02d}'.format(mon) + \
                         '-' + '{:02d}'.format(day), fontsize=8 )

            ax = plt.subplot(2,1,1)
            pc = axes[0].pcolormesh(timesec, ragsec, Zesec, cmap = cm.Spectral_r,vmin = -40, vmax= 30)
            axes[0].set_xticks(np.arange(isec*60*60, (isec+6)*60*60+1, 60*60))
            axes[0].set_xticklabels([])
            plt.xlim([isec*60*60, (isec+6)*60*60+1])
            plt.ylabel('Height AGL (km)', fontsize=7) #height above ground level
            plt.yticks(np.arange(2,10,2), fontsize=6) 
            plt.title('(a) Radar Reflectivity', loc='left', fontsize=7)       
            # add colorbar without taking space from the subplot 
            sub_ax = fig.add_axes([0.87, 0.55, 0.015, 0.3])   # add a small custom axis
            cb1 = plt.colorbar(pc, cax=sub_ax)
            cb1.ax.tick_params(labelsize=7)
            cb1.set_label(label='dBZ', size=7)

            ax = plt.subplot(2,1,2)
            pc2 = axes[1].pcolormesh(timesec, ragsec, Vdsec, cmap = cm.RdBu_r, vmin = -3, vmax =3)        
            axes[1].set_xticks(np.arange(isec*60*60, (isec+6)*60*60+1, 60*60))
            axes[1].set_xticklabels(hrstrsec, fontsize=7)
            plt.xlim([isec*60*60, (isec+6)*60*60+1])
            plt.ylabel('Height AGL (km)', fontsize=7) #height above ground level
            plt.yticks(np.arange(2,10,2), fontsize=6)
            plt.title('(b) Dopper Velocity', loc='left', fontsize=7)
            # add colorbar without taking space from the subplot #####
            sub_ax2 = fig.add_axes([0.87, 0.12, 0.015, 0.3])   # add a small custom axis
            cb2 = plt.colorbar(pc2, cax=sub_ax2)
            cb2.ax.tick_params(labelsize=7)
            cb2.set_label(label='m $\mathregular{s^{-1}}$', size=7)
            
            plt.show()
            ###################################################################        
            
            if query_yes_no("Does melting layer exist in this case?"):
               # number of melting layers                  
               nml = 0
               ############### melting layer loop start ##############
               print('----- ' + '{:4d}'.format(year) + '{:02d}'.format(mon) + \
                     '{:02d}'.format(day) + '  ' + '{:02d}'.format(isec) + \
                     '-' + '{:02d}'.format(isec+6) + 'hr' + ' -----')
               
               while query_yes_no("Start/Continue with the current melting layer?"):
                   nml = nml+1
                   print('--- current melting layer NO. ' + '{:2d}'.format(nml) + \
                         ' ---')
                   mlsec = 0
                   ######################## section loop start ###########################
                   while query_yes_no("Start/Continue to select melting layer sections?"):
                       # this loop will forever run until interrupted
                       # each loop for one section of non-consecutive melting layer                            
                       mlsec = mlsec + 1 # number of sections in the current melting layer
                       
                       # Call the interactive drawing function 
                       print('Click on the upper boundary of the melting layer')
                       drawerup = InteractiveDrawing()
                       drawerup.show(isec, timesec, ragsec, dVdsec, hrstrsec)    
                       # get the x-y position of clicked data points         
                       xup0 = drawerup.xdata
                       yup0 = drawerup.ydata
                   
                       print('Click on the lower boundary of the melting layer')
                       drawerlower = InteractiveDrawing()
                       drawerlower.show(isec, timesec, ragsec, dVdsec, hrstrsec)
                       # get the x-y position of clicked data points
                       xlower0 = drawerlower.xdata
                       ylower0 = drawerlower.ydata
                       
                       # Interpolate into the original temporal resolution, with no interpolation outside the range
                       yup_temp = np.interp( timesec, xup0, yup0, left = np.nan, right = np.nan )
                       ylower_temp = np.interp( timesec, xlower0, ylower0, left = np.nan, right = np.nan )
                                          
                       if mlsec == 1:
                           yup1 = yup_temp.copy()
                           ylower1 = ylower_temp.copy()
                           
                       elif mlsec > 1:
                           yup1[~np.isnan(yup_temp)] = yup_temp[~np.isnan(yup_temp)]
                           ylower1[~np.isnan(ylower_temp)] = ylower_temp[~np.isnan(ylower_temp)]
                                                                   
                   ######################### section loop end #############################                         
               
                   # Quality check: make sure the lower boundary is lower than the higher boundary
                   if np.min( yup1 - ylower1 ) < 0 :
                       print("Error in data clicking: lower boundary higher than upper boundary")
                       break
               
                   # If the collected data points pass the quality control
                   # Step 1: create a mask with 1 for melting layer, 0 for others
                   mask_ml = np.zeros( dVdsec.shape )
               
                   # Step 2: prepare the upper and lower boundary
                   yup = np.copy(yup1)
                   ylow = np.copy(ylower1)
                   # exclude all the moments beyond the range of clicked data points 
                   yup[ np.where( (timesec<np.min(xup0)) & (timesec>np.max(xup0)) )[0] ] = np.nan
                   ylow[ np.where( (timesec<np.min(xlower0)) & (timesec>np.max(xlower0)) )[0] ] = np.nan
               
                   # Step 3: fill in the gap between lower and upper boundary
                   if mask_ml.shape[1] == yup.shape[0]:
                       for iid in range(0, mask_ml.shape[1]):
                           idrag = np.where( (ragsec >= ylow[iid]) & (ragsec <= yup[iid]) )[0]
                           # exclude all the background noise pixels
                           if any( MaskNoisec[idrag,iid] ):
                               yup[iid] = np.nan
                               ylow[iid] = np.nan
                       
                           # exclude all the non-melting part between two melting layer sections
                           if all( np.isnan(dVdsec[idrag,iid]) ):
                               yup[iid] = np.nan
                               ylow[iid] = np.nan
                           elif np.nanmin(dVdsec[idrag,iid]) > -0.0075 * 0.25:
                               yup[iid] = np.nan
                               ylow[iid] = np.nan
                           
                           if (~np.isnan(yup[iid])) and (~np.isnan(ylow[iid])):
                               mask_ml[idrag, iid] = 1                    
                    
                   if nml == 1:
                       MASK_ml = mask_ml.copy()
                       Yup = yup[:, np.newaxis]
                       Ylow = ylow[:,np.newaxis]
                       
                   elif nml > 1:
                       MASK_ml[mask_ml==1] = 1 
                       Yup = np.concatenate((Yup, yup[:,np.newaxis]), axis=1)
                       Ylow = np.concatenate((Ylow, ylow[:, np.newaxis]), axis=1)
                                          
                   print('--- End of melting layer NO. ' + '{:2d}'.format(nml) + \
                         ' ---\n')
                        
                                                                            
               ################ melting layer loop end ###############
                                                 
               id_timesec = id_precisec - idtime[0]    # convert from time index to timesection index
               
               # Step 4: plot the mask for detected melting layer for visual validation
               fig_ml = plt.figure(figsize=(6,3.6), dpi=300)
               plt.pcolormesh(timesec, ragsec, dVdsec, cmap = cm.RdBu_r, vmin = -0.02, vmax =0.02)
               plt.colorbar(label = 'm $\mathregular{s^{-1}}$')
               # add clicked data points
               idmask = np.where( np.transpose(MASK_ml) > 0 )
               plt.scatter( timesec[idmask[0]],ragsec[idmask[1]],\
                        s=0.005, c='#FFC436', marker = 'o', alpha=0.15 )
               plt.xticks(np.arange(isec*60*60, (isec+6)*60*60+1, 60*60), hrstrsec,\
                       fontsize = 9)
               plt.xlim([isec*60*60, (isec+6)*60*60+1])
               plt.ylabel('Height AGL (km)', fontsize=10) #height above ground level
               plt.yticks(np.arange(2,10,2))
               plt.title('Doppler velocity gradient', fontsize=10)
               plt.show()
               
               if query_yes_no("Melting layer detected, continue to save the figure?"):
                   # save the figure w. detected melting layer
                   fig_ml.savefig(fpathout+'Figure/'+ 'OutputMLy_' + '{:4d}'.format(year) + '{:02d}'.format(mon)\
                              + '{:02d}'.format(day) + '_' + '{:02d}'.format(isec)\
                              + '-' + '{:02d}'.format(isec+6) + 'hr' + '.png', dpi=300)
                   plt.close()
               
               
               if query_yes_no("Melting layer detected, continue to save the data?"):
                   
                   # save output data
                   fnameout_ML = 'OutputMLy_' + '{:4d}'.format(year) + '{:02d}'.format(mon)\
                              + '{:02d}'.format(day) + '_' + '{:02d}'.format(isec)\
                              + '-' + '{:02d}'.format(isec+6) + 'hr' + '.nc'     
                   
                   ds = nc.Dataset(fpathout+fnameout_ML, 'w', format = 'NETCDF4')
                   
                   # add dimensions
                   ds.createDimension('time', timesec.size)
                   ds.createDimension('range', ragsec.size)
                   ds.createDimension('num_ml', nml)
                   
                   # add variables
                   ################# input variables to the model #################
                   Timesec = ds.createVariable('time', 'i8', ('time',))
                   Timeabssec = ds.createVariable('timeabs', 'i8', ('time',))
                   Ragsec = ds.createVariable('range', 'f8', ('range',))
                   ZEsec = ds.createVariable('Ze', 'f8', ('range','time'))
                   VDsec = ds.createVariable('Vd', 'f8', ('range','time'))
                   DVDsec = ds.createVariable('dVd', 'f8', ('range','time'))
                   MASKNoisec = ds.createVariable('Mask_Noise', 'f8', ('range','time'))
                   ################# output variables of the model ################
                   MLup = ds.createVariable('MeltLayer_up', 'f8', ('time','num_ml'))
                   MLlow = ds.createVariable('MeltLayer_low', 'f8', ('time','num_ml'))
                   MASKML = ds.createVariable('Mask_MeltLayer', 'f8', ('range','time'))
                   
                   # add units
                   Timesec.units = 'seconds since midnight, i.e. YYYY-MM-DD 00:00:00'
                   Timeabssec.units = 'seconds since 1970-01-01 00:00:00'
                   Ragsec.units = 'km, range height of KAZR (4th to 265th bin)'
                   ZEsec.units = 'dBZ, Radar reflectivity'
                   VDsec.units = 'm s^-1, Mean doppler velocity (positive means motion towards the radar)'
                   DVDsec.units = 's^-1, gradient of mean doppler velocity'
                   MASKNoisec.units = 'logical, background noise mask: signal-to-noise ratio < -15'
                   MLup.units = 'km, upper level height of the melting layers'
                   MLlow.units = 'km, lower level height of the melting layers'
                   MASKML.units = 'logical, melting layer mask: melting layer detected'
                   
                   # assign values
                   Timesec[:] = timesec.copy()
                   Timeabssec[:] = timeabssec.copy()
                   Ragsec[:] = ragsec.copy()
                   ZEsec[:,:] = Zesec.copy()
                   VDsec[:,:] = Vdsec.copy()
                   DVDsec[:,:] = dVdsec.copy()
                   MASKNoisec[:,:] = MaskNoisec.copy()
                   MLup[:] = Yup.copy()
                   MLlow[:] = Ylow.copy()
                   MASKML[:,:] = MASK_ml.copy()                              
                                  
                   # close the file
                   ds.close()
                                                                                                                                                                             

            else:
                MASK_ml = np.zeros(dVdsec.shape)
                if query_yes_no("No melting layer, continue to save the data?"):
                    fnameout_noML = 'OutputMLn_' + '{:4d}'.format(year) + '{:02d}'.format(mon)\
                               + '{:02d}'.format(day) + '_' + '{:02d}'.format(isec)\
                               + '-' + '{:02d}'.format(isec+6) + 'hr' + '.nc'
                    
                    dn = nc.Dataset(fpathout + fnameout_noML, 'w', format = 'NETCDF4')
                    
                    # add dimensions
                    dn.createDimension('time', timesec.size)
                    dn.createDimension('range', ragsec.size)
                    
                    # add variables
                    ################# input variables to the model #################
                    Timesec = dn.createVariable('time', 'i8', ('time',))
                    Timeabssec = dn.createVariable('timeabs', 'i8', ('time',))
                    Ragsec = dn.createVariable('range', 'f8', ('range',))
                    ZEsec = dn.createVariable('Ze', 'f8', ('range','time'))
                    VDsec = dn.createVariable('Vd', 'f8', ('range','time'))
                    DVDsec = dn.createVariable('dVd', 'f8', ('range','time'))
                    MASKNoisec = dn.createVariable('Mask_Noise', 'f8', ('range','time'))
                    ################# output variables of the model ################
                    MLup = dn.createVariable('MeltLayer_up', 'f8', ('time',))
                    MLlow = dn.createVariable('MeltLayer_low', 'f8', ('time',))
                    MASKML = dn.createVariable('Mask_MeltLayer', 'f8', ('range','time'))
                    
                    # add units
                    Timesec.units = 'seconds since midnight, i.e. YYYY-MM-DD 00:00:00'
                    Timeabssec.units = 'seconds since 1970-01-01 00:00:00'
                    Ragsec.units = 'km, range height of KAZR (4th to 265th bin)'
                    ZEsec.units = 'dBZ, Radar reflectivity'
                    VDsec.units = 'm s^-1, Mean doppler velocity (positive means motion towards the radar)'
                    DVDsec.units = 's^-1, gradient of mean doppler velocity'
                    MASKNoisec.units = 'logical, background noise mask: signal-to-noise ratio < -15'
                    MLup.units = 'km, upper level height of the melting layer'
                    MLlow.units = 'km, lower level height of the melting layer'
                    MASKML.units = 'logical, melting layer mask: melting layer detected'
                    
                    # assign values
                    Timesec[:] = timesec.copy()
                    Timeabssec[:] = timeabssec.copy()
                    Ragsec[:] = ragsec.copy()
                    ZEsec[:,:] = Zesec.copy()
                    VDsec[:,:] = Vdsec.copy()
                    DVDsec[:,:] = dVdsec.copy()
                    MASKNoisec[:,:] = MaskNoisec.copy()
                    MLup[:] = np.zeros(timesec.shape)
                    MLlow[:] = np.zeros(timesec.shape)
                    MASKML[:,:] = MASK_ml.copy()                              
                                   
                    # close the file
                    dn.close()
             