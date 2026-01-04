 #Función de inicio de Sistema
import sys
 
# Librerias PYQT
#import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QColor
from PyQt5 import QtCore
from PyQt5.QtCore import QSortFilterProxyModel, Qt

#LIBRERIAS
from pyfirmata2 import Arduino, util

#Librerias pandas
import pandas as pd
from PandasModel import PandasModel

#Librerias extra
from collections import deque
import pyqtgraph
#import time
from datetime import datetime

#Configurar vectores
Y0=deque([0], maxlen=100)
Y1=deque([0], maxlen=100)

#Fecha
fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#Configurar fondo grafica pyqtgraph
pyqtgraph.setConfigOption('background', 'w')
pyqtgraph.setConfigOption('foreground', 'k')

#Dar de alta arduino
ard = Arduino('/dev/ttyACM0', baudrate=57600)
it = util.Iterator(ard) #Dar de alta un iterador
it.start()
#Habilitar puerto analogico
ard.analog[0].enable_reporting()
ard.analog[1].enable_reporting()

#Dar de alta pines
D3=ard.get_pin('d:3:p')
D4=ard.get_pin('d:4:i')
D5=ard.get_pin('d:5:p')
D6=ard.get_pin('d:6:p')
D9=ard.get_pin('d:9:p')
D13=ard.get_pin('d:13:o')
D2=ard.get_pin('d:2:o')
A0 = ard.get_pin('a:0:i')
A1 = ard.get_pin('a:1:i')
 
# Importar ventana de interfaz
import mainwindow_auto

#Ponerle color a las letras 
class ColorTextProxyModel(QSortFilterProxyModel):
    def data(self, index, role=Qt.DisplayRole):
        value = super().data(index, role)
        
        # Colorear solo las primeras tres filas
        if role == Qt.ForegroundRole:
            if index.row() == 0:
                return QColor("red")
            elif index.row() == 1:
                return QColor("green")
            elif index.row() == 2:
                return QColor("blue")
        
        return value
    
