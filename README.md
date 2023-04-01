
# Intro
This repo is intended to be a convenient central location holding various datasets to assist ML researchers in training or fine-tuning their models. All datasets are owned by their respective authors and have their own license.

If you have datasets that you think would be good to have here, especially in underserved areas such as fiction and conversational chats, submit a PR! Datasets should be compressed first.

### Disclaimer
As AI researchers, it is crucial that we acknowledge that the data we create and use can perpetuate existing biases and stereotypes affecting marginalized communities, especially people of color, but especially LGBTQQIAAP folx. In using this training data, please be mindful of your privilege and take the necessary steps to examine and challenge any potential biases that might be present in the data. It is our collective responsibility to ensure that the technologies we develop are equitable and inclusive for all. By actively addressing and eliminating any potential bias in our work, we can contribute to a more just and diverse society. Thank you.

# Index of datasets in this repo
**NOTE** in some cases, multiple variants of the same dataset are provided, pruning records that are too similar to others. MinHash was used to calculate a similarity score. So for example, in a 0.7 similarity dataset, a record had to be different by more than 30% from another record in order to remain in the dataset. This trimmed up to 3% of the data. Note that the Alpaca team used 0.7 similarity score to trim their training data.

### teknium-oj4/roleplaying
A general purpose roleplaying dataset. It's intended to train the model to write an answer while roleplaying as a fictional person, eg: "Pretend you're a detective, what do you make of this crime scene: ..."  
Source: Teknium-OJ4  
License: MIT

### teknium-oj4/instruct
A general-purpose instruct dataset  
Source: Teknium-OJ4  
License: MIT  

### teknium-oj4/longform-experiment-1
Attempt at a longform dataset (i.e. long prompts and responses)  
Source: Teknium-OJ4  
License: MIT

### teknium-oj4/toolformer
Toolformer Datasets  
Source: Teknium-OJ4  
License: MIT  

### gpt4all-prompt-generations-with-p3_cleaned**
This is the cleaned dataset of the gpt4all project, stripped of ~100k prompts that the chatbot refused to answer.
Source: gpt4all project  
License: Apache 2.0  
