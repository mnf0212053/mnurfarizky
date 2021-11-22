# Author: Muhammad Nur Farizky
# Year: 2021
# Description: 
# This program is used in my research during my thesis to map 
# the topological surface of an object using ultrasonic sensor. Requires Raspberry Pi.

import sys, os
sys.path.append('/home/pi/XlsxWriter')

import xlsxwriter

import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

TRIG = 26
RST = 24
CLKCOUNT = 21
SHLD = 12
QH = 19
LED = 6
BTN = 25
TRIG_COMP = 22
ECHO_COMP = 27

RX_SEL = 13 #Rx selector, 1 for vertical, 0 for horizontal
MOTOR_POS = 20
MOTOR_NEG = 16

dly = 0.1 #originally 0.1
n = 5
ver_max = 24 #mm
ver_res = 2 #mm
ver_nn = ver_max/ver_res

hor_max = 130 #mm
hor_res = 10 #mm
hor_nn = hor_max/hor_res

VER = 1
HOR = 0
ON = 1
OFF = 0

gpio.setup(RX_SEL, gpio.OUT)
gpio.setup(MOTOR_POS, gpio.OUT)
gpio.setup(MOTOR_NEG, gpio.OUT)

gpio.output(MOTOR_POS, gpio.HIGH)
gpio.output(MOTOR_NEG, gpio.HIGH)

gpio.setup(TRIG, gpio.OUT)
gpio.output(TRIG, gpio.HIGH)

gpio.setup(RST, gpio.OUT)
gpio.output(RST, gpio.LOW)

gpio.setup(CLKCOUNT, gpio.OUT)
gpio.output(CLKCOUNT, gpio.LOW)


gpio.setup(SHLD, gpio.OUT)
gpio.output(SHLD, gpio.HIGH)

gpio.setup(QH, gpio.IN)

gpio.setup(BTN, gpio.IN)

gpio.setup(LED, gpio.OUT)
gpio.output(LED, gpio.LOW)

gpio.setup(TRIG_COMP, gpio.IN)
gpio.setup(ECHO_COMP, gpio.IN)

print("Init ready.")

def reset():
    gpio.output(RST, gpio.LOW)
    time.sleep(dly)
    gpio.output(RST, gpio.HIGH)
    
def reset_total():
    reset()
    gpio.output(RST, gpio.LOW)
    gpio.output(TRIG, gpio.HIGH)
    rx_select(VER)
    
def rx_select(DIR):
    if DIR == 0:
        gpio.output(RX_SEL, gpio.LOW)
    elif DIR == 1:
        gpio.output(RX_SEL, gpio.HIGH)
        
def trigger(STATE):
    if STATE == ON:
        gpio.output(TRIG, gpio.LOW)
    elif STATE == OFF:
        gpio.output(TRIG, gpio.HIGH)
        

def go_left(dly):
    gpio.output(MOTOR_NEG, gpio.LOW)
    time.sleep(dly)
    gpio.output(MOTOR_NEG, gpio.HIGH)
    
def go_right(dly):
    gpio.output(MOTOR_POS, gpio.LOW)
    time.sleep(dly)
    gpio.output(MOTOR_POS, gpio.HIGH)
    
def save_data(filename, data):
    f = open(filename, "w")
    f.write(str(data))
    f.close()
    
def load_data(filename):
    f = open(filename, "r")
    data = float(f.read(5))
    f.close()
    return data
    

def readpin():
    read_dly = 0.005 #originally 0.05
    #print("Saving bit...")
    gpio.output(SHLD, gpio.LOW)
    time.sleep(read_dly)
    gpio.output(SHLD, gpio.HIGH)
    time.sleep(read_dly)
    #print("Bit saved. Reading counter...")
    QHarr = []

    for i in range(0, 8):
        QHarr.append(gpio.input(QH))
        #print("Bit ", i, " : ", QHarr[i])
        gpio.output(CLKCOUNT, gpio.HIGH)
        time.sleep(read_dly)
        gpio.output(CLKCOUNT, gpio.LOW)
        time.sleep(read_dly)
        
    count = QHarr[0] + QHarr[1]*2 + QHarr[2]*4 + QHarr[3]*8 + QHarr[4]*16 + QHarr[5]*32 + QHarr[6]*64 + QHarr[7]*128
    #print("Bit reading finished. The counted value is ", count)
    return count

