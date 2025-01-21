# MIT License
# Copyright (c) 2025 aeeeeeep

import unittest
from unittest.mock import patch
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from objwatch import ObjWatch
from objwatch.wrappers import TensorShapeWrapper
import logging
from tests.util import filter_func_ptr


class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(28 * 28, 128)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = x.view(-1, 28 * 28)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x


input_size = 28 * 28
num_classes = 10
num_samples = 128
batch_size = 64

X = torch.randn(num_samples, input_size)
y = torch.randint(0, num_classes, (num_samples,))

train_dataset = TensorDataset(X, y)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

model = SimpleNet()
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)


def train():
    model.train()
    for epoch in range(1):
        for batch_idx, (data, target) in enumerate(train_loader):
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            if batch_idx % 100 == 0:
                print(
                    f'Train Epoch: {epoch} [{batch_idx * len(data)}/{len(train_loader.dataset)} '
                    f'({100. * batch_idx / len(train_loader):.0f}%)]\tLoss: {loss.item():.6f}'
                )


class TestPytorchTraining(unittest.TestCase):
    maxDiff = 1e9

    @patch('objwatch.utils.logger.get_logger')
    def test_training_with_objwatch(self, mock_logger):
        mock_logger.return_value = unittest.mock.Mock()

        obj_watch = ObjWatch(
            targets=['tests/test_torch_train.py'],
            exclude_targets=[],
            output=None,
            level=logging.DEBUG,
            simple=True,
            with_locals=False,
            with_globals=True,
            with_module_path=False,
            wrapper=TensorShapeWrapper,
        )
        obj_watch.start()

        with self.assertLogs('objwatch', level='DEBUG') as log:
            train()
        obj_watch.stop()

        generated_log = '\n'.join(log.output)
        golden_log_path = 'tests/utils/golden_torch_train_log.txt'
        with open(golden_log_path, 'r') as f:
            golden_log = f.read()
        self.assertEqual(
            filter_func_ptr(generated_log),
            filter_func_ptr(golden_log),
            "Generated log does not match the golden log. ",
        )


if __name__ == '__main__':
    unittest.main()
