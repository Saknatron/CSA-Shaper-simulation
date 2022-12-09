from multiprocessing.connection import wait
from PyLTSpice.LTSpiceBatch import SimCommander
from PyLTSpice.LTSpice_RawRead import RawRead
from PyLTSpice.LTSteps import LTSpiceLogReader
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
import time
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
import subprocess as sp
import os
import numpy as np
from tkinter.filedialog import askopenfilename
# ---------------------------------------------------------< RUN LTSpice >----|

LTC = SimCommander("C:/Users/USER/OneDrive - KMITL/KMITL-3C/3-Summer/PyLTSpice/noise/RAD-AMP.asc")
def start_param():
    LTC.set_parameters(Vps=189.33e-3, Ctest=1.7e-12, Cdet=0, Cpcb=17e-12)
    LTC.set_parameters(avol=3e3, gbw=1600e6, slew=700e6, il=0, vos=0.25e-3, phi=45, en=4.8e-9, iin=1.3e-15, rin=1e12, ro=0.02, ccm=0.7e-12, cdiff=4.5e-12, vsp=5)
    LTC.set_parameters(cf=0.5e-12, rf=100e6, cpz=500e-12, rpz=100e3, chp=100e-9, rhp=1e6, clp=10e-12, rlp=1e6, cc=0.1e-6, cpcb=17e-12)
