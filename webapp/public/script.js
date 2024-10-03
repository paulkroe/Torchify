const sectionsContainer = document.getElementById('sections-container');
const addSectionButton = document.getElementById('add-section');
let sectionCount = 0;

// Define the options for the dropdown in a data structure
const dropdownOptions = [
  "Linear",
  "Softmax",
  "ReLU",
  "Batch Norm",
  "Dropout"
];

// Function to create a section with a remove button, editable title, and dropdown
function createSectionElement(layerText) {
  const sectionContainer = document.createElement('div');
  sectionContainer.classList.add('section-container');
  
  const newSection = document.createElement('div');
  newSection.classList.add('section');
  
  // Create remove button
  const removeButton = document.createElement('button');
  removeButton.classList.add('remove-section');
  removeButton.textContent = '-';
  
  removeButton.addEventListener('click', () => {
    sectionsContainer.removeChild(sectionContainer);
  });

  // Create layer title (click to edit)
  const layerTitle = document.createElement('span');
  layerTitle.classList.add('layer-title');
  layerTitle.textContent = layerText;

  // Allow title editing on click
  layerTitle.addEventListener('click', () => {
    const input = document.createElement('input');
    input.value = layerTitle.textContent;
    
    newSection.replaceChild(input, layerTitle);

    // When user presses enter or loses focus, change title
    input.addEventListener('blur', () => {
      layerTitle.textContent = input.value;
      newSection.replaceChild(layerTitle, input);
    });

    input.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        layerTitle.textContent = input.value;
        newSection.replaceChild(layerTitle, input);
      }
    });

    input.focus();
  });

  // Create dropdown
  const dropdown = document.createElement('select');
  dropdown.classList.add('dropdown');
  
  // Dynamically add options from the data structure
  dropdownOptions.forEach(optionText => {
    const option = document.createElement('option');
    option.value = optionText;
    option.textContent = optionText;
    dropdown.appendChild(option);
  });

  // Create input fields for "Linear" option
  const inputsContainer = document.createElement('div');
  inputsContainer.classList.add('inputs-container');

  const dimInLabel = document.createElement('label');
  dimInLabel.textContent = "DIM IN";

  const dimInInput = document.createElement('input');
  dimInInput.type = "text";

  const dimOutLabel = document.createElement('label');
  dimOutLabel.textContent = "DIM OUT";

  const dimOutInput = document.createElement('input');
  dimOutInput.type = "text";

  inputsContainer.appendChild(dimInLabel);
  inputsContainer.appendChild(dimInInput);
  inputsContainer.appendChild(dimOutLabel);
  inputsContainer.appendChild(dimOutInput);

  // Ensure inputs are hidden initially
  inputsContainer.style.display = 'none';

  // Show/hide inputs based on dropdown selection
  dropdown.addEventListener('change', (event) => {
    if (event.target.value === 'Linear') {
      inputsContainer.style.display = 'flex'; // Show inputs when "Linear" is selected
    } else {
      inputsContainer.style.display = 'none';  // Hide inputs for other options
    }
  });

  // Check the initial value of the dropdown and show inputs if it's "Linear"
  if (dropdown.value === 'Linear') {
    inputsContainer.style.display = 'flex';
  }

  // Append remove button, dropdown, and inputs to section
  newSection.appendChild(removeButton);
  newSection.appendChild(layerTitle);
  newSection.appendChild(dropdown);
  newSection.appendChild(inputsContainer);

  // Create and append the add-between button to the left of the section
  const addBetweenButton = document.createElement('button');
  addBetweenButton.classList.add('add-between');
  addBetweenButton.textContent = '+';

  addBetweenButton.addEventListener('click', () => {
    sectionCount++;
    const newSection = createSectionElement(`Layer ${sectionCount}`);
    
    // Insert the new section after the clicked add button
    sectionsContainer.insertBefore(newSection, sectionContainer.nextSibling);
  });

  sectionContainer.appendChild(addBetweenButton);
  sectionContainer.appendChild(newSection);
  
  return sectionContainer;
}

addSectionButton.addEventListener('click', () => {
  sectionCount++;
  const newSection = createSectionElement(`Layer ${sectionCount}`);
  sectionsContainer.appendChild(newSection);
});
