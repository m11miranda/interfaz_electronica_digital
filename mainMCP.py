
# INTERFAZ 3:
# DIGITAL EN RASPBERRY (GPIO)
# ANALÓGICO CON MCP3008 (CH0, CH1)


import sys
import math
import os
from datetime import datetime

# Librerias PYQT DE QT DESIGNER 
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore
from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtGui import QColor, QPalette, QBrush

# LIBRERIAS PANDAS
import pandas as pd
from PandasModel import PandasModel

# LIBRERIAS EXTRAS
from collections import deque
import pyqtgraph

# GPIO RASPBERRY PARA LA PARTE DIGITAL + MCP3008
from gpiozero import LED, PWMLED, Button, MCP3008  # >>> MCP3008 AÑADIDO

# CONFIGURAR VECTORES PARA GRÁFICA
Y0 = deque([0], maxlen=100)
Y1 = deque([0], maxlen=100)

# CONFIGURAR FONDO DE GRAFICA
pyqtgraph.setConfigOption('background', 'w')
pyqtgraph.setConfigOption('foreground', 'k')

# (SIN ARDUINO)

# from pyfirmata2 import Arduino, util
# ARD_PORT = '/dev/ttyUSB0'
# ard = Arduino(ARD_PORT, baudrate=57600)
# it = util.Iterator(ard)
# it.start()
# ard.analog[2].enable_reporting()
# ard.analog[3].enable_reporting()
# A2 = ard.get_pin('a:2:i')
# A3 = ard.get_pin('a:3:i')

#CANALES DEL MCP3008
#SPI0: CLK=11, MISO=9, MOSI=10, CE0=8
A2 = MCP3008(channel=0)   # primer pot en CH0
A3 = MCP3008(channel=1)   # segundo pot en CH1

# RASPBERRY (DIGITAL)

LED13   = LED(17)#LED 13 Arduino
LED_EXT = LED(27)#led externo D2
PWM_D3  = PWMLED(18) #D3 PWM digital
PWM_R   = PWMLED(19)#D5 RGB
PWM_G   = PWMLED(13)#D6 RGB
PWM_B   = PWMLED(12)#D9 RGB

BTN_IN  = Button(22, pull_up=False)#PUSH botón D4

#CONEXIONES
#SCLK(GPIO11) - CLK (13)
#MOSI(GPIO10)- DIn (11)
#MISO(GPIO9)- DOut (12)
#CE0(GPIO8) - CS/SHDN (10)
#PUENTES DE AGND Y DGND EN EL MCP
#PUENTE ENTRE VDD Y VREF

#IMPORTAR VENTANA PRINCIPAL DE INTERFAZ
import mainwindow_auto


class RowColorDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        row = index.row()

        if row == 0:
            option.palette.setBrush(QPalette.Text, QBrush(QColor("#d32f2f")))  # rojo
        elif row == 1:
            option.palette.setBrush(QPalette.Text, QBrush(QColor("#2e7d32")))  # verde
        elif row == 2:
            option.palette.setBrush(QPalette.Text, QBrush(QColor("#1565c0")))  # azul


