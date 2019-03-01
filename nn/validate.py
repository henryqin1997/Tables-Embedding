import torch.nn as nn
import torch
import torch.optim as optim
import torch.utils.data
import numpy as np
import os
import json
from .load import load_data, load_data_100_sample, load_data_domain_schemas
from .plot import plot_performance

torch.manual_seed(1)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
input_size = 120
hidden_size = 500
num_labels = 3334
num_epochs = 100
batch_size = 50
learning_rate = 0.0001
test_size = 3000


class NeuralNet(nn.Module):
    def __init__(self):
        super(NeuralNet, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, num_labels)
        )

    def forward(self, x):
        out = self.fc(x)
        return out


class TableDataset(torch.utils.data.Dataset):
    def __init__(self, inputs, targets):
        inputs = np.array(inputs)
        targets = np.array(targets)
        assert inputs.shape[0] == targets.shape[0]
        self.inputs = inputs
        self.targets = targets

    def __len__(self):
        return self.inputs.shape[0]

    def __getitem__(self, index):
        return self.inputs[index], self.targets[index]


def compute_accuracy(predicted, correct, no_other=True, other_index=3333):
    assert len(predicted) == len(correct)
    if no_other:
        no_other_index = correct != other_index
        predicted = predicted[no_other_index]
        correct = correct[no_other_index]
        if len(correct) == 0:
            return np.nan

    return (predicted == correct).sum().item() / len(correct)


def main():
    model = NeuralNet().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    if os.path.exists('nn/inputs.csv') and os.path.exists('nn/targets.csv'):
        inputs = np.genfromtxt('nn/inputs.csv', dtype='int64', delimiter=',')
        targets = np.genfromtxt('nn/targets.csv', dtype='int64', delimiter=',')
    else:
        inputs, targets = load_data()
        np.savetxt('nn/inputs.csv', inputs, fmt='%i', delimiter=',')
        np.savetxt('nn/targets.csv', targets, fmt='%i', delimiter=',')

    dataset = TableDataset(inputs, targets)

    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [len(dataset) - test_size, test_size])

    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size,
                                               shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=batch_size,
                                              shuffle=False)

    model.load_state_dict(torch.load('nn/model.pt', map_location=lambda storage, location: storage))
    model.eval()

    print('Testing...')
    running_acc = 0.0
    with torch.no_grad():
        for batch_index, (columns, labels) in enumerate(test_loader):
            columns = columns.float().to(device)
            labels = labels.to(device)
            out = model(columns)
            _, predicted = torch.max(out.data, 1)
            acc = compute_accuracy(predicted, labels)
            acc = running_acc if np.isnan(acc) else acc
            running_acc += (acc - running_acc) / (batch_index + 1)
    print('Accuracy of the network on the test dataset: {:.2f}%'.format(
        100 * running_acc))


if __name__ == "__main__":
    main()
