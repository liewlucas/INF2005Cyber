import streamlit as st
import cv2
import numpy as np
from PIL import Image
import wave
import tempfile
import os
import subprocess
from subprocess import call,STDOUT

# Allow file types: JPG, MP3, MP4, MOV
valid_extensions = ["jpg", "jpeg", "mp4","png", "wav","gif"]

def natural_sort_key(s):
    """Key function for natural sorting (sort by numerical order)."""
    import re
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

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

# Function to check if the file extension is allowed
def is_valid_file_extension(file_name, valid_extensions):
    file_extension = file_name.split(".")[-1]
    return file_extension.lower() in valid_extensions

# Extract each image frame from input video and saves as PNG image in tmp directory.
def frame_extraction(cover_object, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"[INFO] Directory '{output_folder}' is created")
    
    if cover_object:
        # Create a temporal file
        with tempfile.NamedTemporaryFile() as temp_file:
            # Write the SGY to the temporal file
            temp_file.write(cover_object.getbuffer())
            print(cover_object)
            # Now you can use the temporal file path
            vidcap = cv2.VideoCapture(temp_file.name)
    
    count = 0

    while True:
        success, image = vidcap.read()
        if not success:
            break
        filename = os.path.join(output_folder, "{:d}.png".format(count))
        cv2.imwrite(filename, image)
        print("Saved frame:", filename)  # Print the name of the saved PNG image
        count += 1

def encode_all_frames(folderpath, inputstring, lsb):
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

            encode_image(imagepath,encoded_imagepath, char , lsb)  # Encode the character and save to the new frame
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

def create_video_from_frames(input_folder, output_filename):
    # frame_files = os.listdir(input_folder)
    # frame_files = [f for f in frame_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    # frame_files.sort(key=natural_sort_key)

    # command = ['ffmpeg', '-i', input_folder + '/%d_e.png', '-c:v', 'huffyuv', '-crf', '0', output_filename]
    # subprocess.run(command)

    # # Extract audio from input video
    # call(["ffmpeg", "-i", name, "-q:a", "0", "-map", "a", "tmp1/audio.mp3", "-y"], stdout=open(os.devnull, "w"), stderr=STDOUT)
    
    # # Encode text into image frames
    # # encode_string(input_string)
    # call(["ffmpeg", "-i", input_folder + "%d_e.png" , "-vcodec", "png", "tmp1/video.mov", "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
    
    # # Combine video and audio back together 
    # call(["ffmpeg", "-i", "tmp1/video.mov", "-i", "tmp1/audio.mp3", "-codec", "copy", output_filename, "-y"],stdout=open(os.devnull, "w"), stderr=STDOUT)
    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"Input folder '{input_folder}' does not exist.")
        return
    
    # Find all image files in the input folder and sort them by name
    image_files = sorted([f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))])

    # Check if there are any image files in the folder
    if not image_files:
        print(f"No image files found in '{input_folder}'.")
        return

    # Create a list of image file paths with consecutive numbers
    image_paths = [os.path.join(input_folder, f) for f in image_files]

    # Construct the ffmpeg command to create an MP4 video
    command = [
        "ffmpeg",
        "-framerate", "60",  # Adjust the framerate as needed
        "-i", os.path.join(input_folder, "%d_e.png"),  # Input image pattern
        "-c:v", "libx264",    # Video codec
        "-pix_fmt", "yuv420p",  # Pixel format
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",  # Ensure even width and height
        "-r", "30",            # Output frame rate (same as input)
        "-y",                  # Overwrite output file if it exists
        output_filename        # Output file name
    ]

    # Execute the ffmpeg command
    subprocess.run(command)

    print(f"Video '{output_filename}' created successfully.")