start_param()
print("---------------------------------------< HI >------------|")
print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
print("::: 1,Varry :: 2,Constance :: 3,ENC(csa) :: 4,Program ::::")
print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
print("Choose 1 or 2 or 3 or 4 ? \n  >>  ",end='')
nnmode = int(input())
if(nnmode!=4):
    if(nnmode==3):
        Cdet_list = [1.12E-11, 1.30E-11, 1.45E-11, 1.51E-11, 1.59E-11, 2.24E-11, 2.50E-11, 3.50E-11, 4.88E-11, 5.76E-11, 6.71E-11, 9.81E-11, 1.25E-10, 2.01E-10]
        Rleak_list = [1.55E+08, 1.67E+08, 1.74E+08, 1.76E+08, 1.78E+08, 2.10E+08, 2.41E+08, 3.67E+08, 5.49E+08, 6.67E+08, 7.97E+08, 1.21E+09, 1.49E+09, 1.41E+10]
        command_Cdet,command_Rleak = "table(X" ,"table(X"
        for i in range(0,len(Cdet_list)):
            command_Cdet += ", %d, %s"%(i+1, str(Cdet_list[i]))
            command_Rleak += ", %d, %s"%(i+1, str(Rleak_list[i]))
        command_Cdet += ')'
        command_Rleak += ')'
        LTC.add_instruction(".step param X 1 %d 1"%(len(Cdet_list)))
        LTC.set_parameter('Cdet', command_Cdet)
        LTC.set_parameter('Rleak', command_Rleak)
        
        #LTC.add_instruction(".step dec param GBW %s %s 10"%(Rn1,Rn2))
        #LTC.add_instruction(".step dec param Avol %s %s 10"%(Cn1,Cn2))
        print("---------------------------------------< Wait.. >-----------|")
    if(nnmode==1 or nnmode==2):
        print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print(":::  Voltage : Vcc, Vpulse")
        print(":::  Op-amp spec. : Avol, GBW, Slew, Ilimit, Rail, Vos, Phimargin, En, Inn, Rin")
        print(":::  Resistor : Rs1, Rs2, Rleak, Rfcsa, Rcsa2amp, Rinamp, Rfamp")
        print(":::  Capacitor : Cdet, Cd2csa, Cbfcsa2gnd, Cfcsa, Ccsa2amp, Css")
        print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
        print("^^^^^^^^ Type parameter ^^^^^^^^^^^^^^^")
        print("You choose :   ",end='')
        nnvarry = input()
        print("1st value :   ",end='')
        nn1 = input()
        if(nnmode==1):
            print("2nd value :   ",end='')
            nn2 = input()
            print("Sampling in dec. :   ",end='')
            Sampling = input()
            LTC.add_instruction(".step dec param %s %s %s %s"%(nnvarry, nn1, nn2, Sampling))
        else:
            LTC.set_parameter(nnvarry,nn1)


    LTC.set_element_model('Vpulse', "PULSE(0 {Vpulse} 0.2e-3 20e-9 20e-9 1e-3 1)")
    LTC.add_instruction(".noise V(OUT) Idet dec 50 1 10Meg")
    LTC.add_instruction(".meas NOISE vonoise INTEG V(onoise)")
    LTC.run()
    LTC.remove_instruction(".noise V(OUT) Idet dec 50 1 10Meg")
    LTC.add_instruction(".tran 0 1m 0 1u")
    LTC.run()
    LTC.wait_completion()
    print("Total Simulations: {}".format(LTC.runno))
    print("Successful Simulations: {}".format(LTC.okSim))
    print("Failed Simulations: {}".format(LTC.failSim))
    # ---------------------------------------------------------< READ DATA >----|
    LTR1 = RawRead("noise/RAD-AMP_1.raw")
    LTR2 = RawRead("noise/RAD-AMP_2.raw")

    LGF = LTSpiceLogReader("noise/RAD-AMP_1.log")

    noise = LTR1.get_trace('V(onoise)')
    vcsa = LTR2.get_trace('V(csa)')
    vout = LTR2.get_trace('V(out)')
    value_noise = noise.get_wave(0)
    rms_value_noise = sum(value_noise**2)
    value_csa = vcsa.get_wave(0)
    min_value_csa = min(value_csa)
    value_out = vout.get_wave(0)
    max_value_out = max(value_out)

    steps = LTR1.get_steps()

    print("-----------------------------------------< VALUE >-------------|")
    save_enc = []
    for j in steps:
        print("Step : %d / %d"%(j+1,1+max(steps)))
        rms_value_noise = LGF.get_measure_values_at_steps('vonoise',j)
        min_value_csa = min(vcsa.get_wave(j))
        max_value_out = max(vout.get_wave(j))
        ENC_value_fe = 1.91e5*rms_value_noise/max_value_out
        print("RMS(NOISE) : %f Vrms"%(rms_value_noise))
        print("MIN(CSA) : %f mV"%(min_value_csa*1000))
        print("MAX(OUT) : %f mV"%(max_value_out*1000))
        print("ENC : %f e-rms."%(ENC_value_fe))
        print("::::::::::::::::::::::::")
        save_enc.append(ENC_value_fe)
    print("---------------------------------------------------------------|")


    # -------------------------------------------------------< Plot Graph >---|
    print("You want give a noise Vout graph ? [y/n] >>  ",end='')
    show_noise_graph = input()
    print("You want give a Vcsa graph ? [y/n] >>  ",end='')
    show_csa_graph = input()
    print("You want give a Vout graph ? [y/n] >>  ",end='')
    show_out_graph = input()
    if(show_noise_graph.lower() == 'y'):
        #fig, (ax1, ax2, ax3) = plt.subplots(3)
        fig, ax1 = plt.subplots()
        for i in steps:
            ax1.plot(LTR1.get_axis(i),noise.get_wave(i))
        ax1.set(xlabel='Frequancy (Hz)', ylabel='Voltage Noise Density (V/sqrt(Hz))', title='V(ONOISE)')
        ax1.grid()
        ax1.set_xscale('log')
        ax1.legend(['First step'])
        plt.show()
        #fig.savefig("noise/graph_noise_cv.png", dpi=1000)
    else:
        print("Skip noise graph")
    if(show_csa_graph.lower() == 'y'):
        fig, ax2 = plt.subplots()
        for i in steps:
            ax2.plot(LTR2.get_axis(i),vcsa.get_wave(i))
        ax2.set(xlabel='time (s)', ylabel='Voltage (V)', title='V(CSA)')
        ax2.grid()
        ax2.legend(['First step'])
        plt.show()
    else:
        print("Skip csa graph")
    if(show_out_graph.lower() == 'y'):
        fig, ax3 = plt.subplots()
        for i in steps:
            ax3.plot(LTR2.get_axis(i),vout.get_wave(i))
        ax3.set(xlabel='time (s)', ylabel='Voltage (V)', title='V(OUT)')
        ax3.grid()
        ax3.legend(['First step'])
        plt.show()
    else:
        print("Skip out graph")
        #fig.savefig("noise/graph_out.png", dpi=1000)
        #plt.imshow(mpimg.imread('noise/circuit.png'))
        #plt.show()

    if(nnmode==3):
        xvalue = []
        for i in Cdet_list:
            xvalue.append(i*1e12)
        fig, ay1 = plt.subplots()
        ay1.plot(xvalue,save_enc,'m-*')
        ay1.set(xlabel='Cdet (pF)', ylabel='ENC (eRMS)', title='ENC')
        ay1.grid(color='k', linestyle='--', linewidth=0.5, which='both')
        print("Min ENC : %f"%min(save_enc))
        print("Min in step : %d"%save_enc.index(min(save_enc)))
        plt.show()
        #fig.savefig("noise/graph_enc_Cv.png", dpi=1000)
    print("Finish!")