def reset_position():
    go_left(1)
    
def single_measurement():    
    trigger(ON)
    time.sleep(dly)
    trigger(OFF)
    #for k in range(0,2):
    cnt = readpin()
    reset()
    #print("cnt = ", cnt)
    return cnt
    
def least_square(x, y):
    N = len(x)
    sxy = 0
    for i in range(0, N):
        sxy = sxy + x[i]*y[i]
        
    sx2 = 0
    for i in range(0, N):
        sx2 = sx2 + x[i]*x[i]
        
    m = (N*sxy - sum(x)*sum(y)) / (N*sx2 - sum(x)*sum(x))
    b = (sum(y) - m*sum(x)) / N
    
    return m, b
     
def round_res(num, deg):
    _num = num
    i = 0
    while _num > deg:
        _num = _num - deg
        i = i + 1
    _num = _num/deg
    if _num < 0.5:
        return deg*i
    else:
        return deg*(i+1)
            
def calibration(length):
    avg_rep = []
    std_rep = []
    for j in range(0, 5):
        countavg = 0
        count_std = []
        dsq = 0
        for i in range(0,n+1):
            #gpio.output(TRIG, gpio.HIGH)
            #time.sleep(dly)
            #gpio.output(TRIG, gpio.LOW)
            #for k in range(0,2):
            newcnt = single_measurement()
            count_std.append(newcnt)
            countavg = countavg + newcnt
            #reset()
            
        count_total = 0
        for i in range(1, n+1):
            count_total = count_std[i] + count_total
        avg = count_total/n
        avg_rep.append(avg)
        for i in range(1, n+1):
            dsq = dsq + pow(count_std[i] - avg, 2)
        stdev = round(pow(dsq/(n - 1) , 0.5), 2)
        std_rep.append(stdev)
    for i in range(0, len(avg_rep)):
        if std_rep[i] == min(std_rep):
            avg = avg_rep[i]
            stdev = std_rep[i]
            break
    print(length, " mm # ", avg, " # ", stdev)
    return avg, stdev

            
def calibration_h(length, DIR):
    if DIR == VER:
        m = load_data('VER/ver_cal_m.txt')
        b = load_data('VER/ver_cal_b.txt')
        dgr = ver_res #mm
    else:
        m = load_data('HOR/hor_cal_m.txt')
        b = load_data('HOR/hor_cal_b.txt')
        dgr = hor_res #mm
    avg_rep = []
    std_rep = []
    for j in range(0, 5):
        heightavg = 0
        height_std = []
        dsq = 0
        for i in range(0,n+1):
            #gpio.output(TRIG, gpio.HIGH)
            #time.sleep(dly)
            #gpio.output(TRIG, gpio.LOW)
            #for k in range(0,2):
            newhgt = round_res((single_measurement() - b)/m, dgr)
            height_std.append(newhgt)
            heightavg = heightavg + newhgt
            #reset()
            
        height_total = 0
        for i in range(1, n+1):
            height_total = height_std[i] + height_total
        avg = round_res(height_total/n, dgr)
        avg_rep.append(avg)
        for i in range(1, n+1):
            dsq = dsq + pow(height_std[i] - avg, 2)
        stdev = round_res(pow(dsq/(n - 1) , 0.5), dgr/2)
        std_rep.append(stdev)
    for i in range(0, len(avg_rep)):
        if std_rep[i] == min(std_rep):
            avg = avg_rep[i]
            stdev = std_rep[i]
            break
    print(length, " mm # ", avg, " # ", stdev)
    return avg, stdev

