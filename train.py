#!/usr/bin/env python3

# Imports
import numpy as np

import torch
import torch.nn as neural_net
import torch.nn.functional as func
from torch import optim
from torch.utils.data import Dataset


class ValueDataset(Dataset):
    def __init__(self):
        # Shadows name, blah blah
        data = np.load("processed/dataset.npz")
        self.X = data["arr_0"]
        self.Y = data["arr_1"]
        print("data loaded.", self.X.shape, self.Y.shape)

    def __len__(self):
        return self.X.shape[0]

    def __getitem__(self, idx):
        return self.X[idx], self.Y[idx]


class Net(neural_net.Module):
    def __init__(self):
        super(Net, self).__init__()
        # Applying a 2-D convolution over an input signal composed of several input planes

        # A
        self.a1 = neural_net.Conv2d(5, 16, kernel_size=3, padding=1)
        self.a2 = neural_net.Conv2d(16, 16, kernel_size=3, padding=1)
        self.a3 = neural_net.Conv2d(16, 32, kernel_size=3, stride=2)
        # B
        self.b1 = neural_net.Conv2d(32, 32, kernel_size=3, padding=1)
        self.b2 = neural_net.Conv2d(32, 32, kernel_size=3, padding=1)
        self.b3 = neural_net.Conv2d(32, 64, kernel_size=3, stride=2)
        # C
        self.c1 = neural_net.Conv2d(64, 64, kernel_size=2, padding=1)
        self.c2 = neural_net.Conv2d(64, 64, kernel_size=2, padding=1)
        self.c3 = neural_net.Conv2d(64, 128, kernel_size=2, stride=2)
        # D
        self.d1 = neural_net.Conv2d(128, 128, kernel_size=1)
        self.d2 = neural_net.Conv2d(128, 128, kernel_size=1)
        self.d3 = neural_net.Conv2d(128, 128, kernel_size=1)
        # Linear
        self.last = neural_net.Linear(128, 1)

    def forward(self, x) -> torch.Tensor:
        """Rectified linear unit function element-wise"""
        # 4x4, 2x2, 1x128
        x = func.relu(self.a1(x))
        x = func.relu(self.a2(x))
        x = func.relu(self.a3(x))

        x = func.relu(self.b1(x))
        x = func.relu(self.b2(x))
        x = func.relu(self.b3(x))

        x = func.relu(self.c1(x))
        x = func.relu(self.c2(x))
        x = func.relu(self.c3(x))

        x = func.relu(self.d1(x))
        x = func.relu(self.d2(x))
        x = func.relu(self.d3(x))

        x = x.view(-1, 128)
        x = self.last(x)

        # And finally, the value output
        return func.tanh(x)


if __name__ == "__main__":
    chess_data = ValueDataset()
    train_loader = torch.utils.data.DataLoader(chess_data, batch_size=256, shuffle=True)
    model = Net()
    optimizer = optim.Adam(model.parameters())
    # Cuda
    model.cuda()
    floss = neural_net.MSELoss()

    model.train()

    for epoch in range(100):
        all_loss = 0
        num_loss = 0
        for batch_idx, (data, target) in enumerate(train_loader):
            # Maybe break this up a bit more later on:
            target = target.unsqueeze(-1)
            data, target = data.to(device), target.to(device)
            data = data.float()
            target = target.float()

            optimizer.zero_grad()
            output = model(data)

            loss = floss(output, target)
            loss.backward()
            optimizer.step()

            all_loss += loss.item()
            num_loss += 1

        print(f"{epoch}: {all_loss / num_loss}")
        torch.save(model.state_dict(), "neural_nets/chess_values.pth")
