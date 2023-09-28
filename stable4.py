from stegano import lsb
from os.path import isfile,join
import cv2
import math
import os
import shutil
from subprocess import call,STDOUT
from PIL import Image
import numpy as np


def natural_sort_key(s):
    """Key function for natural sorting (sort by numerical order)."""
    import re
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]




def split_string(s_str,count=10):
    per_c=math.ceil(len(s_str)/count)
    c_cout=0
    out_str=''
    split_list=[]
    for s in s_str:
        out_str+=s
        c_cout+=1
        if c_cout == per_c:
            split_list.append(out_str)
            out_str=''
            c_cout=0
    if c_cout!=0:
        split_list.append(out_str)
    return split_list

# Extract each image frame from input video and saves as PNG image in tmp directory.
def frame_extraction(video):
    if not os.path.exists("./tmp"):
        os.makedirs("tmp")
    temp_folder = "./tmp"
    print("[INFO] tmp directory is created")

    vidcap = cv2.VideoCapture(video)
    count = 0

    while True:
        success, image = vidcap.read()
        if not success:
            break
        filename = os.path.join(temp_folder, "{:d}.png".format(count))
        cv2.imwrite(filename, image)
        print("Saved frame:", filename)  # Print the name of the saved PNG image
        count += 1


def encode_all_frames(folderpath, inputstring):
    # Specify the path to the "tmp" folder
    folder_path = folderpath  # You can adjust this path as needed

     # Get the directory of the script
    script_directory = os.path.dirname(__file__)

    # Check if the folder exists
    if os.path.exists(folder_path):

        # Create a new folder for encoded images in the script's directory
        encoded_folder = os.path.join(script_directory, "encoded")
        if not os.path.exists(encoded_folder):
            os.makedirs(encoded_folder)


        # Split the input text into individual characters
        characters = list(inputstring)

        # List all files in the folder
        files = os.listdir(folder_path)

        # Filter out unwanted filenames like .DS_store
        filtered_files = [filename for filename in files if not filename.startswith(".")]

        # Sort the filtered list of filenames by numerical order
        sorted_files = sorted(filtered_files, key=natural_sort_key)

        # Iterate through the sorted list of filenames and characters
        for filename, char in zip(sorted_files, characters):
            imagepath = os.path.join(folder_path, filename)  # Joins the sorted filenames with its full path
            encoded_imagepath = os.path.join(encoded_folder, f"{filename[:-4]}_e.png")  # New encoded image path with "e" added

            encode_with_opencv(imagepath, char, encoded_imagepath, 8)  # Encode the character and save to the new frame
            print(f"Encoding.. File: {imagepath}, Character: {char}")

        for filename in sorted_files[len(characters):]:
            imagepath = os.path.join(folder_path, filename)
            base_filename, file_extension = os.path.splitext(filename)
            encoded_imagepath = os.path.join(encoded_folder, f"{base_filename}_e{file_extension}")
            os.rename(imagepath, encoded_imagepath)
            print(f"Moving.. File: {imagepath} to {encoded_imagepath}")

        # # Move the remaining frames to the encoded folder
        # for filename in sorted_files[len(characters):]:
        #     imagepath = os.path.join(folder_path, filename)
        #     encoded_imagepath = os.path.join(encoded_folder, filename)
        #     os.rename(imagepath, encoded_imagepath)
        #     print(f"Moving.. File: {imagepath} to {encoded_imagepath}")

        print("Encoding and Moving Done!")


    else:
        print("The 'tmp' folder does not exist.")


def create_video_from_frames(input_folder, output_filename):
    frame_files = os.listdir(input_folder)
    frame_files = [f for f in frame_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    frame_files.sort(key=natural_sort_key)
    
    frames = []
    for frame_file in frame_files:
        frame_path = os.path.join(input_folder, frame_file)
        frame = cv2.imread(frame_path)
        frames.append(frame)
        print("appending frame ", frame_file)
    
    height, width, layers = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_filename, fourcc, 20.0, (width, height))
    
    for frame in frames:
        out.write(frame)
    
    out.release()


