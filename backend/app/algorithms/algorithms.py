# app/algorithms/algorithms.py

import numpy as np
from scipy.fft import fft
from typing import List

def spectrum(signal: List[float], fs: float = 1000, remove_dc: bool = True, window: str = 'hann'):
    """
    Вычисляет спектр сигнала с помощью FFT.

    signal: список значений (может содержать Decimal)
    fs: частота дискретизации
    remove_dc: удалять ли постоянную составляющую
    window: тип оконной функции
    """
    # Приводим все значения к float
    # Проверка на пустой сигнал
    if len(signal) == 0:
        return np.array([]), np.array([])  # или raise ValueError(...)

    # Приводим все значения к float
    signal = np.array([float(x) for x in signal], dtype=float)
    n = len(signal)

    # Удаляем DC-составляющую
    if remove_dc:
        signal = signal - np.mean(signal)

    # Оконная функция
    if window == 'hann':
        window_vals = np.hanning(n)
    elif window == 'hamming':
        window_vals = np.hamming(n)
    else:
        window_vals = np.ones(n)

    signal_windowed = signal * window_vals

    # FFT (берём половину спектра)
    fft_result = fft(signal_windowed)[:n // 2]
    frequencies = np.fft.fftfreq(n, 1 / fs)[:n // 2]
    amplitudes = np.abs(fft_result) / (n // 2)  # нормализация
    return frequencies, amplitudes

def func1(values_x, values_y):
    # Пример дополнительной функции: умножаем на 5
    for i in range(len(values_y)):
        values_y[i] = float(values_y[i]) * 5
    return values_x, values_y

def execute_function(function_name, values_x, values_y):
    # Поддерживаем spectrum и alias fourier
    if function_name in ('spectrum', 'fourier'):
        return spectrum(values_y)
    if function_name == 'func1':
        return func1(values_x, values_y)
    # Если нужно добавить другие функции — добавляйте здесь
    raise ValueError(f"Unknown function '{function_name}'")