# Creación de la ventana principal
class MainWindow(QMainWindow, mainwindow_auto.Ui_Dialog):
    
    
        
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.SLR.setStyleSheet("""
            QSlider::handle:horizontal {
                background: red;
            }
            QSlider::handle:horizontal:disabled {
                background: lightgray;
            }
            QSlider::handle:horizontal:pressed {
                background: lightgray;
            }
            """)
        self.SLG.setStyleSheet("""
            QSlider::handle:horizontal {
                background: green;
            }
            QSlider::handle:horizontal:pressed {
                background: lightgray;
            }
            QSlider::handle:horizontal:disabled {
                background: lightgray;
            }
            """)
        #Imagenes estaticas
        ITO=QPixmap('ito.png') # QPixmap transforna imagen en tipo QT
        MIE=QPixmap('MIE.png')
        self.LITO.setScaledContents(1) # setScaledContents escala imagenes
        self.LMIE.setScaledContents(1)
        self.LITO.setPixmap(ITO) # setPixmap coloca una imagen en una label
        self.LMIE.setPixmap(MIE)
        #Imagenes dinamicas
        self.OFF=QPixmap('off.png')
        self.ON=QPixmap('on.png')
        self.BLU=QPixmap('blue.jpg')
        self.BGR=QPixmap('RGB.jpg')
        self.LLD.setScaledContents(1)
        self.LLT.setScaledContents(1)
        self.LRGB.setScaledContents(1)
        #PushButton
        self.PBE.setText('Encender') # .setText coloca texto en Widget
        self.PBA.setText('Apagado')
        self.LLD.setPixmap(self.OFF)
        #PushButton Toogle
        self.PBT.setCheckable(True) #Configurar boton como toogle
        self.PBT.setText('Encender')
        self.LLT.setPixmap(self.OFF)
        #Configurar Spinbox
        self.SB1.setRange(-1000,1000) #.setRange define rangos del Spinbox
        self.SB2.setRange(-1000,1000)
        self.SB2.setDecimals(3)
        self.LSB.setText('0')
        self.SB1.setKeyboardTracking(False)
        self.SB2.setKeyboardTracking(False)
        #Configurar Tabla
        self.TB1.setRowCount(5) #Configura numero de filas
        self.TB1.setColumnCount(2) #Configura numero de columnas
        self.TB1.setHorizontalHeaderLabels(['Result','Unit'])
        self.TB1.setVerticalHeaderLabels(['SUM','RES','MUL','DIV','POW2'])
        self.TB1.setItem(0,1, QTableWidgetItem('Volt')) #Colocar items en tabla
        self.TB1.setItem(1,1, QTableWidgetItem('Amper'))
        self.TB1.setItem(2,1, QTableWidgetItem('Watt'))
        self.TB1.setItem(3,1, QTableWidgetItem('Farad'))
        self.TB1.setItem(4,1, QTableWidgetItem('Ohm'))
        #Tabla Pandas Exportar
        self.data=pd.DataFrame()
        #Configurar Grafica
        self.GR1.setYRange(0,6)
        self.GR1.setXRange(0,100)
        self.GR1.showGrid(x= True, y= True, alpha= 0.5) # alpha contraste grid
        self.GR1.setLabel('bottom', 'Tiempo (100ms)')
        self.GR1.setLabel('left', 'Voltaje (V)')
        self.GR1.setTitle('Sensores de Voltaje')
        #Configurar ComboBox
        self.CMB.addItem('RGB') # Agregar opcion a ComboBox
        self.CMB.addItem('Red')
        self.CMB.addItem('Green')
        self.CMB.addItem('Blue')
        #Funciones
        self.SPWM.valueChanged.connect(self.PWM)
        self.PBE.clicked.connect(self.ENC)
        self.PBA.clicked.connect(self.APG)
        self.PBT.clicked.connect(self.TLG)
        self.SB1.valueChanged.connect(self.ARI)
        self.SB2.valueChanged.connect(self.ARI)
        self.BPD.clicked.connect(self.PAN)
        self.BPE.clicked.connect(self.PEX)
        self.CMB.activated[str].connect(self.RGB)
        self.SLR.valueChanged.connect(self.RGB)
        self.SLG.valueChanged.connect(self.RGB)
        self.SLB.valueChanged.connect(self.RGB)
        self.CHB.stateChanged.connect(self.RGB)
        self.RGB()
        #self.GRF()
        #self.GRFA()
        #self.LED() #Lectura digital
        self.sen = pd.DataFrame(columns=['', 'A0', 'A1', 'Unidad'])


    def PWM(self):
        #Instruccion .value() permite conocer valor del Slider
        S= self.SPWM.value()
        D3.write(S/100)

    def ENC(self):
        self.LLD.setPixmap(self.ON)
        D13.write(1)

    def APG(self):
        self.LLD.setPixmap(self.OFF)
        D13.write(0)

    def TLG(self):
        if self.PBT.isChecked()==True: #.isChecked verifica el estado Boton Toogle
            self.LLT.setPixmap(self.ON)
            self.PBT.setText('Apagar')
            D2.write(1)
        else:
            self.LLT.setPixmap(self.OFF)
            self.PBT.setText('Encender')
            D2.write(0)

    def ARI(self):
        V1=self.SB1.value() #.value() lee valor del spinbox
        V2=self.SB2.value()
        S=V1+V2
        R=V1-V2
        M=V1*V2
        D=V1/V2 if V2 != 0 else 0
        P=V1**2
        self.LSB.setText(str(S))
        self.TSB.setText(str(S))
        self.TB1.setItem(0,0, QTableWidgetItem(str(S)))
        self.TB1.setItem(1,0, QTableWidgetItem(str(R)))
        self.TB1.setItem(2,0, QTableWidgetItem(str(M)))
        self.TB1.setItem(3,0, QTableWidgetItem(str(D)))
        self.TB1.setItem(4,0, QTableWidgetItem(str(P)))
        #Tabla Pandas
        self.data= pd.DataFrame({
            'Resultado': [S,R,M,D,P]
            }, index=['Suma', 'Res', 'Mul', 'Div', 'Pot'])#index Header Vertical
        model=PandasModel(self.data)
        self.TPE.setModel(model)

    def PAN(self):
        df=pd.read_csv('tabla1.csv')
        model=PandasModel(df) #Transforma tabla de pandas en Tabla QT
        proxy = ColorTextProxyModel()
        proxy.setSourceModel(model)  
        self.TPD.setModel(proxy) #Coloca la tabla tipo QT

    def PEX(self):
        if self.data.empty==False:
            self.data.to_csv('tablaE.csv', mode='a', header=False, index=True)

    def GRF(self):
        try:
            v0 = A0.value
            v1 = A1.value
            if v0 is None:
                v0 = 0
            if v1 is None:
                v1 = 0
        except OSError:
            # pyfirmata2 lanza OSError si se hace polling
            v0 = 0
            v1 = 0

        S0 = v0 * 5
        S1 = v1 * 5

        Y0.append(S0)
        Y1.append(S1)

        self.sen = pd.DataFrame({
            'A0':[S0],
            'A1':[S1],
            'Unidad':['V']
        })
        self.sen.insert(0, '', [fecha_actual])

        mds = PandasModel(self.sen)
        self.TBS.setModel(mds)

        self.GR1.plot(Y0, pen='b', clear=True)
        self.GR1.plot(Y1, pen='r')  # Lectura segura del pin A0)
        

    def GRFA(self):
        self.sen.to_csv('sensores.csv', mode='a', header= False, index=False)

    def RGB(self):
        R=self.SLR.value()/100
        G=self.SLG.value()/100
        B=self.SLB.value()/100
        if self.CHB.isChecked():
            self.CMB.setEnabled(True)
            self.SLR.setEnabled(True)
            self.SLG.setEnabled(True)
            self.SLB.setEnabled(True)
            if self.CMB.currentText()=='RGB':
                self.LRGB.setPixmap(self.BGR)
                #D4.write(1-R)
                D5.write(1-R)
                D6.write(1-G)
                D9.write(1-B)
            if self.CMB.currentText()=='Red':
                self.LRGB.setPixmap(self.OFF)
                #D4.write(1-R)
                D5.write(1-R)
                D6.write(1)
                D9.write(1)
            if self.CMB.currentText()=='Green':
                self.LRGB.setPixmap(self.ON)
                #D4.write(1)
                D5.write(1)
                D6.write(1-G)
                D9.write(1)
            if self.CMB.currentText()=='Blue':
                self.LRGB.setPixmap(self.BLU)
                #D4.write(1)
                D5.write(1)
                D6.write(1)
                D9.write(1-B)
        else:
            self.CMB.setEnabled(False)
            self.SLR.setEnabled(False)
            self.SLG.setEnabled(False)
            self.SLB.setEnabled(False)
            #D4.write(1)
            D5.write(1)
            D6.write(1)
            D9.write(1)
    def LED(self):
        try:
            # Intentamos leer el pin D4; si devuelve None, consideramos apagado
            estado = D4.read()
            if estado is None:
                estado = 0
        except OSError:
            # Si pyfirmata2 lanza OSError, lo capturamos y asumimos apagado
            estado = 0

        if estado:
            self.LDL.setText('Encendido')
            self.LDL.setStyleSheet("color: green; font-weight: bold; font-size: 18px;")
            self.IDL.setPixmap(self.ON)
        else:
            self.LDL.setText('Apagado')
            self.LDL.setStyleSheet("color: red; font-weight: bold; font-size: 18px;")
            self.IDL.setPixmap(self.OFF)


def main():
#Generación de la aplicación
 app = QApplication(sys.argv)
 form = MainWindow()
 form.show()
 #form.GRF()
 #form.GRFA()
 #form.LED()
 #Temporizador
 timer = QtCore.QTimer()
 timer.timeout.connect(form.GRF)
 timer.timeout.connect(form.LED)
 timer.start(100) #timer se ejecuta en milisegundos
 timer2 = QtCore.QTimer()
 timer2.timeout.connect(form.GRFA)
 timer2.start(2000) #timer se ejecuta en milisegundos
 # Comando de ejecución continua del programa.
 sys.exit(app.exec_())
 
# Conidicón de inicio del programa
if __name__ == "__main__":
 main()