def split_encodedvideo_to_frames(video_path, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Initialize the frame count to 0
    frame_count = 0

    # Loop through the video frames
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Remove the leading zeros from the frame count
        frame_count_without_leading_zeros = str(frame_count).lstrip('0')

        # Save the frame as an image in the output folder
        frame_filename = os.path.join(output_folder, f"{frame_count_without_leading_zeros}.png")
        print("extracting frame:", frame_filename)
        cv2.imwrite(frame_filename, frame)

        frame_count += 1

    # Release the video capture object
    cap.release()

    print(f"Split {frame_count} frames from the video.")

def decode_all_frames(folderpath):
    print("Decoding Started")

    decodetextlist = [] #list to store letters that are decoded
    # Specify the path to the "tmp" folder
    folder_path = folderpath # You can adjust this path as needed

   # Check if the folder exists
    if os.path.exists(folder_path):
            
        # List all files in the folder
        files = os.listdir(folder_path)
        #print(files)
        
         # Filter out unwanted filenames like .DS_store
        filtered_files = [filename for filename in files if not filename.startswith(".")]

        # Sort the filtered list of filenames by numerical order
        sorted_files = sorted(filtered_files, key=natural_sort_key)

         # Iterate through the sorted list of filenames 
        for filename in sorted_files:
            #print(filename)
            imagepath = os.path.join(folder_path, filename) #joins the sorted filenames with its full path
            # decodetext = decode_with_opencv(imagepath,8) # encodes the image in the path previously joined
            # print("Decoding.. File:",imagepath, "Decoded Text: ", decodetext)
            # decodetextlist.append(decodetext)

            decodetext = decode_with_opencv(imagepath, 8)  # Attempt to decode the image
            

            if decodetext == 0:
                print("All Encoded Files Decoded")
                break
                
            else:
                print("Decoding.. File:", imagepath, "Decoded Text: ", decodetext)
                decodetextlist.append(decodetext)
                continue
    
        full_decoded_message = "".join(decodetextlist)
        print("Decoding Done! Decoded Text:", full_decoded_message) #show decoded text after all decode has been done for all files, decoded text is the same for all frames 
        

    else:
        print("The 'tmp' folder does not exist.")

def decodes_all_frames(encoded_folderpath):
    print("decoding started")
    """
    Decode all encoded frames in a folder.

    Args:
        encoded_folderpath: The path to the folder containing encoded frames.

    Returns:
        A list of decoded frames.
    """

    # List all files in the folder
    files = os.listdir(encoded_folderpath)

    # Filter out unwanted filenames like .DS_store
    filtered_files = [filename for filename in files if not filename.startswith(".")]

    # Sort the filtered list of filenames by numerical order
    sorted_files = sorted(filtered_files, key=natural_sort_key)

    # Decode each frame and append it to the list of decoded frames
    decoded_frames = []
    for filename in sorted_files:
        print(filename)
        encoded_imagepath = os.path.join(encoded_folderpath, filename)
        decoded_frame = decode_with_opencv(encoded_imagepath, 8)
        decoded_frames.append(decoded_frame)
        print("decoding frame:", filename)

    return decoded_frames     
        

# Function to convert data to 8 bit binary format 
def to_bin(data):
    if isinstance(data, str):
        return ''.join([format(ord(i), "08b") for i in data])  
    elif isinstance(data, bytes) or isinstance(data, np.ndarray):
        return [(format(i, "08b")) for i in data]  
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b") 
    else:
        raise TypeError("Type not supported.")


# Function to encode data into an image
def encode(image_name, secret_data,lsb):
        
    image = cv2.imread(image_name)  # Read the image with cv2
    
    n_bytes = (image.shape[0] * image.shape[1] * 3 // 8)*lsb  # Calculate the maximum number of bytes that can be encoded in the image

    secret_data += "====="  # Add a null terminator 

    if len(secret_data) > n_bytes:
        raise ValueError("[!] Insufficient bytes, need bigger image or less data")  # Check if there is enough space for encoding
    
    binary_secret_data = to_bin(secret_data)  # Convert the secret data to binary

    secret_index = 0 # pointer for bits of secret text added

    #this is to add padding to front of data.
    #padding is needed so that it will be able to replace the n lsb nicely (say 3 lsb, left with last 2. will return error)
    if(len(binary_secret_data)%lsb!=0):
        add= "0" * (len(binary_secret_data)%lsb)
        binary_secret_data = add + binary_secret_data

    data_len = len(binary_secret_data)  # Get the size of data to hide

    #encode data into img r, g, b. may change later so that it fills 1 channel before 
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            pixel = image[i, j]  # Get the pixel at the current position
            r, g, b = to_bin(pixel)  # Convert RGB values of the pixel to binary format
            if secret_index < data_len:
                pixel[0] = int(r[:-(lsb)] + binary_secret_data[secret_index:secret_index+lsb], 2)  # Encode data into the Red channel LSB
                secret_index += (lsb)
            if secret_index < data_len:
                pixel[1] = int(g[:-(lsb)] + binary_secret_data[secret_index:secret_index+lsb], 2)  # Encode data into the Green channel LSB
                secret_index +=(lsb)
            if secret_index < data_len:
                pixel[2] = int(b[:-(lsb)] + binary_secret_data[secret_index:secret_index+lsb], 2)  # Encode data into the Blue channel LSB
                secret_index +=(lsb)

            if secret_index >= data_len:
                break
        if secret_index >= data_len:
            break
    return image


# Function to encode text into an image using OpenCV
def encode_with_opencv(image_path, text, output_path,lsb):
    encoded_image = encode(image_path, text,lsb)  # Encode the text into the image
    cv2.imwrite(output_path, encoded_image)  # Save the encoded image to the specified path

# Function to decode data from an image
def decode(image_name, lsb):
    lsb = int(lsb)
    modlsb = 8 % lsb
    last = "0" * modlsb

    nullt = to_bin("=====")

    
    # Read the image
    image = cv2.imread(image_name)
    binary_data = ""
    counter = 0
    errorstate = False

    # Check for the error state and break out of the loop if it is set
    if errorstate:
        return None

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            pixel = image[i, j]  # Get the pixel at the current position
            r, g, b = to_bin(pixel)  # Convert RGB values of the pixel to binary format
            binary_data += r[-lsb:]  # Extract the LSB of Red channel and add to binary_data
            counter += lsb
            binary_data += g[-lsb:]  # Extract the LSB of Green channel and add to binary_data
            counter += lsb
            binary_data += b[-lsb:]  # Extract the LSB of Blue channel and add to binary_data
            counter += lsb

            # Check for the terminator and break out of the loop if it is found
            if nullt in binary_data:
                break
        else:
            errorstate = True
            break

    # If the terminator was not found, return None
    if errorstate:
        return 0

    # Otherwise, continue with the decoding process

    # Remove padding from the front, add padding back to the back so that it can be split into 8-bit chunks properly
    binary_data = binary_data[modlsb:]
    binary_data = binary_data + last

    all_bytes = [binary_data[i: i + 8] for i in range(0, len(binary_data), 8)]  # Split binary into 8-bit chunks
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))  # Convert each 8-bit chunk to a character
        if decoded_data[-5:] == "=====":
            break

    return decoded_data[:-5]

