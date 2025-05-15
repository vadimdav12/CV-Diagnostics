# backend/app/algorithms/algorithms.py

import numpy as np
from scipy.fft import fft
from typing import List, Tuple, Any

def spectrum(signal: List[float], fs: float = 1000, remove_dc: bool = True, window: str = 'hann') -> Tuple[np.ndarray, np.ndarray]:
    """
    Вычисляет спектр сигнала с помощью FFT.
    """
    if len(signal) == 0:
        return np.array([]), np.array([])

    signal = np.array([float(x) for x in signal], dtype=float)
    n = len(signal)

    if remove_dc:
        signal = signal - np.mean(signal)

    if window == 'hann':
        win = np.hanning(n)
    elif window == 'hamming':
        win = np.hamming(n)
    else:
        win = np.ones(n)

    signal_windowed = signal * win
    fft_result = fft(signal_windowed)[:n // 2]
    frequencies = np.fft.fftfreq(n, 1 / fs)[:n // 2]
    amplitudes = np.abs(fft_result) / (n // 2)
    return frequencies, amplitudes

def lowpass(values_x: List[Any], values_y: List[float], window_size: int = 5) -> Tuple[List[Any], List[float]]:
    """
    Простой низкочастотный фильтр: скользящее среднее по y-значениям.
    window_size: размер окна скользящего среднего.
    """
    if len(values_y) == 0:
        return values_x, values_y

    y = np.array([float(v) for v in values_y], dtype=float)
    # pad для сохранения длины
    pad = window_size // 2
    y_padded = np.pad(y, (pad, pad), mode='edge')
    y_filtered = np.convolve(y_padded, np.ones(window_size)/window_size, mode='valid')
    return values_x, y_filtered.tolist()

def func1(values_x: List[Any], values_y: List[float]) -> Tuple[List[Any], List[float]]:
    """
    Пример дополнительной функции: умножаем все y-на значения на 5.
    """
    y = [float(v)*5 for v in values_y]
    return values_x, y

def execute_function(function_name: str, values_x: List[Any], values_y: List[float]) -> Tuple[Any, Any]:
    """
    Вызывает нужную функцию обработки данных.
    Поддерживаем: spectrum, fourier (alias), func1, lowpass.
    """
    name = function_name.lower()
    if name in ('spectrum', 'fourier'):
        return spectrum(values_y)
    if name == 'func1':
        return func1(values_x, values_y)
    if name in ('lowpass', 'filter'):
        # здесь можно регулировать размер окна, если есть параметр
        return lowpass(values_x, values_y)
    raise ValueError(f"Unknown function '{function_name}'")
