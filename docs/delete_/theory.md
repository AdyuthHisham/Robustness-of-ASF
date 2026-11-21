# Chapter 2: Theory

## 2.1.1.
1. Cameras failure modes ... real automotive images. > This para is a pain to read. Currently it feel slike three snippets from three papers pasted here but i just want to know what the failure types are.

## 2.1.x 

The structure I want for the modalities paragraph
1. What is the sensor? How does it work? What is the main function it plays in a MSF. And if possible how much is it relied on in a MSF

Keep the para brief and same size for all three modalities; Also mention how prevalent these sensors are in MSF literature.

## 2.2 

1. Add a note to add images of the sensor positions and other relatable images for both datasets

2. Both 2.2.1 and 2.2.2 should follow this structure:
What modalities and sensors are used. (all of them and not just the three modalities). How many frames of data are available for both dataset. Geographically where is the data gathered from. Data diversity. And all labels available for both dataset.

## 2.3.1 
1. ... pipeline stage at which fusion occurs ... > make the three types into an enum for better readability
2. Remove the second para but if possible sprinkle its data into the first data without breaking the flow of the first para.

## 2.3.2 
1. For the top two classical fusion, show the formulas. The idea is to describe what all fusion types are available and then show the top classical fusion strategies with formulas and then describe the pros and cons of using classical fusion.

## 2.4.x

Structure for models:
What is the model's novelty/describe the model in very brief. Which dataset is it built/tested on and which modalities. What fusion level do they follow. And make a table each with its metrics for each individual model.  Also make a note for mt to add images for each model.

Move 2.4.3.0.1 to methodlogy

## 2.5 
Read/pull all corruption and corruption benchmark papers to support the categories described for the corruptions.

Let me know if any category can not be supported with the available papers.

## 2.5.x 
Structure:
What is this type? What are the common corruptions under this category? Which sensors are affected and which is robust to this corruption type.

## 2.5.7
Read what this section is trying to say and ask me if i want to cut it or not

## 2.6 
1. ... directly relevant since ASF fuses 4D radar. > need to verify that ASF fuses 4D radar based on the input data fed to asf during inference and training

2. 2nd para. Need to verify if ASF uses 4D radar. Models dont usually have availability aware mechanisms. I am doing a deep analysis but I need t find if previous papers have also done the same level as me. Based on the answers of these I might have to rewrite the 2nd para.
