#!/usr/bin/env python
# coding: utf8

""" Unit testing for Separator class. """

__email__ = 'research@deezer.com'
__author__ = 'Deezer Research'
__license__ = 'MIT License'

import filecmp
import itertools
from os import makedirs
from os.path import splitext, basename, exists, join
from tempfile import TemporaryDirectory

import pytest
import numpy as np

import tensorflow as tf

from spleeter.audio.adapter import get_default_audio_adapter
from spleeter.commands import create_argument_parser

from spleeter.commands import evaluate

from spleeter.utils.configuration import load_configuration

res_4stems = {  "vocals": {
                    "SDR": 0.000,
                    "SAR": -15.856,
                    "SIR": -6.861,
                    "ISR": 0.000
                },
                "drums": {
                    "SDR": -0.069,
                    "SAR": -15.769,
                    "SIR": -5.049,
                    "ISR": 0.001
                },
                "bass":{
                    "SDR": -0.000,
                    "SAR": -10.499,
                    "SIR": -6.988,
                    "ISR": -0.000
                },
                "other":{
                    "SDR": -1.365,
                    "SAR": -14.591,
                    "SIR": -4.751,
                    "ISR": -0.016
                }
            }


def generate_fake_eval_dataset(path):
    aa = get_default_audio_adapter()
    n_songs = 2
    fs = 44100
    duration = 3
    n_channels = 2
    rng = np.random.RandomState(seed=0)
    for song in range(n_songs):
        song_path = join(path, "test", f"song{song}")
        makedirs(song_path, exist_ok=True)
        for instr in ["mixture", "vocals", "bass", "drums", "other"]:
            filename = join(song_path, f"{instr}.wav")
            data = rng.rand(duration*fs, n_channels)-0.5
            aa.save(filename, data, fs)


def test_evaluate(path="FAKE_MUSDB_DIR"):
    generate_fake_eval_dataset(path)
    p = create_argument_parser()
    arguments = p.parse_args(["evaluate", "-p", "spleeter:4stems", "--mus_dir", path])
    params = load_configuration(arguments.configuration)
    metrics = evaluate.entrypoint(arguments, params)
    for instrument, metric in metrics.items():
        print(instrument), print(metric)
        for m, value in metric.items():
            print(np.median(value)), print(res_4stems[instrument][m])
            assert np.allclose(np.median(value), res_4stems[instrument][m], atol=1e-3)