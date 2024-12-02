import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from tqdm import tqdm

# Define the transforms
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

# Load the MNIST dataset
train_dataset = datasets.MNIST(root='./data', train=True, transform=transform, download=True)
test_dataset = datasets.MNIST(root='./data', train=False, transform=transform, download=True)

train_loader = DataLoader(dataset=train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(dataset=test_dataset, batch_size=64, shuffle=False)

# Feed Forward Neural Network
class FFNN(nn.Module):
    def __init__(self):
        super(FFNN, self).__init__()
        # Define layers
        self.flatten0 = nn.Flatten()
        self.linear0 = nn.Linear(28 * 28, 256)
        self.relu1 = nn.ReLU()
        self.linear1 = nn.Linear(256, 128)
        self.relu2 = nn.ReLU()
        self.linear2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.flatten0(x)
        x = self.linear0(x)
        x = self.relu1(x)
        x = self.linear1(x)
        x = self.relu2(x)
        x = self.linear2(x)
        return x
    
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        # Define layers
        self.conv2d0 = nn.Conv2d(1, 32, 3, stride=1, padding=1)
        self.relu0 = nn.ReLU()
        self.maxpool2d0 = nn.MaxPool2d(2, stride=2)
        self.conv2d1 = nn.Conv2d(32, 64, 3, stride=1, padding=1)
        self.relu1 = nn.ReLU()
        self.maxpool2d1 = nn.MaxPool2d(2, stride=2)
        self.flatten0 = nn.Flatten()
        self.linear0 = nn.Linear(64 * 7 * 7, 128)
        self.relu2 = nn.ReLU()
        self.linear1 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv2d0(x)
        x = self.relu0(x)
        x = self.maxpool2d0(x)
        x = self.conv2d1(x)
        x = self.relu1(x)
        x = self.maxpool2d1(x)
        x = self.flatten0(x)
        x = self.linear0(x)
        x = self.relu2(x)
        x = self.linear1(x)
        return x

def train(model, loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for inputs, labels in loader:
        inputs, labels = inputs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    accuracy = 100 * correct / total
    return running_loss / len(loader), accuracy

def evaluate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for inputs, labels in loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)

            running_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = 100 * correct / total
    return running_loss / len(loader), accuracy

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Instantiate models, loss function, and optimizers
models = {"FFNN": FFNN(), "CNN": CNN(),}
criterion = nn.CrossEntropyLoss()
optimizers = {name: optim.Adam(model.parameters(), lr=0.001) for name, model in models.items()}

# Move models to device
for model in models.values():
    model.to(device)

# Training and evaluation
num_epochs = 3
for name, model in models.items():
    print(f"Training {name}")
    for epoch in tqdm(range(num_epochs), total=num_epochs, desc=f"Training {name}"):
        train_loss, train_acc = train(model, train_loader, criterion, optimizers[name], device)
        test_loss, test_acc = evaluate(model, test_loader, criterion, device)

        print(f"Epoch {epoch+1}/{num_epochs}")
        print(f"Train Loss: {train_loss:.4f}, Train Accuracy: {train_acc:.2f}%")
        print(f"Test Loss: {test_loss:.4f}, Test Accuracy: {test_acc:.2f}%")
    print("=" * 50)

