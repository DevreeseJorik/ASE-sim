from setups import GyaradosSetup, KakunaSetup
import logging
import numpy as np
import matplotlib.pyplot

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    matplotlib.pyplot.set_loglevel (level = 'warning')
    np.set_printoptions(formatter={'int':hex})
    GyaradosSetup().run()
    KakunaSetup().run()