# Function to encode data
def encode_get_input():
    output_object = 'sample copy.png'
    output_audio = 'sampleStego.wav'
    st.header('Upload an image/audio/video as cover object and a TEXT payload.')

    cover_object = st.file_uploader("Upload cover object", type=valid_extensions)
    if cover_object is not None:
        print(cover_object.type) # Testing code

        # Check if the uploaded file has a valid extension
        if is_valid_file_extension(cover_object.name, valid_extensions):
            st.success(f"File '{cover_object.name}' successfully uploaded!")
        else:
            st.error("Invalid file type! Please upload a JPG, wav, or MP4 file.")

    payload_input = st.text_input("Enter payload text:")
    lsb_value = st.slider("No. of LSB Cover Object Bits Selected", min_value=1, max_value=8)

    if cover_object is not None and payload_input:
        if st.button("Encode"):
            try:
                # Display of Input Cover Object and Payload
                st.header('Input:')
                if cover_object.type in ['audio/mpeg','audio/x-wav']:
                    st.audio(cover_object, format=cover_object.type)
                    output_audio = encode_audio(lsb_value, payload_input, cover_object)
                    st.header('Output:')
                    st.audio(output_audio, format=cover_object.type)
                elif cover_object.type.startswith('image'):
                    st.image(cover_object, use_column_width=True)
                    encode_image(cover_object, output_object, payload_input, lsb_value)
                    st.header('Output:')
                    st.image(output_object, use_column_width=True)
                elif cover_object.type in ['video/QuickTime', 'video/mp4']:
                    st.video(cover_object, format=cover_object.type)
                    # frame_extraction(cover_object, './tmp')
                    # encode_all_frames("./tmp",payload_input, lsb_value)
                    create_video_from_frames("./encoded", "encoded_video1.mp4",)
                # st.write(f"Input payload: {payload_input}")
                # print(cover_object) Test code

                
            except Exception as e:
                st.error(f"An error occured: {e}")
                
    else:
        st.warning("Please provide Cover Object and Payload.")
    return output_object