else:
    class MatplotlibWidget(QMainWindow):
        def __init__(self):
            QMainWindow.__init__(self)
            loadUi("interface.ui",self)
            self.setWindowTitle("TMEC - Simulation a circuit")
            self.setWindowIcon(QIcon("noise/icon.png"))
            self.MplWidget.canvas.axes.set_position([0.063, 0.067, 0.923, 0.893])
            self.MplWidget.canvas.axes.clear()
            self.textBrowser.clear()
            self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))
            #self.MplWidget.canvas.axes.plot(LTR1.get_axis(),noise.get_wave())
            #self.MplWidget.canvas.axes.set_xscale('log')
            #self.MplWidget.canvas.draw()
            self.download
            self.bt_ccf.clicked.connect(self.circuitfile)
            self.bt_ckf.clicked.connect(self.checkfile)
            self.setbt.clicked.connect(self.set_param)
            self.circuit.clicked.connect(self.show_cir)
            #--------------------------------------------------------<FIXED>--
            self.RunBT_list.clicked.connect(self.listFixed)
            self.comboBox_runlist.currentTextChanged.connect(self.plot_list)
            self.LogBT_list.clicked.connect(self.show_log)
            self.circuit_list.clicked.connect(self.show_cir)
            #--------------------------------------------------------<SWEEB>--
            self.RunBT_sw.clicked.connect(self.sweeb_element)
            self.comboBox_runsw.currentTextChanged.connect(self.plot_sw)
            self.LogBT_sw.clicked.connect(self.show_log)
            self.circuit_sw.clicked.connect(self.show_cir)
            #--------------------------------------------------------<ENC>----
            self.comboBox_enc1.currentTextChanged.connect(self.enc_elm1)
            self.comboBox_enc2.currentTextChanged.connect(self.enc_elm2)
            self.up_1.clicked.connect(self.enc_up1)
            self.up_2.clicked.connect(self.enc_up2)
            self.clear_1.clicked.connect(self.enc_clc1)
            self.clear_2.clicked.connect(self.enc_clc2)
            self.RunBT_enc.clicked.connect(self.enc_cal)
            self.LogBT_enc.clicked.connect(self.show_log)
            self.show

        def checkfile(self):
            self.textBrowser.append(self.namefile.text())

        def circuitfile(self):
            filename = askopenfilename()
            self.namefile.setText(filename)
            self.textBrowser.append("Choosed file")



        def set_param(self):
            
            LTC.set_parameters(Vps=self.pulsen.text(), Ctest=self.ctestn.text(), Cdet=self.cdetn.text(), Cpcb=self.cpcbn.text())
            LTC.set_parameters(cf=self.cfn.text(), rf=self.rfn.text(), cpz=self.cpzn.text(), rpz=self.rpzn.text(), chp=self.chpn.text(), rhp=self.rhpn.text(), clp=self.clpn.text(), rlp=self.rlpn.text())
            opampname = self.comboBox_listop.currentText()
            if(opampname == "TL082I"):
                LTC.set_parameters(avol=200e3, gbw=4e6, slew=16e6, il=0, vos=3e-3, phi=45, en=15e-9, iin=10e-15, rin=1e12, ro=300, Ccm=1e-12, Cdiff=2e-12, vsp=9)
            elif(opampname == "OPA657"):
                LTC.set_parameters(avol=3e3, gbw=1600e6, slew=700e6, il=0, vos=0.25e-3, phi=45, en=4.8e-9, iin=1.3e-15, rin=1e12, ro=0.02, Ccm=0.7e-12, Cdiff=4.5e-12, vsp=5)
            elif(opampname == "OPA859"):
                LTC.set_parameters(avol=1.7e3, gbw=900e6, slew=1150e6, il=15e-3, vos=0.9e-3, phi=45, en=3.3e-9, iin=3e-15, rin=1e12, ro=0.15, Ccm=0.62e-12, Cdiff=0.2e-12, vsp=2.5)
            elif(opampname == "OPA818"):
                LTC.set_parameters(avol=40e3, gbw=2700e6, slew=1400e6, il=50e-3, vos=0.35e-3, phi=45, en=2.2e-9, iin=2.5e-15, rin=500e9, ro=0.2, Ccm=1.9e-12, Cdiff=0.5e-12, vsp=5)
            elif(opampname == "ADA4817"):
                LTC.set_parameters(avol=1.7e3, gbw=1050e6, slew=870e6, il=0, vos=0.4e-3, phi=45, en=4e-9, iin=2.5e-15, rin=500e9, ro=0.15, Ccm=0.3e-12, Cdiff=0.1e-12, vsp=5)
            elif(opampname == "ADA4637"):
                LTC.set_parameters(avol=1000e3, gbw=19e6, slew=170e6, il=0, vos=0.4e-3, phi=45, en=4e-9, iin=2.5e-15, rin=10e12, ro=41, Ccm=7e-12, Cdiff=9e-12, vsp=9)
            self.textBrowser.append("Set up : Finish!")

        def download(self):
            self.completed = 0
            while self.completed < 100:
                self.completed += 1
                self.progressBar.setValue(self.completed)

        def listFixed(self):
            listelm = self.comboBox_listelm.currentText()
            v1,v2,v3,v4,v5,v6 = "","","","","","",
            v1 = self.v1.text()
            v2 = self.v2.text()
            v3 = self.v3.text()
            v4 = self.v4.text()
            v5 = self.v5.text()
            v6 = self.v6.text()
            if(v1 != "" and v2 != "" and v1 != v2):
                self.progressBar_list.setValue(0)
                self.set_param()
                LTC.add_instruction(".step param %s list %s %s %s %s %s %s"%(listelm, v1, v2, v3, v4, v5, v6))
                LTC.set_element_model('Vpulse', "PULSE(0 {Vps} 0.2e-3 20e-9 20e-9 1e-3 1)")
                LTC.add_instruction(".noise V(OUT) Idet dec 50 1 10G")
                LTC.add_instruction(".meas NOISE vonoise INTEG V(onoise)")
                LTC.run()
                #time.sleep(0.25)
                self.progressBar_list.setValue(25)
                LTC.remove_instruction(".noise V(OUT) Idet dec 50 1 10G")
                LTC.remove_instruction(".meas NOISE vonoise INTEG V(onoise)")
                LTC.add_instruction(".tran 0 1m 0 1u")
                LTC.run()
                #time.sleep(0.25)
                self.progressBar_list.setValue(50)
                LTC.remove_instruction(".step param %s list %s %s %s %s %s %s"%(listelm, v1, v2, v3, v4, v5, v6))
                LTC.remove_instruction(".tran 0 1m 0 1u")
                LTC.wait_completion()
                self.comboBox_runlist.setCurrentText("Noise")
                #time.sleep(0.25)
                self.progressBar_list.setValue(75)
                self.textBrowser.append("Total Simulations: {}".format(LTC.runno))
                self.textBrowser.append("Successful Simulations: {}".format(LTC.okSim))
                self.textBrowser.append("Failed Simulations: {}".format(LTC.failSim))
                self.textBrowser.append("------------------------------")
                READ_DATA = RawRead("noise/RAD-AMP_{}.raw".format((LTC.runno)-1))
                steps = READ_DATA.get_steps()
                self.MplWidget.canvas.axes.clear()
                data = READ_DATA.get_trace('V(onoise)')
                self.MplWidget.canvas.axes.set_xscale('log')
                READ_DATA_2 = RawRead("noise/RAD-AMP_{}.raw".format(LTC.runno))
                vcsa = READ_DATA_2.get_trace('V(csa)')
                vout = READ_DATA_2.get_trace('V(out)')
                save_enc = []
                LGF = LTSpiceLogReader("noise/RAD-AMP_{}.log".format((LTC.runno)-1))
                for i in steps:
                    self.MplWidget.canvas.axes.plot(READ_DATA.get_axis(i),data.get_wave(i))
                    
                    self.textBrowser.append("Step : %d / %d"%(i+1,1+max(steps)))
                    rms_value_noise = LGF.get_measure_values_at_steps('vonoise',i)
                    min_value_csa = min(vcsa.get_wave(i))
                    max_value_out = max(vout.get_wave(i))
                    nnctest = self.ctestn.text().split('e')
                    ctest = float(float(nnctest[0])*(10**int(nnctest[1])))
                    nnvpulse = self.pulsen.text().split('e')
                    vpulse = float(float(nnvpulse[0])*(10**int(nnvpulse[1])))
                    ENC_value_fe = ctest*vpulse*rms_value_noise/max_value_out/1.6e-19/11
                    self.textBrowser.append("RMS(NOISE) : %f Vrms"%(rms_value_noise))
                    self.textBrowser.append("MIN(CSA) : %f mV"%(min_value_csa*1000))
                    self.textBrowser.append("MAX(OUT) : %f mV"%(max_value_out*1000))
                    self.textBrowser.append("ENC : %f e-rms."%(ENC_value_fe))
                    self.textBrowser.append("::::::::::::::::::::::::")
                    
                    save_enc.append(ENC_value_fe)
                self.MplWidget.canvas.axes.set(xlabel='Frequancy (Hz)', ylabel='Voltage Noise Density (V/sqrt(Hz))', title='V(ONOISE)')
                self.MplWidget.canvas.axes.grid()
                self.MplWidget.canvas.axes.legend(['1st step','2nd step','3rd step','4th step','5th step','6th step'])
                self.MplWidget.canvas.draw()
                self.comboBox_runlist.setEnabled(True)
                self.LogBT_list.setEnabled(True)
                self.comboBox_runsw.setEnabled(False)
                self.LogBT_sw.setEnabled(False)
                #time.sleep(0.25)
                self.progressBar_list.setValue(100)
            else:
                pass

        def sweeb_element(self):
            swelm_name = self.comboBox_swelm.currentText()
            stelm = self.StartV.text()
            laelm = self.LastV.text()
            swetype = self.swetype.currentText()
            numpoint = self.numpoint.text()
            if(stelm!="" and laelm!=""):
                self.progressBar_sw.setValue(0)
                self.set_param()
                LTC.add_instruction(".step %s param %s %s %s %s"%(swetype, swelm_name, stelm, laelm, numpoint))
                LTC.set_element_model('Vpulse', "PULSE(0 {Vps} 0.2e-3 20e-9 20e-9 1e-3 1)")
                LTC.add_instruction(".noise V(OUT) Idet dec 50 1 10G")
                LTC.add_instruction(".meas NOISE vonoise INTEG V(onoise)")
                LTC.run()
                self.progressBar_sw.setValue(25)
                LTC.remove_instruction(".noise V(OUT) Idet dec 50 1 10G")
                LTC.remove_instruction(".meas NOISE vonoise INTEG V(onoise)")
                LTC.add_instruction(".tran 0 1m 0 1u")
                LTC.run()
                self.progressBar_sw.setValue(50)
                LTC.remove_instruction(".step %s param %s %s %s %s"%(swetype, swelm_name, stelm, laelm, numpoint))
                LTC.remove_instruction(".tran 0 1m 0 1u")
                LTC.wait_completion()
                self.comboBox_runlist.setCurrentText("Noise")
                self.progressBar_sw.setValue(75)
                self.textBrowser.append("Total Simulations: {}".format(LTC.runno))
                self.textBrowser.append("Successful Simulations: {}".format(LTC.okSim))
                self.textBrowser.append("Failed Simulations: {}".format(LTC.failSim))
                self.textBrowser.append("------------------------------")
                READ_DATA = RawRead("noise/RAD-AMP_{}.raw".format((LTC.runno)-1))
                steps = READ_DATA.get_steps()
                self.MplWidget.canvas.axes.clear()
                data = READ_DATA.get_trace('V(onoise)')
                self.MplWidget.canvas.axes.set_xscale('log')
                READ_DATA_2 = RawRead("noise/RAD-AMP_{}.raw".format(LTC.runno))
                vcsa = READ_DATA_2.get_trace('V(csa)')
                vout = READ_DATA_2.get_trace('V(out)')
                save_enc = []
                LGF = LTSpiceLogReader("noise/RAD-AMP_{}.log".format((LTC.runno)-1))
                for i in steps:
                    self.MplWidget.canvas.axes.plot(READ_DATA.get_axis(i),data.get_wave(i))
                    
                    self.textBrowser.append("Step : %d / %d"%(i+1,1+max(steps)))
                    rms_value_noise = LGF.get_measure_values_at_steps('vonoise',i)
                    min_value_csa = min(vcsa.get_wave(i))
                    max_value_out = max(vout.get_wave(i))
                    nnctest = self.ctestn.text().split('e')
                    ctest = float(float(nnctest[0])*(10**int(nnctest[1])))
                    nnvpulse = self.pulsen.text().split('e')
                    vpulse = float(float(nnvpulse[0])*(10**int(nnvpulse[1])))
                    ENC_value_fe = ctest*vpulse*rms_value_noise/max_value_out/1.6e-19/11
                    self.textBrowser.append("RMS(NOISE) : %f Vrms"%(rms_value_noise))
                    self.textBrowser.append("MIN(CSA) : %f mV"%(min_value_csa*1000))
                    self.textBrowser.append("MAX(OUT) : %f mV"%(max_value_out*1000))
                    self.textBrowser.append("ENC : %f e-rms."%(ENC_value_fe))
                    self.textBrowser.append("::::::::::::::::::::::::")
                    
                    save_enc.append(ENC_value_fe)
                self.MplWidget.canvas.axes.set(xlabel='Frequancy (Hz)', ylabel='Voltage Noise Density (V/sqrt(Hz))', title='V(ONOISE)')
                self.MplWidget.canvas.axes.grid()
                self.MplWidget.canvas.axes.legend(['1st step','2nd step','3rd step','4th step','5th step','6th step'])
                self.MplWidget.canvas.draw()
                self.comboBox_runsw.setEnabled(True)
                self.LogBT_sw.setEnabled(True)
                self.comboBox_runlist.setEnabled(False)
                self.LogBT_list.setEnabled(False)
                self.progressBar_sw.setValue(100)
            else:
                pass
            
        
        def plot_(self, plot_name):
            READ_DATA_1 = RawRead("noise/RAD-AMP_{}.raw".format((LTC.runno)-1))
            READ_DATA_2 = RawRead("noise/RAD-AMP_{}.raw".format(LTC.runno))
            steps = READ_DATA_1.get_steps()
            self.MplWidget.canvas.axes.clear()
            self.progressBar_list.setValue(50)
            self.progressBar_sw.setValue(50)
            if(plot_name=="Noise"):
                data = READ_DATA_1.get_trace('V(onoise)')
                self.MplWidget.canvas.axes.set_xscale('log')
                READ_X = READ_DATA_1
                self.MplWidget.canvas.axes.set(xlabel='Frequancy (Hz)', ylabel='Voltage Noise Density (V/sqrt(Hz))', title='V(ONOISE)')
                self.MplWidget.canvas.axes.grid()
            elif(plot_name=="CSA"):
                data = READ_DATA_2.get_trace('V(csa)')
                self.MplWidget.canvas.axes.set_xscale('linear')
                READ_X = READ_DATA_2
                self.MplWidget.canvas.axes.set(xlabel='time (s)', ylabel='Voltage (V)', title='V(CSA)')
                self.MplWidget.canvas.axes.grid()
            elif(plot_name=="OUT"):
                data = READ_DATA_2.get_trace('V(out)')
                self.MplWidget.canvas.axes.set_xscale('linear')
                READ_X = READ_DATA_2
                self.MplWidget.canvas.axes.set(xlabel='time (s)', ylabel='Voltage (V)', title='V(OUT)')
                self.MplWidget.canvas.axes.grid()
            if(plot_name=="ENC"):
                self.textBrowser.append("Sorry, ENC not work")
                self.MplWidget.canvas.axes.clear()
                self.MplWidget.canvas.draw()
            else:
                for i in steps:
                    self.MplWidget.canvas.axes.plot(READ_X.get_axis(i),data.get_wave(i))
                    self.MplWidget.canvas.axes.legend(['1st step','2nd step','3rd step','4th step','5th step','6th step'])
                self.MplWidget.canvas.draw()
            self.progressBar_list.setValue(100)
            self.progressBar_sw.setValue(100)
        def plot_list(self):
            plot_name = self.comboBox_runlist.currentText()
            self.plot_(plot_name)
        def plot_sw(self):
            plot_name = self.comboBox_runsw.currentText()
            self.plot_(plot_name)
        def show_log(self):
            sp.Popen(["Notepad.exe","noise/RAD-AMP_{}.log".format(LTC.runno)])
        def show_cir(self):
            os.startfile("noise\circuit.png")
            #sp.Popen(["eog","noise/circuit.png"])

        def enc_elm1(self):
            self.Value1.setEnabled(True)
            self.clear_1.setEnabled(True)
            self.up_1.setEnabled(True)
        def enc_elm2(self):
            self.Value2.setEnabled(True)
            self.clear_2.setEnabled(True)
            self.up_2.setEnabled(True)
        def enc_up1(self):
            give_v1 = self.Value1.text()
            if(give_v1!=''):
                self.listWidget_1.insertItem(self.listWidget_1.count(),give_v1)
            self.Value1.clear()
            nn1 = self.listWidget_1.count()
            nn2 = self.listWidget_2.count()
            if(nn1>nn2):
                xx = nn1
                yy = nn2
            else:
                xx = nn2
                yy = nn1
            percent = int(100*yy/xx)
            if(percent==100 and nn1>1):
                self.RunBT_enc.setEnabled(True)
            else:
                self.RunBT_enc.setEnabled(False)
            self.progressBar.setValue(percent)
        def enc_up2(self):
            give_v2 = self.Value2.text()
            if(give_v2!=''):
                self.listWidget_2.insertItem(self.listWidget_2.count(),give_v2)
            self.Value2.clear()
            nn1 = self.listWidget_1.count()
            nn2 = self.listWidget_2.count()
            if(nn1>nn2):
                xx = nn1
                yy = nn2
            else:
                xx = nn2
                yy = nn1
            percent = int(100*yy/xx)
            if(percent==100 and nn1>1):
                self.RunBT_enc.setEnabled(True)
            else:
                self.RunBT_enc.setEnabled(False)
            self.progressBar.setValue(percent)
        def enc_clc1(self):
            self.listWidget_1.takeItem(self.listWidget_1.currentRow())
            self.Value1.clear()
            nn1 = self.listWidget_1.count()
            nn2 = self.listWidget_2.count()
            if(nn1>nn2):
                xx = nn1
                yy = nn2
            else:
                xx = nn2
                yy = nn1
            if(xx>0):
                percent = int(100*yy/xx)
            else:
                percent = 0
            if(percent==100 and nn1>1):
                self.RunBT_enc.setEnabled(True)
            else:
                self.RunBT_enc.setEnabled(False)
            self.progressBar.setValue(percent)
        def enc_clc2(self):
            self.listWidget_2.takeItem(self.listWidget_2.currentRow())
            self.Value2.clear()
            nn1 = self.listWidget_1.count()
            nn2 = self.listWidget_2.count()
            if(nn1>nn2):
                xx = nn1
                yy = nn2
            else:
                xx = nn2
                yy = nn1
            if(xx>0):
                percent = int(100*yy/xx)
            else:
                percent = 0
            if(percent==100 and nn1>1):
                self.RunBT_enc.setEnabled(True)
            else:
                self.RunBT_enc.setEnabled(False)
            self.progressBar.setValue(percent)
            
        def enc_cal(self):
            self.progressBar.setValue(0)
            nn = self.listWidget_1.count()
            name_v1 = self.comboBox_enc1.currentText()
            name_v2 = self.comboBox_enc2.currentText()
            v1_list, v2_list = "", ""
            v1_list, v2_list = "table(X", "table(X"
            save_v1, save_v2 = [], []
            for i in range(0,nn):
                self.listWidget_1.setCurrentRow(i)
                self.listWidget_2.setCurrentRow(i)
                save_v1.append((self.listWidget_1.currentItem().text()))
                save_v2.append((self.listWidget_2.currentItem().text()))
                v1_list += ", %d, %s"%(i+1, self.listWidget_1.currentItem().text())
                v2_list += ", %d, %s"%(i+1, self.listWidget_2.currentItem().text())
            v1_list += ')'
            v2_list += ')'
            self.set_param()
            LTC.add_instruction(".step param X 1 %d 1"%(nn))
            LTC.set_parameter(name_v1, v1_list)
            LTC.set_parameter(name_v2, v2_list)

            LTC.set_element_model('Vpulse', "PULSE(0 {Vps} 0.2e-3 20e-9 20e-9 1e-3 1)")
            LTC.add_instruction(".noise V(OUT) Idet dec 50 1 10G")
            LTC.add_instruction(".meas NOISE vonoise INTEG V(onoise)")
            LTC.run()
            self.progressBar.setValue(25)
            LTC.remove_instruction(".noise V(OUT) Idet dec 50 1 10G")
            LTC.remove_instruction(".meas NOISE vonoise INTEG V(onoise)")
            LTC.add_instruction(".tran 0 1m 0 1u")
            LTC.run()
            self.progressBar.setValue(50)
            LTC.remove_instruction(".tran 0 1m 0 1u")
            LTC.remove_instruction(".step param X 1 %d 1"%(nn))
            LTC.wait_completion()
            LTC.reset_netlist()
            self.textBrowser.append("Total Simulations: {}".format(LTC.runno))
            self.textBrowser.append("Successful Simulations: {}".format(LTC.okSim))
            self.textBrowser.append("Failed Simulations: {}".format(LTC.failSim))
            self.textBrowser.append("------------------------------")

            LTR1 = RawRead("noise/RAD-AMP_{}.raw".format((LTC.runno)-1))
            LTR2 = RawRead("noise/RAD-AMP_{}.raw".format((LTC.runno)))
            LGF = LTSpiceLogReader("noise/RAD-AMP_{}.log".format((LTC.runno)-1))
            vcsa = LTR2.get_trace('V(csa)')
            vout = LTR2.get_trace('V(out)')
            steps = LTR1.get_steps()
            save_enc = []
            for j in steps:
                self.textBrowser.append("Step : %d / %d"%(j+1,1+max(steps)))
                rms_value_noise = LGF.get_measure_values_at_steps('vonoise',j)
                min_value_csa = min(vcsa.get_wave(j))
                max_value_out = max(vout.get_wave(j))
                nnctest = self.ctestn.text().split('e')
                ctest = float(float(nnctest[0])*(10**int(nnctest[1])))
                nnvpulse = self.pulsen.text().split('e')
                vpulse = float(float(nnvpulse[0])*(10**int(nnvpulse[1])))
                ENC_value_fe = ctest*vpulse*rms_value_noise/max_value_out/1.6e-19/11
                self.textBrowser.append("RMS(NOISE) : %f Vrms"%(rms_value_noise))
                self.textBrowser.append("MIN(CSA) : %f mV"%(min_value_csa*1000))
                self.textBrowser.append("MAX(OUT) : %f mV"%(max_value_out*1000))
                self.textBrowser.append("ENC : %f"%(ENC_value_fe))
                self.textBrowser.append("::::::::::::::::::::::::")
                save_enc.append(ENC_value_fe)
            self.MplWidget.canvas.axes.clear()
            xvalue = []
            for i in save_v1:
                ii = i.split('e')
                xvalue.append(int(float(ii[0])*(10**int(ii[1]))))
            """
            print(xvalue)
            print(save_enc)
            """
            self.progressBar.setValue(75)
            self.MplWidget.canvas.axes.plot(xvalue,save_enc)
            self.MplWidget.canvas.axes.set(xlabel='%s (main), %s (sub)'%(name_v1, name_v2), ylabel='ENC (eRMS)', title='ENC')
            self.MplWidget.canvas.axes.grid()
            self.MplWidget.canvas.axes.set_xscale('log')
            self.textBrowser.append("Min ENC : %f"%min(save_enc))
            #self.textBrowser.append("Min in step : %d"%save_enc.index(min(save_enc))+1)
            self.MplWidget.canvas.draw()
            self.LogBT_enc.setEnabled(True)
            self.progressBar.setValue(100)
    if(nnmode==4):
        app = QApplication([])
        window = MatplotlibWidget()
        window.show()
        app.exec_()
"""
"""
