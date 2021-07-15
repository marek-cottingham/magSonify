import unittest
import numpy as np

class numpyunittest_TestCase(unittest.TestCase):
    def assertNumpyClose(s,a,b,equal_nan=True):
        s.assertTupleEqual(a.shape,b.shape)
        af = a.flatten()
        bf = b.flatten()
        for i in range(len(af)):
            try:
                s.assertTrue(np.isclose(a[i], b[i], equal_nan=equal_nan))
            except:
                print(
                    f"Not equal: a[{i}] = {a[i]}; b[{i}] = {b[i]} \n"
                    f"- {a} \n"
                    f"+ {b}"
                )
                raise
     
