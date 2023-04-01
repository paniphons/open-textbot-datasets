#Given an array of similar {instruction, input, response} objects, this script identifies the longest/most complete conversation, and extracts each one into its own file.
#The purpose of this script is to extract training data from a huge dump of chatbot logs (in the format of a JSON array containing {instruction, input, response} entries). Because the dump contained multiple records for the same chat session (every time the user sends something, a whole new request is made to the chat backend, including all the chat up to that point as part of the input/context), we wanted to deduplicate this data, and only keep the final/most complete conversation.

#One other change it does is if a standard system prompt is found containing the string "Write XYZ's next reply in a fictional chat between XYZ and You", it will replace You with User.



import json
import argparse
import os
from collections import Counter
from time import sleep
import re

def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data



#If the prompt is the standard Tavern prompt, we replace "between Charname and You" with "between Charname and User".
def replace_You_in_prompt(input):
    pattern = r"next reply in a fictional chat between\s+\w+\s+and\s+You"
    result = re.sub(pattern, lambda match: match.group(0).replace("You", "User"), input)
    replacement_made = (result != input)
    return (replacement_made, result)


#Returns a tuple of (success, character name, your name) from a standard Scale prompt
def extract_names_from_known_prompt1(prompt):
    pattern = r"Write (.+)'s next reply in a fictional chat between \1 and ([^.]+)\."
    names = []

    ret = None
    match = re.search(pattern, prompt)
    if match:
        ret = (True, match.group(1), match.group(2))
    
    return (False, None, None)

#Returns the input's identifiers for the chat participants, but cannot identify who's the character/bot and who's You
#It just returns the top 2 identifiers.
def detect_names_from_input(input):
    lines = input.split('\n')
    names = []
    for line in lines:
        if ':' in line:
            name = line.split(':')[0]
            names.append(name)
    name_counter = Counter(names)
    sorted_convo_names = sorted(name_counter.items(), key=lambda x: x[1], reverse=True)
    for convo_name, count in sorted_convo_names:
        print(f"{convo_name}: {count} times")
    ret = ()
    return sorted_convo_names

#Given an input, attempts to detect the names of the Character and the User
# NOTE: it's not foolproof, and only works for the default Scale prompt.
# Returns a tuple of (Character name, User name)
def detect_names(instruction, input):
    names_from_input = detect_names_from_input(input)

    combined = instruction + input
    if "next reply in a fictional chat" in combined:
        (prompt_character_name, prompt_you_name) = extract_names_from_known_prompt1(combined)
        assert (prompt_character_name in sorted_names) and (prompt_you_name in sorted_names)
        return (prompt_character_name, you_name)
    else:
        print("!!!!!!!New system prompt detected! Notify you-know-who to update this script, and specify the record number written above")
        sleep(3)
        return None

#Given a chat "input" field, gives the first thing the user typed in the chat
def find_first_user_chat(instruction, input, combined):
    start_substring = "user:"
    end_substring = "assistant:"
    start_index = input.find(start_substring)
    end_index = input.find(end_substring, start_index)

    if start_index == -1:
        print("WARNING: could not find user chat in input: ", input)
        user_chat = ""
    else:
        #we found the user's input. we decide how far to read ahead based on whether we find a reply
        if end_index == -1:
            user_chat = input[start_index + len(start_substring):(start_index + 300)]
        else:
            user_chat = input[(start_index + len(start_substring)):end_index]
        
    return user_chat


#Used to discard partial entries of the same chat session
def find_most_complete_transcript(transcripts):
    complete_transcript = {}
    counter = 1
    for transcript in transcripts:
        print("Processing record", counter)
        counter += 1
        instruction = transcript["instruction"]
        input = transcript["input"]
        combined = instruction + input
        # To identify a conversation, we use the first 50 characters as a key for comparison (covers character name),
        # as well as the first thing a user types. This is not a perfect solution but it should work in most cases.
        first_user_chat = find_first_user_chat(instruction, input, combined)
        key = input[:50] + first_user_chat
        #print("Using key:", key)
        if key not in complete_transcript:
            complete_transcript[key] = transcript
        elif len(input) > len(complete_transcript[key]["input"]):
            complete_transcript[key] = transcript
    return list(complete_transcript.values())


#For now we just replace You in the prompt, if found
def apply_post_processing(transcripts):
    retouched_transcripts = []
    counter = 0
    for transcript in transcripts:
        counter += 1
        print("Applying post-processing to extracted convo #", counter)

        instruction = transcript["instruction"]
        input = transcript["input"]
        response = transcript["response"]

        #Replace You with User
        change_made_in_instruction, new_instruction = replace_You_in_prompt(transcript["instruction"])
        if change_made_in_instruction:
            instruction = new_instruction
        else:
            change_made_in_input, new_input = replace_You_in_prompt(transcript["input"])
            if change_made_in_input:
                input = new_input
            else:
                print("WARNING: did not find expected system prompt in this record! Tell your developer the filename and record number. Pausing briefly.")
                sleep(3)

        #Replace "assistant:" entries with the character's name
        character_name = None
        prompt_found, character_name_1, _ = extract_names_from_known_prompt1(instruction)
        if prompt_found:
            character_name = character_name_1
        else:
            prompt_found, character_name_2, _ = extract_names_from_known_prompt1(input)
            if prompt_found:
                character_name = character_name_2
        if character_name:
            count = input.count("\nassistant:")
            input = input.replace("\nassistant:", "\n" + character_name + ":")
            if count > 0:
                print(count,"instances of 'assistant' replaced with", character_name)

        transcript["instruction"] = instruction
        transcript["input"] = input
        transcript["response"] = response

        retouched_transcripts.append(transcript)

    return retouched_transcripts

def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

if __name__ == "__main__":

    print("Running in,", os.path.dirname(os.path.realpath(__file__)))

    # parser = argparse.ArgumentParser(description='The JSON array containing your chatlogs.')
    # parser.add_argument('input_file', type=str, help='Path to the input file.')
    # args = parser.parse_args()
    # input_file = args.input_file
    input_file = "./kuru.json"

    input_file_name, ext = os.path.splitext(input_file)

    print ("Processing", input_file)
    transcripts = load_json(input_file)
    complete_transcripts = find_most_complete_transcript(transcripts)
    print("Discarded", (len(transcripts) - len(complete_transcripts)), "partial transcripts")
    retouched_transcripts = apply_post_processing(complete_transcripts)


    counter = 0
    for retouched_transcript in retouched_transcripts:
        counter += 1
        output_file = input_file_name + '.convo.' + str(counter) + ext
        save_json(output_file, retouched_transcript)
        print("Saved to", output_file)

    print ("Done processing", input_file, "\n==============")
