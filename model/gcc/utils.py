import itertools
import math
from copy import deepcopy

import numpy as np
from numpy.fft import fft, fftshift, ifft


def delete_folder(paths):
    import shutil
    for path in paths:
        shutil.rmtree(path)


def nextpow2(N):
    """ Function for finding the next power of 2 """
    N = abs(N)
    for i in range(N):
        if 2 ** i >= N:
            return i


def enframe(x, frame_len, overloap, win=None):
    N = len(x)
    step_len = frame_len - overloap
    frame_num = int(np.floor((N - overloap) / step_len))
    y = np.zeros((frame_num, frame_len))
    n = [i for i in range(1, frame_len + 1)]
    if win == "hanning":
        window = 0.5 - 0.5 * np.cos(2 * np.pi * n / frame_len)
    elif win == "hamming":
        window = 0.54 - 0.46 * np.cos(2 * np.pi * n / frame_len)
    else:  # rect
        window = np.ones((1, frame_len))
    for i in range(frame_num):
        start_index = (i) * step_len
        end_index = start_index + frame_len
        y[i, :] = x[start_index:end_index, 0] * window
    return y


def calc_xcorr_cuples(signal):
    const = (i for i in range(signal.shape[0]))
    cuples = []
    for i in itertools.combinations(const, 2):
        cuples.append(i)
    return cuples


def gcc_phat(x1, x2):
    Ncorr = 2 * len(x1) - 1
    NFFT = 2 ** nextpow2(Ncorr)
    Gss = fft(x1, NFFT) * fft(x2, NFFT).conj()
    Gss = np.expand_dims(Gss, 0)
    xcorr_cac = fftshift(ifft(np.exp(1j * np.angle(Gss))))
    y = xcorr_cac[
        0, int(NFFT / 2 + 1 - (Ncorr - 1) / 2) - 1 : int(NFFT / 2 + 1 + (Ncorr - 1) / 2)
    ]
    y = np.expand_dims(y, 0)
    return y


def gcc_all_2(frame_num, frame_len, s_ideal_enframe):
    s1 = s_ideal_enframe[0]
    s2 = s_ideal_enframe[1]
    xcorrCac12 = np.zeros((frame_num, 2 * frame_len - 1), dtype="complex_")
    for i in range(frame_num):
        xcorrCac12[i, :] = gcc_phat(s1[i], s2[i])
    xcorr12 = np.abs(np.sum(xcorrCac12, axis=0))
    return [xcorr12]


def gcc_all(frame_num, frame_len, s_ideal_enframe):
    s1, s2 = s_ideal_enframe
    xcorr_cac = [
        np.zeros((frame_num, 2 * frame_len - 1), dtype="complex_") for _ in range(1)
    ]
    for i in range(frame_num):
        xcorr_cac[0][i, :] = gcc_phat(s1[i], s2[i])
    xcorr = [np.abs(np.sum(xcorr_cac[i], axis=0)) for i in range(1)]
    return xcorr


def cartesian_to_polar(obj):
    x, y= obj
    r = math.sqrt(x *x + y *y )
    # theta = np.arctan(y / x) / np.pi * 180
    theta = math.atan(y / x) / math.pi * 180
    theta = theta if x >= 0 else theta + 180
    result = np.array([r,theta])
    if np.isnan(result).any():
        return 0
    return result


def polar_to_cartesian(obj):
    r, theta = obj
    To_angle = np.pi / 180
    x = r *  np.cos(theta * To_angle)
    y = r * np.sin(theta * To_angle)
    return np.array([x, y])


def sinc(x, n, t):
    find_index = np.where(n == t)[0]
    if len(find_index) != 0:
        return x[find_index]
    # print("haa")
    y = 0
    N = len(x)
    for i in range(N):
        y += x[i] * np.sin((t - n[i]) * np.pi) / ((t - n[i]) * np.pi)
    return y


def sinc_vector(input_signal, input_time, interpolation_points):
    _input_signal = deepcopy(input_signal)
    _input_time = deepcopy(input_time)
    length_input_time = len(_input_time)
    total_pips = length_input_time + interpolation_points * (length_input_time - 1) + 1
    output_signal = np.zeros((1, total_pips))
    output_time = np.zeros((1, total_pips))
    _input_time = np.insert(_input_time, 0, 0)
    _input_signal = np.insert(_input_signal, 0, 0)
    length_input_time = len(_input_time)
    interpolation_points_ = interpolation_points + 1
    for i in range(1, total_pips):
        calc_index = int(math.ceil(i / (interpolation_points_)))
        if i % (interpolation_points_) == 1:
            output_signal[0, i] = _input_signal[calc_index]
            output_time[0, i] = _input_time[calc_index]
        else:
            _out_signal = 0
            time_position_before = _input_time[calc_index]
            time_position_after = _input_time[calc_index + 1]
            dt = (time_position_after - time_position_before) / (interpolation_points_)
            _out_time = time_position_before + dt * (
                i
                - (interpolation_points_) * (math.ceil(i / (interpolation_points_) - 1))
                - 1
            )
            for j in range(1, length_input_time):
                _out_signal += (
                    _input_signal[j]
                    * np.sin((_out_time - _input_time[j]) * np.pi)
                    / ((_out_time - _input_time[j]) * np.pi)
                )
            output_signal[0, i] = _out_signal
            output_time[0, i] = _out_time

    return [output_signal[0, 1:], output_time[0, 1:]]


def get_one_delay_point(gcc_all_, inter_points, inter_radius):
    length_gcc = np.size(gcc_all_, 1)
    frame_length = int((length_gcc) / 2)
    delay_point_max = np.zeros((1, 1))
    for i in range(1):
        gcc_calculated = gcc_all_[i]
        max_index = int(np.where(gcc_calculated == np.max(gcc_calculated))[0])
        if max_index == frame_length:
            gcc_calculated[max_index] = 0
            max_index = int(np.where(gcc_calculated == np.max(gcc_calculated))[0])
        input_time = np.arange(
            max_index - inter_radius, max_index + inter_radius + 1, 1
        )
        input_signal = np.array([gcc_calculated[i] for i in input_time])
        output_signal, output_time = sinc_vector(input_signal, input_time, inter_points)
        max_index2 = int(np.where(output_signal == np.max(output_signal))[0])
        delay_point_max[i, 0] = output_time[max_index2]
    return delay_point_max - frame_length


def print_result(title, cartesian):
    polar = cartesian_to_polar(cartesian)
    print("---------------------------------------------------")
    print(f"{title}")
    print(
        "Cartesian coordinate result: %7.4f met, %7.4f met"
        % (cartesian[0], cartesian[1])
    )
    print(
        "polar coordinate result: %7.4f met, %7.4f deg"
        % (polar[0], polar[1])
    )
    print("\n")

def make_result(cartesian):
    angles=np.arange(0,181,5)
    r,theta = cartesian_to_polar(cartesian)
    angle = np.abs(angles-theta)
    angle = np.where(angle==np.min(angle))[0][0]
    return angles[angle]