# Function to encode data into an image
def encode_image(cover_object, output, secret_data, lsb):
    print(type(cover_object))
    if (type(cover_object) == str):
        image = cv2.imread(cover_object)
    else:
        file_bytes = np.asarray(bytearray(cover_object.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
    # print(image.shape) Test code
    # Calculate the maximum number of bytes that can be encoded in the image
    n_bytes = (image.shape[0] * image.shape[1] * 3 // 8)*lsb

    secret_data += "====="  # Add a null terminator

    # Convert the secret data to binary
    binary_secret_data = to_bin(secret_data)

    # print((len(str(binary_secret_data)))) # Test code
    # print((n_bytes)) # Test code
    if len(str(binary_secret_data)) > n_bytes:  
        # Check if there is enough space for encoding
        raise ValueError(
            "[!] Insufficient bytes, need bigger image or less data")

    

    # this is to add padding to front of data.
    # padding is needed so that it will be able to replace the n lsb nicely (say 3 lsb, left with last 2. will return error)
    if (len(binary_secret_data) % lsb != 0):
        add = "0" * (lsb-len(binary_secret_data) % lsb)
        binary_secret_data = binary_secret_data + add

    data_len = len(binary_secret_data)  # Get the size of data to hide

    status = 0
    secret_index = 0  # pointer for bits of secret text added
    # encode data into img r, g, b. may change later so that it fills 1 channel before
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            pixel = image[i, j]  # Get the pixel at the current position
            # Convert RGB values of the pixel to binary format
            r, g, b = to_bin(pixel)
            if secret_index < data_len:
                # Encode data into the Red channel LSB
                pixel[0] = int(
                    r[:-(lsb)] + binary_secret_data[secret_index:secret_index+lsb], 2)
                secret_index += (lsb)
        if secret_index >= data_len:
            status = 1
            break
        if secret_index >= data_len:
            status = 1
            break
    # if msg havent encode finish, move to g channel
    if status != 1:
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                pixel = image[i, j]  # Get the pixel at the current position
                # Convert RGB values of the pixel to binary format
                r, g, b = to_bin(pixel)
                if secret_index < data_len:
                    # Encode data into the Red channel LSB
                    pixel[1] = int(
                        g[:-(lsb)] + binary_secret_data[secret_index:secret_index+lsb], 2)
                    secret_index += (lsb)
                if secret_index >= data_len:
                    status = 1
                    break
            if secret_index >= data_len:
                status = 1
                break

    # if msg havent encode finish, move to b channel
    if status != 1:
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                pixel = image[i, j]  # Get the pixel at the current position
                # Convert RGB values of the pixel to binary format
                r, g, b = to_bin(pixel)
                if secret_index < data_len:
                    # Encode data into the Blue channel LSB
                    pixel[2] = int(
                        b[:-(lsb)] + binary_secret_data[secret_index:secret_index+lsb], 2)
                    secret_index += (lsb)
                if secret_index >= data_len:
                    status = 1
                    break
            if secret_index >= data_len:
                status = 1
                break
    if status != 1:
        print("Image not large enough to encode")  # should never happen
    cv2.imwrite(output, image)
    return

# Function to encade data into an audio
def encode_audio(n, payload, cover_object):
    print("\nEncoding Starts..")

    if cover_object:
    
        # Create a temporal file
        with tempfile.NamedTemporaryFile() as temp_file:
            # Write the SGY to the temporal file
            temp_file.write(cover_object.getbuffer())
            
            # Now you can use the temporal file path
            audio = wave.open(temp_file.name, mode="rb")

    # print(audio) Test code


    # Convert audio into bytes
    frame_bytes = list(audio.readframes(audio.getnframes()))

    # Initialize an empty string to store the binary representation
    binary_list = []

    # Convert all bytes of audio into binary
    for byte in frame_bytes:
        binary_value = bin(byte)[2:].zfill(8)
        binary_list.append(binary_value)
    terminator = "=====" 
    payload += terminator # Add a null terminator

    # Convert payload and delimiter to binary
    binary_payload = ''.join(format(ord(char), '08b') for char in payload)

    print(len(str(binary_payload))) # Test code
    print(((len(binary_list)*n))) # Test code
    if len(str(binary_payload)) > (len(binary_list)*n):  
        # Check if there is enough space for encoding
        raise ValueError(
            "[!] Insufficient bytes, need bigger image or less data")
    
    # Check if padding is needed
    if len(binary_payload) % n != 0:
        # Calculate the number of padding bits needed
        padding_length = n - (len(binary_payload) % n)
        binary_payload += "0" * padding_length  # Padding with zeros


    # Initialize an empty list to store the binary chunks
    binary_chunks = []

    # Iterate through the binary string in chunks of size 'n' for n LSBs
    for i in range(0, len(binary_payload), n):
        chunk = binary_payload[i:i + n]
        binary_chunks.append(chunk)

    mod_binary_list = []


    # Replace n LSBs of audio bytes with payload bits
    for i, n_bits in enumerate(binary_chunks):
        # Extract the current binary byte from the audio
        audio_byte = binary_list[i]

        # Replace the last n bits of the audio byte with n_bits
        new_audio_byte = audio_byte[:-n] + n_bits

        # Update the binary_list with the modified audio byte
        mod_binary_list.append(new_audio_byte)

    final_binary_list = []

    final_binary_list.extend(mod_binary_list)

    # Add the remaining audio bytes
    final_binary_list.extend(binary_list[len(mod_binary_list):])


    # Initialize an empty bytearray to store the reconstructed frame bytes
    frame_modified = []

    # Iterate through binary strings and convert to bytes
    for binary_string in final_binary_list:
        # Convert the binary string to an integer
        decimal_value = int(binary_string, 2)

        # Append the integer value as a byte to the bytearray
        frame_modified.append(decimal_value)


    frame_mod_bytes = bytes(frame_modified)


    # Write the modified audio to a new file
    with wave.open('sampleStego.wav', 'wb') as new_audio:
        new_audio.setparams(audio.getparams())
        new_audio.writeframes(frame_mod_bytes)

    print("Successfully encoded inside sampleStego.wav")
    return 'sampleStego.wav'

# Function to decode data
def decode_get_input():
    st.header('Upload an image/audio/video as Stego Object.')
    stego_object = st.file_uploader("Upload stego object", type=valid_extensions)
    if stego_object is not None:
        print(stego_object.type) # Testing code

        # Check if the uploaded file has a valid extension
        if is_valid_file_extension(stego_object.name, valid_extensions):
            st.success(f"File '{stego_object.name}' successfully uploaded!")
        else:
            st.error("Invalid file type! Please upload a JPG, MP3, or MP4 file.")
    
    lsb_value = st.slider("No. of LSB Cover Object Bits Selected", min_value=1, max_value=8)

    if stego_object is not None:
        if st.button("Decode"):
            try:
                st.header('Input:')
                if stego_object.type in ['audio/mpeg','audio/x-wav']:
                    st.audio(stego_object, format=stego_object.type)
                    payload_text = decode_audio(lsb_value, stego_object)
                elif stego_object.type.startswith('image'):
                    st.image(stego_object, use_column_width=True)
                    st.write(f"Decoding......")
                    payload_text = decode_image(stego_object, lsb_value)
                elif stego_object.type in ['video/QuickTime', 'video/mp4']:
                    st.video(stego_object, format=stego_object.type)
                    frame_extraction(stego_object, './tmp2')
                    decode_all_frames("./tmp2")
                st.header('Payload:')
                st.write(payload_text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload the Stego Object.")
    return stego_object

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

            decodetext = decode_image(imagepath, 8)  # Attempt to decode the image
            

            if decodetext == 0:
                print("All Encoded Files Decoded")
                break
                
            else:
                st.write("Decoding.. File:", imagepath, "Decoded Text: ", decodetext)
                print("Decoding.. File:", imagepath, "Decoded Text: ", decodetext)
                decodetextlist.append(decodetext)
                continue
    
        full_decoded_message = "".join(decodetextlist)
        print("Decoding Done! Decoded Text:", full_decoded_message) #show decoded text after all decode has been done for all files, decoded text is the same for all frames 

def decode_image(image_name, lsb):
    lsb = int(lsb)
    modlsb = 8 % lsb
    last = ("0"*modlsb)

    nullt = to_bin("=====")

    # Read the image
    if (type(image_name) == str):
        image = cv2.imread(image_name)
    else:
        file_bytes = np.asarray(bytearray(image_name.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
    binary_data = ""
    status = 0  # if status = 1 means decode finish

    # decode from all r channels first
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            pixel = image[i, j]  # Get the pixel at the current position
            # Convert RGB values of the pixel to binary format
            r, g, b = to_bin(pixel)
            # Extract the LSB of Red channel and add to binary_data
            binary_data += r[-(lsb):]
            if nullt in binary_data:  # idt this is working. Technically to find the terminator, but even if cant find also its ok
                status = 1
                break
        if nullt in binary_data:  # idt this is working. Technically to find the terminator, but even if cant find also its ok
            status = 1
            break

    # decode from all g channels
    if status != 1:
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                pixel = image[i, j]  # Get the pixel at the current position
                # Convert RGB values of the pixel to binary format
                r, g, b = to_bin(pixel)
                # Extract the LSB of Red channel and add to binary_data
                binary_data += g[-(lsb):]
                if nullt in binary_data:  # idt this is working. Technically to find the terminator, but even if cant find also its ok
                    status = 1
                    break
            if nullt in binary_data:  # idt this is working. Technically to find the terminator, but even if cant find also its ok
                status = 1
                break
    # decode from all b channels (should nv reach here unless u input harry potter bruh)
    if status != 1:
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                pixel = image[i, j]  # Get the pixel at the current position
                # Convert RGB values of the pixel to binary format
                r, g, b = to_bin(pixel)
                # Extract the LSB of Red channel and add to binary_data
                binary_data += g[-(lsb):]
                if nullt in binary_data:  # idt this is working. Technically to find the terminator, but even if cant find also its ok
                    status = 1
                    break
            if nullt in binary_data:  # idt this is working. Technically to find the terminator, but even if cant find also its ok
                status = 1
                break
    if status != 1:
        print("Null Terminator not found")

    # Split binary into 8-bit chunks
    all_bytes = [binary_data[i: i + 8] for i in range(0, len(binary_data), 8)]
    decoded_data = ""
    for byte in (all_bytes):
        # Convert each 8-bit chunk to a character
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "=====":
            break

    return decoded_data[:-5]

def decode_audio(n, input_audio):
    print("\nDecoding Starts..")
    if input_audio:
    
        # Create a temporal file
        with tempfile.NamedTemporaryFile() as temp_file:
            # Write the SGY to the temporal file
            temp_file.write(input_audio.getbuffer())
            
            # Now you can use the temporal file path
            audio = wave.open(temp_file.name, mode="rb")

    terminator = "====="
    terminator = str(terminator)

    binary_terminator = ''.join(format(ord(char), '08b') for char in terminator)


    # Convert audio into bytes
    frame_bytes = list(audio.readframes(audio.getnframes()))


    # Initialize an empty string to store the binary representation
    binary_list = []

    # Convert all bytes of audio into binary
    for byte in frame_bytes:
        binary_value = bin(byte)[2:].zfill(8)
        binary_list.append(binary_value)

    # Initialize an empty string to store the hidden message
    hidden_message = ''
    hidden_bits = ''

    # Iterate through the audio bits to retrieve the message
    for binary_byte in binary_list:
        retrieved_bits = binary_byte[-n:]
        hidden_bits += retrieved_bits

        if binary_terminator in hidden_bits:
            break



    # Iterate through the bit string and group by 8 bits
    for i in range(0, len(hidden_bits), 8):
        chunk = hidden_bits[i:i + 8]
        ascii_character = chr(int(chunk,2))
        hidden_message += ascii_character

        # if terminator in hidden_message:
        #     message = hidden_message.replace("====", "")
        #     break

    print("Decoded message: ", hidden_message[:-5])

    audio.close()
    return hidden_message[:-5]


def main():
    output = 'output.png'
    st.markdown('<style>body{background-color: Blue;}</style>',unsafe_allow_html=True)

    st.title('ACW 1.0: LSB Replacement Steganography Program')
    switch = st.radio('Choice:', ['Encode','Decode'])

    match switch:
        case 'Encode':
            encode_get_input()

            
        case 'Decode':
            decode_get_input()


if __name__ == "__main__":
    main()