def measure(DIR):
    if DIR == VER:
        m = load_data('VER/ver_cal_m.txt')
        b = load_data('VER/ver_cal_b.txt')
        dgr = ver_res #mm
    else:
        m = load_data('HOR/hor_cal_m.txt')
        b = load_data('HOR/hor_cal_b.txt')
        dgr = hor_res #mm
    avg_rep = []
    std_rep = []
    for j in range(0, 2):
        heightavg = 0
        height_std = []
        dsq = 0
        for i in range(0,n+1):
            #for k in range(0,2):
            newhgt = round_res((single_measurement() - b)/m, dgr)
            height_std.append(newhgt)
            heightavg = heightavg + newhgt
            
        height_total = 0
        for i in range(1, n+1):
            height_total = height_std[i] + height_total
        avg = round_res(height_total/n, dgr)
        avg_rep.append(avg)
        for i in range(1, n+1):
            dsq = dsq + pow(height_std[i] - avg, 2)
        stdev = round_res(pow(dsq/(n - 1) , 0.5), dgr/2)
        std_rep.append(stdev)
    for i in range(0, len(avg_rep)):
        if std_rep[i] == min(std_rep):
            avg = avg_rep[i]
            stdev = std_rep[i]
            break
    return avg, stdev

def calibration2(DIR):
    if DIR == VER:
        nn = int(ver_nn) #16
        res = ver_res
        rx_select(VER)
    else:
        nn = int(hor_nn)
        res = hor_res
        rx_select(HOR)
    hgt_arr = []
    avg_arr = []
    std_arr = []
    print("Calibration is started. Push the button to start the measurement.")
    print("Height # Average # Std. Deviation")
    for i in range(0,nn+1):
        gpio.output(LED, gpio.HIGH)
        gpio.wait_for_edge(BTN, gpio.RISING)
        gpio.output(LED, gpio.LOW)
        if DIR == VER:
            avg, std = calibration((nn-i)*res)
            hgt_arr.append((nn-i)*res)
        else:
            avg, std = calibration(i*res)
            hgt_arr.append(i*res)
        avg_arr.append(avg)
        std_arr.append(std)
    m, b = least_square(hgt_arr, avg_arr)
    if b > 0:
        print("Equation : ", "y = ", round(m, 2), "x + ", round(b, 2))
    elif b == 0:
        print("Equation : ", "y = ", round(m, 2), "x")
    else:
        print("Equation : ", "y = ", round(m, 2), "x - ", (-1)*round(b, 2))
        
    if DIR == VER:
        file_xls = 'VER/ver_calibration.xlsx'
    else:
        file_xls = 'HOR/hor_calibration.xlsx'
        
    workbook = xlsxwriter.Workbook(file_xls)
    worksheet = workbook.add_worksheet()
    
    for i in range(0, nn+1):
        worksheet.write(i, 0, hgt_arr[i])
        worksheet.write(i, 1, avg_arr[i])
        worksheet.write(i, 2, std_arr[i])
        
    worksheet.write(0, 3, m)
    worksheet.write(0, 4, b)

    workbook.close()
    
    if DIR == VER:
        save_data('VER/ver_cal_m.txt', m)
        save_data('VER/ver_cal_b.txt', b)
    else:
        save_data('HOR/hor_cal_m.txt', m)
        save_data('HOR/hor_cal_b.txt', b)
          
def test_measure(DIR):
    if DIR == VER:
        nn = int(ver_nn) #16
        res = ver_res
        rx_select(VER)
    else:
        nn = int(hor_nn)
        res = hor_res
        rx_select(HOR)
    hgt_arr = []
    avg_arr = []
    std_arr = []
    print("Calibration is started. Push the button to start the measurement.")
    print("Height # Average # Std. Deviation")
    for i in range(0,nn+1):
        gpio.output(LED, gpio.HIGH)
        gpio.wait_for_edge(BTN, gpio.RISING)
        gpio.output(LED, gpio.LOW)
        if DIR == VER:
            avg, std = calibration_h((nn-i)*res, DIR)
            hgt_arr.append((nn-i)*res)
        else:
            avg, std = calibration_h(i*res, DIR)
            hgt_arr.append(i*res)
        avg_arr.append(avg)
        std_arr.append(std)
    m, b = least_square(hgt_arr, avg_arr)
    if b > 0:
        print("Equation : ", "y = ", round(m, 2), "x + ", round(b, 2))
    elif b == 0:
        print("Equation : ", "y = ", round(m, 2), "x")
    else:
        print("Equation : ", "y = ", round(m, 2), "x - ", (-1)*round(b, 2))
        
    if DIR == VER:
        file_xls = 'VER/ver_calibration_h.xlsx'
    else:
        file_xls = 'HOR/hor_calibration_h.xlsx'
        
    workbook = xlsxwriter.Workbook(file_xls)
    worksheet = workbook.add_worksheet()
    
    for i in range(0, nn+1):
        worksheet.write(i, 0, hgt_arr[i])
        worksheet.write(i, 1, avg_arr[i])
        worksheet.write(i, 2, std_arr[i])
        
    worksheet.write(0, 3, m)
    worksheet.write(0, 4, b)

    workbook.close()
    
    if DIR == VER:
        save_data('VER/ver_cal_m_h.txt', m)
        save_data('VER/ver_cal_b_h.txt', b)
    else:
        save_data('HOR/hor_cal_m_h.txt', m)
        save_data('HOR/hor_cal_b_h.txt', b)

