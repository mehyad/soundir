from scipy.io import wavfile
import numpy as np

from model.gcc import methods, utils


def signal_to_noise(a, axis=0, ddof=0):
    a = np.asanyarray(a)
    m = a.mean(axis)
    sd = a.std(axis=axis, ddof=ddof)
    return abs(10 * np.log10(np.abs(np.where(sd == 0, 0, m / sd))))


def filter(signal, fs):
    max_ = np.max(signal)
    signal_ = nr.reduce_noise(signal, fs, True)
    gain = max_ / np.max(signal_)
    return signal_ * gain


# def plot_signal(signal, microphone=0):
#     _time = np.linspace(0, (signal[microphone].shape[0]) / SAMPLING_FREQUENCY, (signal[microphone].shape[0]))
#     plt.figure(figsize=(10, 4))
#     plt.plot(_time, signal[microphone], label="signal")
#     plt.xlabel("t/s")
#     plt.legend()
#     plt.show()

def tdoa( FILE_NAME,distance,method):
    [SAMPLING_FREQUENCY,SIGNALS] = wavfile.read(FILE_NAME)
    try:
        
        SNR = round(signal_to_noise(SIGNALS[:, 0]))
        print("SNR: ", SNR)
        # if SNR < 30:
        #     filtered_left_signal = filter(SIGNALS[:, 0], SAMPLING_FREQUENCY)
        #     filtered_right_signal= filter(SIGNALS[:, 1], SAMPLING_FREQUENCY)
        #     s_ideal = [
        #         np.expand_dims(filtered_left_signal , 1),
        #         np.expand_dims(filtered_right_signal, 1)
        #     ]
        # else:
        s_ideal = [
            np.expand_dims(SIGNALS[:, 0], 1),
            np.expand_dims(SIGNALS[:, 1], 1)
        ]
        FRAME_LENGTH = 1200
        OVER_LAPPED  = 400
        
        s_ideal_enframe = [utils.enframe(i, FRAME_LENGTH, OVER_LAPPED) for i in s_ideal]

        frameNum  = np.size(s_ideal_enframe[0], 0)
        gcc_all_0 = np.array(utils.gcc_all(frameNum, FRAME_LENGTH, s_ideal_enframe))

        # plt.plot(gcc_all_0[1])
        # plt.stem(gcc_all_0[0])
        # plt.show()
        distance = distance/200
        #------------------
        MICROPHONE             = np.array([[distance, 0], [-distance, 0],])
        SOUND_VELOCITY         = 340
        if method == "SRP":
            result1 = methods.srp_phat_maxFind_method(gcc_all_0, MICROPHONE, SOUND_VELOCITY, SAMPLING_FREQUENCY)
            return utils.make_result(result1),'OK'
        if method == "GD":
            result2 = methods.numerical_calculation_GD(gcc_all_0, MICROPHONE, SOUND_VELOCITY, SAMPLING_FREQUENCY)
            return utils.make_result(result2),'OK'
    except:
        return 0,'signal not stereo'