# Function to decode text from an image using OpenCV
def decode_with_opencv(image_path,lsb):
    #decoded_text = decode(image_path,lsb)  # Decode the text from the image

    decoded_text = decode(image_path, lsb)  # Attempt to decode the text from the image
    if decoded_text == 0:
        return 0
    else:
        return decoded_text
   

    
        

    

    # if decoded_text == 0:
    #     return 0
    # else:
    #     return decoded_text


def clean_encoded(path="./encoded"):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("[INFO] encoded files are cleaned up")

def clean_tmp(path="./tmp"):
    if os.path.exists(path):
        shutil.rmtree(path)
        print("[INFO] tmp files are cleaned up")

def main():
    
    #user input video file name
    f_name=input("Enter video file name WITH extension.\n")

    # Extract image frames from input video
    frame_extraction(f_name)

    #user input payload
    input_string = input("Enter the input string :")
    input_string = "Cyber" + input_string

    #encode all frames
    encode_all_frames("./tmp",input_string)

    #reconstruct video
    create_video_from_frames("./encoded", "encoded_video.mp4")
    print("Video Created: encoded_video.mp4")

    #clean tmp and encoded folder
    # clean_tmp()
    # clean_encoded()

if __name__ == "__main__":
    while True:
        print("Selection option number:\n 1.Hide a message in video\n 2.Reveal the secret from video")
        choice = input()
        if choice == '1':
            main()
        elif choice == '2':
            #user input video file name
            vid_name=input("Enter video file name WITH extension.\n")

            # Extract image frames from input video
            split_encodedvideo_to_frames(vid_name,"./encodedvid")
            decode_all_frames("./encodedvid")

        else:
            break