def shift_register_check():
    single_measurement()
    for i in range(0,10):
        time.sleep(0.5)
        print(readpin())
        
def indicator_test():
    #led turns on while the button is pressed
    while True:
        gpio.wait_for_edge(BTN, gpio.RISING)
        gpio.output(LED, gpio.HIGH)
        gpio.wait_for_edge(BTN, gpio.FALLING)
        gpio.output(LED, gpio.LOW)
        
def test_comp_t():
    trigger(OFF)
    time.sleep(1)
    start = time.time()
    stop = time.time()
    trigger(ON)
    #gpio.wait_for_edge(ECHO_COMP, gpio.RISING)
    stop = time.time()
    print(stop-start)

def main_program():
    #algo program 2 :
            #baca tx vertikal
            #baca tx horizontal
            #gerakin tatakan ke kanan
            #ulangi 1-3 hingga ujung

    #reset_position()
    ver_data_avg = []
    ver_data_std = []
    hor_data = []
    hor_data_avg = []
    hor_data_std = []
    
    nn = int(hor_nn)
    for i in range(0, nn):
        rx_select(VER)
        h_ver_avg, h_ver_std = measure(VER)
        ver_data_avg.append(h_ver_avg)
        ver_data_std.append(h_ver_std)
        rx_select(HOR)
        h_hor_avg, h_hor_std = measure(HOR)
        hor_data_avg.append(h_hor_avg)
        hor_data_std.append(h_hor_std)
        pos_current = h_hor_avg
        while pos_current <= i*hor_res:
            go_right(0.07)
            pos_current, dum = measure(HOR)
            print(pos_current, " # ", h_hor_avg)
        hor_data.append(i*hor_res)
        
    file_xls = 'MEASURE/ms_recent.xlsx'
        
    workbook = xlsxwriter.Workbook(file_xls)
    worksheet = workbook.add_worksheet()
    
    for i in range(0, nn):
        worksheet.write(i, 0, hor_data_avg[i])
        worksheet.write(i, 1, hor_data[i])
        worksheet.write(i, 2, ver_data_avg[i])
        worksheet.write(i, 3, ver_data_std[i])
        worksheet.write(i, 4, hor_data_std[i])
        

    workbook.close()

def single_debug():
    m = load_data('VER/ver_cal_m.txt')
    b = load_data('VER/ver_cal_b.txt')
    while True:
        val = single_measurement()
        print(round_res((val - b)/m, 3), " # ", val)
        time.sleep(1)
        
def test_trigger():
    while True:
        rx_select(VER)
        time.sleep(0.5)
        trigger(OFF)
        print('Trigger OFF')
        time.sleep(5)
        reset()
        rx_select(VER)
        time.sleep(0.5)
        trigger(ON)
        print('Trigger ON')
        time.sleep(5)
        
def reset_test():
    while True:
        reset()
        time.sleep(1)
reset_total()
#main_program()
#calibration2(HOR)
#test_measure(HOR)
#rx_select(VER)
#trigger(ON)
test_trigger()
#reset_test()
#single_debug()
#test_comp_t()
#gpio.output(RST, gpio.HIGH)
#rx_select(HOR)
reset_total()

    
