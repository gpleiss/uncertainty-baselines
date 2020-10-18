# coding=utf-8
# Copyright 2020 The Uncertainty Baselines Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""Tests for speech_commands."""

from absl.testing import parameterized
import numpy as np
import tensorflow.compat.v2 as tf
import uncertainty_baselines as ub
from uncertainty_baselines.datasets import base


class SpeechCommandsDatasetTest(tf.test.TestCase, parameterized.TestCase):

  @parameterized.named_parameters(
      ('Train', base.Split.TRAIN), ('Validation', base.Split.VAL),
      ('Test', base.Split.TEST), ('WhiteNoiseNegative5DB', ('white_noise', -5)),
      ('PitchShift4Semitones', ('pitch_shift', 4)),
      ('LowPassFiltering4kHz', ('low_pass', 4)), ('RoomReverb12M',
                                                  ('room_reverb', 12)))
  def testSpeechCommandsDataset(self, split):
    batch_size = 35
    eval_batch_size = 25
    dataset_builder = ub.datasets.SpeechCommandsDataset(
        batch_size=batch_size,
        eval_batch_size=eval_batch_size,
        shuffle_buffer_size=20)
    dataset = dataset_builder.build(split).take(1)
    element = next(iter(dataset))
    features = element['features']
    labels = element['labels']
    if split == base.Split.TRAIN:
      self.assertEqual(
          features.shape,
          (batch_size, ub.datasets.SpeechCommandsDataset.AUDIO_LENGTH))
      self.assertEqual(labels.shape, (batch_size,))
    else:
      self.assertEqual(
          features.shape,
          (eval_batch_size, ub.datasets.SpeechCommandsDataset.AUDIO_LENGTH))
      self.assertEqual(labels.shape, (eval_batch_size,))
    # The in-distrubtions labels go up to 10 only.
    self.assertFalse(np.any(labels > 10))

    # Uncomment the code here to generate sample .wav files for inspection.
    # from scipy.io import wavfile
    # import tempfile
    # if isinstance(split, tuple):
    #   for i, label in enumerate(labels.numpy()):
    #     wav_file_path = tempfile.mktemp() + '_%s_label_%d.wav' % (
    #         split[0], label)
    #     wavfile.write(wav_file_path, 16000, features.numpy()[i] / 32768)
    #     print('Wrote to %s' % wav_file_path)

  def testSpeechCommandsDatasetSemanticShiftSplit(self):
    batch_size = 7
    eval_batch_size = 5
    dataset_builder = ub.datasets.SpeechCommandsDataset(
        batch_size=batch_size,
        eval_batch_size=eval_batch_size,
        shuffle_buffer_size=20)
    dataset = dataset_builder.build(('semantic_shift',)).take(1)
    element = next(iter(dataset))
    features = element['features']
    labels = element['labels']

    self.assertEqual(
        features.shape,
        (eval_batch_size, ub.datasets.SpeechCommandsDataset.AUDIO_LENGTH))
    self.assertEqual(labels.shape, (eval_batch_size,))
    # The semantic shift split has only the label 11, which differs from the
    # non-semantic-shifted labels: 0 - 10.
    self.assertFalse(np.any(labels != 11))

  def testInvalidSplitKeyNameLeadsToException(self):
    dataset_builder = ub.datasets.SpeechCommandsDataset(
        batch_size=7, eval_batch_size=5, shuffle_buffer_size=20)
    split = ('nonsensical_split', 42)
    with self.assertRaisesRegex(ValueError,
                                r'Unrecognized shift split: nonsensical_split'):
      dataset_builder.build(split)


if __name__ == '__main__':
  tf.test.main()