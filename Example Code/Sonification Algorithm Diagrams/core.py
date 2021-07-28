

import context
context.get()

import magSonify
import datetime

def setup(
    event = (
        datetime.datetime(2008,12,8),
        datetime.datetime(2008,12,9)
    )
):
    mag = magSonify.THEMISdata()
    mag.importCDAS(
        *event
    )
    mag.defaultProcessing()
    pol = mag.magneticFieldMeanFieldCoordinates.extractKey(1)

    polBefore = pol.copy()
    return pol, polBefore