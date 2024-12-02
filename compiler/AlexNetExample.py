import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from tqdm import tqdm

# Load CIFAR-10 Dataset
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize CIFAR-10 images to 224x224 for AlexNet
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),  # Normalize to [-1, 1]
])

train_dataset = datasets.CIFAR10(root='./data', train=True, transform=transform, download=True)
test_dataset = datasets.CIFAR10(root='./data', train=False, transform=transform, download=True)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers=2)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False, num_workers=2)

class AlexNet(nn.Module):
    def __init__(self):
        super(AlexNet, self).__init__()
        # Define layers
        self.conv2d0 = nn.Conv2d(3, 64, 11, stride=4, padding=2)
        self.relu0 = nn.ReLU()
        self.maxpool2d0 = nn.MaxPool2d(3, stride=2)
        self.conv2d1 = nn.Conv2d(64, 192, 5, padding=2)
        self.relu1 = nn.ReLU()
        self.maxpool2d1 = nn.MaxPool2d(3, stride=2)
        self.conv2d2 = nn.Conv2d(192, 384, 3, padding=1)
        self.relu2 = nn.ReLU()
        self.conv2d3 = nn.Conv2d(384, 256, 3, padding=1)
        self.relu3 = nn.ReLU()
        self.conv2d4 = nn.Conv2d(256, 256, 3, padding=1)
        self.relu4 = nn.ReLU()
        self.maxpool2d2 = nn.MaxPool2d(3, stride=2)
        self.flatten0 = nn.Flatten()
        self.dropout0 = nn.Dropout(p=0.5)
        self.linear0 = nn.Linear(256 * 6 * 6, 4096)
        self.relu5 = nn.ReLU()
        self.dropout0 = nn.Dropout(p=0.5)
        self.linear1 = nn.Linear(4096, 4096)
        self.relu6 = nn.ReLU()
        self.linear2 = nn.Linear(4096, 10)

    def forward(self, x):
        x = self.conv2d0(x)
        x = self.relu0(x)
        x = self.maxpool2d0(x)
        x = self.conv2d1(x)
        x = self.relu1(x)
        x = self.maxpool2d1(x)
        x = self.conv2d2(x)
        x = self.relu2(x)
        x = self.conv2d3(x)
        x = self.relu3(x)
        x = self.conv2d4(x)
        x = self.relu4(x)
        x = self.maxpool2d2(x)
        x = self.flatten0(x)
        x = self.dropout0(x)
        x = self.linear0(x)
        x = self.relu5(x)
        x = self.dropout0(x)
        x = self.linear1(x)
        x = self.relu6(x)
        x = self.linear2(x)
        return x


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = AlexNet().to(device)

# Define Loss and Optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training Loop
def train(model, loader, criterion, optimizer, device):
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for images, labels in tqdm(loader, total=len(loader), desc="Training"):
        images, labels = images.to(device), labels.to(device)

        # Forward pass
        outputs = model(images)
        loss = criterion(outputs, labels)

        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    return total_loss / len(loader), 100.0 * correct / total

# Testing Loop
def test(model, loader, criterion, device):
    model.eval()
    total_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

    return total_loss / len(loader), 100.0 * correct / total

# Train and Test the Model
epochs = 5
for epoch in range(1, epochs + 1):
    train_loss, train_acc = train(model, train_loader, criterion, optimizer, device)
    test_loss, test_acc = test(model, test_loader, criterion, device)

    print(f"Epoch {epoch}/{epochs}:")
    print(f"  Train Loss: {train_loss:.4f}, Train Accuracy: {train_acc:.2f}%")
    print(f"  Test Loss: {test_loss:.4f}, Test Accuracy: {test_acc:.2f}%")
