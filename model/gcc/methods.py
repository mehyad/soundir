import time
import numpy as np
from model.gcc import utils


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print("Time used: %.5f s" % (end_time - start_time))
        return result

    return wrapper


@timer
def numerical_calculation_GD( gcc_all,mic, v, fs):
    ALPHA               = 0.005
    ERROR_THRESHOLD     = 1e-1
    ITERATION_THRESHOLD = 500
    FACTOR_MATRIX       = np.array([[1, -1],])
    DELAY_REFERENCE     = utils.get_one_delay_point(gcc_all, 20, 20)

    obj       = np.array([1, 1])
    error     = 100
    iteration = 0

    while (error > ERROR_THRESHOLD) and (iteration < ITERATION_THRESHOLD):
        _range = np.power(np.ones((1, 1)) * obj - mic, 2)
        _range = np.reshape(np.sqrt(np.sum(_range, 1)), (-1, 1))

        delay = np.dot(FACTOR_MATRIX, _range) * 2 / v * fs
        error = np.sum(np.power(delay - DELAY_REFERENCE, 2))

        range_gradient = (1 / (np.dot(_range, np.ones((1, 2)))) * (np.ones((1, 1)) * obj - mic))
        delay_gradient = np.dot(FACTOR_MATRIX, range_gradient)

        delay_error    = np.dot((delay - DELAY_REFERENCE), np.ones((1, 2)))
        error_gradient = np.sum(delay_gradient * delay_error * 4 * fs / v, axis=0)

        obj = obj - ALPHA * error_gradient
        iteration += 1
    return obj


@timer
def srp_phat_maxFind_method(gcc_all_0, mic, v, fs):

    FRAME_LENGTH = (np.size(gcc_all_0, 1)) / 2
    X_AXIS_RANGE = np.arange(0, 8, 0.12)
    Y_AXIS_RANGE = np.arange(0, 8, 0.12)
    INDEXES = utils.calc_xcorr_cuples(mic)

    energy_calc = 0
    for x in X_AXIS_RANGE:
        for y in Y_AXIS_RANGE:
            obj = np.array([x, y])
            distances = [
                np.sqrt(np.sum(np.power(obj - mic[i], 2))) for i in range(len(mic))
            ]
            delays = [2 * (distances[i[0]] - distances[i[1]]) / v * fs for i in INDEXES]
            energy_xx_cac = np.zeros((1, 1))
            for i in range(1):
                index = (
                    FRAME_LENGTH
                    + np.floor(delays[i])
                    + np.array([i for i in range(-3, 5)])
                )
                index_ = index.astype(int)
                temp = np.array([gcc_all_0[i][j] for j in index_])
                energy_xx_cac[0, i] = utils.sinc(temp, index, FRAME_LENGTH + delays[i])

            energy_sum = np.sum(energy_xx_cac)
            if energy_sum > energy_calc:
                energy_calc = energy_sum
                result = obj
    return result

