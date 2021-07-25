
import zmq
import json, datetime
from scipy.signal import stft
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import io

import context as sonifyContext
sonifyContext.get()

import magSonify

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:
    #  Wait for next request from client
    message = socket.recv()
    #message = b'["07/12/2008","D","12","pol"]'
    datetimeStr, sat, hours, component = json.loads(message)
    print(datetimeStr, sat, hours, component)

    componentToInt = {"com": 0, "pol": 1, "tor": 2}

    datetimeConverted = datetime.datetime.strptime(datetimeStr,"%d/%m/%Y")

    # Do data processing
    mag = magSonify.THEMISdata()
    interval = datetime.timedelta(hours=int(hours))
    mag.importCDAS(
        datetimeConverted,
        datetimeConverted + interval,
        sat
    )
    mag.defaultProcessing()
    ax = mag.magneticFieldMeanFieldCoordinates.extractKey(componentToInt[component])

    # Generate the plot
    nperseg = 1024//2
    f, t, Zxx_dBdt = stft(ax.x, fs=1/3.0, nperseg=nperseg, noverlap=nperseg//4*3)
    dt_list = [datetimeConverted+datetime.timedelta(seconds=ii) for ii in t]

    myFmt = mdates.DateFormatter('%H:%M')
    xlim=[datetimeConverted,datetimeConverted + interval]

    fig, ax2 = plt.subplots(1,1)
    cmap=plt.get_cmap('inferno')
    im=ax2.pcolormesh(dt_list, f*1000., np.abs(Zxx_dBdt), vmin=0, vmax=0.04, shading='auto', cmap=cmap)
    ax2.set(ylim=[0,25])
    ax2.xaxis.set_major_formatter(myFmt)
    ax2.set_title('STFT Magnitude')
    ax2.set_ylabel('Frequency [mHz]')
    ax2.set_xlabel('Time [UT]')

    # Save plot to string buffer and prepare to send
    
    imgdata = io.BytesIO()

    plt.savefig(imgdata, format='svg')

    print(imgdata)

    #  Send reply back to client
    socket.send(imgdata.getvalue())