class MainWindow(QMainWindow, mainwindow_auto.Ui_Dialog):

    def _style_slider_colored(self, slider, hex_color: str):
        slider.setStyleSheet(f"""
        QSlider::groove:horizontal {{ height: 6px; background: #e0e0e0; border-radius: 3px; }}
        QSlider::handle:horizontal {{ background: {hex_color}; width: 16px; height: 16px;
            margin: -5px 0; border-radius: 8px; border: 1px solid #777; }}
        QSlider::sub-page:horizontal {{ background: {hex_color}; border-radius: 3px; }}
        QSlider::add-page:horizontal {{ background: #e0e0e0; border-radius: 3px; }}
        """)

    def _style_slider(self, slider, hex_color: str):
        slider.setStyleSheet(f"""
        QSlider::groove:horizontal {{
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: {hex_color};
            width: 16px;
            height: 16px;
            margin: -5px 0;
            border-radius: 8px;
            border: 1px solid #777;
        }}
        QSlider::sub-page:horizontal {{
            background: {hex_color};
            border-radius: 3px;
        }}
        QSlider::add-page:horizontal {{
            background: #e0e0e0;
            border-radius: 3px;
        }}

        QSlider::groove:vertical {{
            width: 6px;
            background: #e0e0e0;
            border-radius: 3px;
        }}
        QSlider::handle:vertical {{
            background: {hex_color};
            width: 16px;
            height: 16px;
            margin: 0 -5px;
            border-radius: 8px;
            border: 1px solid #777;
        }}
        QSlider::sub-page:vertical {{
            background: {hex_color};
            border-radius: 3px;
        }}
        QSlider::add-page:vertical {{
            background: #e0e0e0;
            border-radius: 3px;
        }}
        """)

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        # IMÁGENES ESTÁTICAS
        ITO = QPixmap('ITO.png')
        MIE = QPixmap('MIE.png')
        self.LITO.setScaledContents(1)
        self.LMIE.setScaledContents(1)
        self.LITO.setPixmap(ITO)
        self.LMIE.setPixmap(MIE)

        # IMÁGENES DINÁMICAS
        self.OFF = QPixmap('off.png')
        self.ON  = QPixmap('on.png')
        self.BLU = QPixmap('blue.png')
        self.BGR = QPixmap('RGB.png')
        self.LLD.setScaledContents(1)
        self.LLT.setScaledContents(1)
        self.LRGB.setScaledContents(1)

        # PUSH BUTTONS
        self.PBE.setText('ENCENDER')
        self.PBA.setText('APAGAR')
        self.LLD.setPixmap(self.OFF)

        # BOTÓN TOGGLE
        self.PBT.setCheckable(True)
        self.PBT.setText('ENCENDER')
        self.LLT.setPixmap(self.OFF)

        # SPINBOXES
        self.SB1.setRange(-1000, 1000)
        self.SB2.setRange(-1000, 1000)
        self.SB2.setDecimals(3)
        self.LSB.setText('0')
        self.SB1.setKeyboardTracking(False)
        self.SB2.setKeyboardTracking(False)

        # TABLA ARITMÉTICA
        self.TB1.setRowCount(5)
        self.TB1.setColumnCount(2)
        self.TB1.setHorizontalHeaderLabels(['ANS', 'Unit'])
        self.TB1.setVerticalHeaderLabels(['SUM', 'RES', 'MUL', 'DIV', 'POW2'])
        self.TB1.setItem(0, 1, QTableWidgetItem('Volts'))
        self.TB1.setItem(1, 1, QTableWidgetItem('Ampers'))
        self.TB1.setItem(2, 1, QTableWidgetItem('Watt'))
        self.TB1.setItem(3, 1, QTableWidgetItem('Farads'))
        self.TB1.setItem(4, 1, QTableWidgetItem('Ohms'))

        # TABLA PANDAS EXPORTAR
        self.data = pd.DataFrame()

        # GRÁFICA
        self.GR1.setYRange(0, 6)
        self.GR1.setXRange(0, 100)
        self.GR1.showGrid(x=True, y=True, alpha=0.5)
        self.GR1.setLabel('bottom', 'Tiempo (100ms)')
        self.GR1.setLabel('left', 'Voltaje (V)')
        self.GR1.setTitle('Sensores de voltaje')

        # COMBOBOX RGB
        self.CMB.addItem('RGB')
        self.CMB.addItem('RED')
        self.CMB.addItem('GREEN')
        self.CMB.addItem('BLUE')

        # RGB INICIAL DESHABILITADO
        self.CMB.setEnabled(False)
        self.SLR.setEnabled(False)
        self.SLG.setEnabled(False)
        self.SLB.setEnabled(False)
        self.CHB.setChecked(False)

        # CONEXIÓN DE SEÑALES
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

        self.sen = pd.DataFrame()
        self.RGB()

    # ========================
    #   LÓGICA DIGITAL (GPIO)
    # ========================

    def PWM(self):
        S = self.SPWM.value()  # 0–100
        PWM_D3.value = S / 100.0

    def ENC(self):
        self.LLD.setPixmap(self.ON)
        LED13.on()

    def APG(self):
        self.LLD.setPixmap(self.OFF)
        LED13.off()

    def TLG(self):
        if self.PBT.isChecked():
            self.LLT.setPixmap(self.ON)
            self.PBT.setText('APAGAR')
            LED_EXT.on()
        else:
            self.LLT.setPixmap(self.OFF)
            self.PBT.setText('ENCENDER')
            LED_EXT.off()

    # ========================
    #   ARITMÉTICA SPINBOXES
    # ========================

    def ARI(self):
        V1 = self.SB1.value()
        V2 = self.SB2.value()
        S = V1 + V2
        R = V1 - V2
        M = V1 * V2
        D = V1 / V2 if V2 != 0 else "Math Error"
        PW2 = V1 ** 2

        self.LSB.setText(str(S))
        self.TSB.setText(str(S))

        self.TB1.setItem(0, 0, QTableWidgetItem(str(S)))
        self.TB1.setItem(1, 0, QTableWidgetItem(str(R)))
        self.TB1.setItem(2, 0, QTableWidgetItem(str(M)))
        self.TB1.setItem(3, 0, QTableWidgetItem(str(D)))
        self.TB1.setItem(4, 0, QTableWidgetItem(str(PW2)))

        self.data = pd.DataFrame(
            {'Resultado': [S, R, M, D, PW2]},
            index=['SUMA', 'RES', 'MUL', 'DIV', 'POT']
        )
        model = PandasModel(self.data)
        self.TPE.setModel(model)

    # ========================
    #   CSV DE PRUEBA
    # ========================

    def PAN(self):
        df = pd.read_csv('tabla1.csv')
        model = PandasModel(df)
        self.TPD.setModel(model)
        self.TPD.setItemDelegate(RowColorDelegate(self.TPD))

    def PEX(self):
        if not self.data.empty:
            self.data.to_csv('tablaE.csv', mode='a', header=True, index=True)

    # ========================
    #   LECTURA ANALÓGICA MCP3008 CH0/CH1
    # ========================

    def GRF(self):
        try:
            v2 = A2.value   # MCP3008 channel 0 (0–1)
            v3 = A3.value   # MCP3008 channel 1 (0–1)
            if v2 is None:
                v2 = 0
            if v3 is None:
                v3 = 0
        except OSError:
            v2 = 0
            v3 = 0

        # OJO: si alimentas el MCP3008 con 3.3 V, físicamente es 0–3.3 V
        # Aquí mantengo *5* para no cambiar tu interfaz; puedes poner 3.3 si quieres exactitud.
        S2 = v2 * 5
        S3 = v3 * 5

        Y0.append(S2)
        Y1.append(S3)

        self.GR1.plot(Y0, pen='b', clear=True)
        self.GR1.plot(Y1, pen='r')

        ts = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.sen = pd.DataFrame(
            {'A2': [S2], 'A3': [S3], 'Unidad': ['V']},
            index=[ts]
        )

        mds = PandasModel(self.sen)
        self.TBS.setModel(mds)

    def GRFA(self):
        if not self.sen.empty:
            self.sen.to_csv('Sensores.csv', mode='a', header=False, index=True)

    # ========================
    #   RGB CONTROLADO POR GPIO
    # ========================

    def RGB(self):
        R = self.SLR.value() / 100.0
        G = self.SLG.value() / 100.0
        B = self.SLB.value() / 100.0

        if self.CHB.isChecked():
            self.CMB.setEnabled(True)
            self.SLR.setEnabled(True)
            self.SLG.setEnabled(True)
            self.SLB.setEnabled(True)

            self._style_slider_colored(self.SLR, "#d32f2f")
            self._style_slider_colored(self.SLG, "#2e7d32")
            self._style_slider_colored(self.SLB, "#1565c0")

            if self.CMB.currentText() == 'RGB':
                self.LRGB.setPixmap(self.BGR)
                PWM_R.value = 1 - R
                PWM_G.value = 1 - G
                PWM_B.value = 1 - B
            elif self.CMB.currentText() == 'RED':
                self.LRGB.setPixmap(self.OFF)
                PWM_R.value = 1 - R
                PWM_G.value = 1
                PWM_B.value = 1
            elif self.CMB.currentText() == 'GREEN':
                self.LRGB.setPixmap(self.ON)
                PWM_R.value = 1
                PWM_G.value = 1 - G
                PWM_B.value = 1
            elif self.CMB.currentText() == 'BLUE':
                self.LRGB.setPixmap(self.BLU)
                PWM_R.value = 1
                PWM_G.value = 1
                PWM_B.value = 1 - B
        else:
            self.CMB.setEnabled(False)
            self.SLR.setEnabled(False)
            self.SLG.setEnabled(False)
            self.SLB.setEnabled(False)

            PWM_R.value = 1
            PWM_G.value = 1
            PWM_B.value = 1

            self.SLR.setStyleSheet("")
            self.SLG.setStyleSheet("")
            self.SLB.setStyleSheet("")
            self.LRGB.setPixmap(self.OFF)

    # ========================
    #   LECTURA BOTÓN DIGITAL
    # ========================

    def LED(self):
        try:
            estado = BTN_IN.is_pressed
        except OSError:
            estado = False

        if estado:
            self.LDL.setText('ENCENDIDO')
            self.LDL.setStyleSheet("color: #2e7d32; font-weight: 600;")
            self.IDL.setPixmap(self.ON)
        else:
            self.LDL.setText('APAGADO')
            self.LDL.setStyleSheet("color: #d32f2f; font-weight: 600;")
            self.IDL.setPixmap(self.OFF)


def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()

    timer = QtCore.QTimer()
    timer.timeout.connect(form.GRF)
    timer.timeout.connect(form.LED)
    timer.start(100)  # ms

    timer2 = QtCore.QTimer()
    timer2.timeout.connect(form.GRFA)
    timer2.start(2000)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

