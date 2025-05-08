import numpy as np
from scipy.fft import fft
from typing import List


def spectrum(signal: List[float], fs: float = 1000, remove_dc: bool = True, window: str = 'hann'):
    """
    Вычисляет спектр сигнала с помощью FFT.

    Параметры:
        signal (list[float]): Входной сигнал (список значений).
        sensor_type (SensorType): Тип датчика ('vibration', 'current', 'temperature').
        fs (float): Частота дискретизации (Гц). По умолчанию 1000 Гц.
        remove_dc (bool): Удалять ли постоянную составляющую. По умолчанию True.
        window (str): Оконная функция ('hann', 'hamming', 'rect'). По умолчанию 'hann'.

    Возвращает:
        frequencies (np.ndarray): Массив частот (Гц).
        amplitudes (np.ndarray): Массив амплитуд.
    """
    signal = np.array(signal)
    n = len(signal)

    # Удаление постоянной составляющей (если нужно)
    if remove_dc:
        signal = signal - np.mean(signal)

    # Применение оконной функции
    if window == 'hann':
        window_vals = np.hanning(n)
    elif window == 'hamming':
        window_vals = np.hamming(n)
    else:  # прямоугольное окно
        window_vals = np.ones(n)

    signal_windowed = signal * window_vals

    # Вычисление FFT
    fft_result = fft(signal_windowed)[:n // 2]
    frequencies = np.fft.fftfreq(n, 1 / fs)[:n // 2]
    amplitudes = np.abs(fft_result) / (n // 2)  # Нормализация

    return frequencies, amplitudes

def func1(values_x, values_y):
    for i in range(len(values_y)):
        values_y[i] = values_y[i] * 5
    return values_x, values_y

def execute_function(function_name, values_x, values_y):
    if function_name == 'func1':
        return func1(values_x, values_y)
    if function_name == 'spectrum':
        return spectrum(values_y)