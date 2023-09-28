import streamlit as st
import cv2
import numpy as np
from PIL import Image
import wave
import tempfile

# Allow file types: JPG, MP3, MP4, MOV
valid_extensions = ["jpg", "jpeg", "mp3", "mp4","mov","png", "wav"]

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

# Function to encode data
def encode_get_input():
    output_object = 'sample copy.png'
    st.header('Upload an image/audio/video as cover object and a TEXT payload.')

    cover_object = st.file_uploader("Upload cover object", type=valid_extensions)
    if cover_object is not None:
        print(cover_object.type) # Testing code

        # Check if the uploaded file has a valid extension
        if is_valid_file_extension(cover_object.name, valid_extensions):
            st.success(f"File '{cover_object.name}' successfully uploaded!")
        else:
            st.error("Invalid file type! Please upload a JPG, MP3, or MP4 file.")

    payload_input = st.text_input("Enter payload text:")
    lsb_value = st.slider("No. of LSB Cover Object Bits Selected", min_value=1, max_value=8)

    if cover_object is not None and payload_input:
        if st.button("Encode"):
            try:
                # Display of Input Cover Object and Payload
                st.header('Input:')
                if cover_object.type in ['audio/mpeg','audio/x-wav']:
                    st.audio(cover_object, format=cover_object.type)
                    encode_audio(lsb_value, payload_input, cover_object)
                elif cover_object.type.startswith('image'):
                    st.image(cover_object, use_column_width=True)
                    encode_image(cover_object, output_object, payload_input, lsb_value)
                    st.image(output_object, use_column_width=True)
                elif cover_object.type in ['video/QuickTime', 'video/mp4']:
                    st.video(cover_object, format=cover_object.type)
                st.write(f"Input payload: {payload_input}")
                # print(cover_object) Test code

                
            except Exception as e:
                st.error(f"An error occured: {e}")
                
    else:
        st.warning("Please provide Cover Object and Payload.")
    return output_object


# Function to encode data into an image
def encode_image(cover_object, output, secret_data, lsb):
    file_bytes = np.asarray(bytearray(cover_object.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)
    # print(image.shape) Test code
    # Calculate the maximum number of bytes that can be encoded in the image
    n_bytes = (image.shape[0] * image.shape[1] * 3 // 8)*lsb

    secret_data += "====="  # Add a null terminator

    if len(secret_data) > n_bytes:
        # Check if there is enough space for encoding
        raise ValueError(
            "[!] Insufficient bytes, need bigger image or less data")

    # Convert the secret data to binary
    binary_secret_data = to_bin(secret_data)

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
                st.header('Payload:')
                st.write(payload_text)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload the Stego Object.")
    return stego_object

def decode_image(image_name, lsb):
    lsb = int(lsb)
    modlsb = 8 % lsb
    last = ("0"*modlsb)

    nullt = to_bin("=====")

    # Read the image
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

def decode_display_output(cover_object, payload):
    # Display Cover Object Output
    st.header('Output:')
    if cover_object.type == 'audio/mpeg':
        st.audio(cover_object, format='audio/mpeg') 
    elif cover_object.type.startswith('image'):
        st.image(cover_object, use_column_width=True)
    elif cover_object.type in ['video/QuickTime', 'video/mp4']:
        st.video(cover_object, format=cover_object.type)
    st.write(f"TEXT Payload: {payload}")


def main():
    output = 'output.png'
    st.markdown('<style>body{background-color: Blue;}</style>',unsafe_allow_html=True)

    st.title('ACW 1.0: LSB Replacement Steganography Program')
    switch = st.radio('Choice:', ['Encode','Decode'])

    match switch:
        case 'Encode':
            stego_object = encode_get_input()
            st.write(f"Encoding......")
            # if stego_object is not None:
            #     encode_display_output(stego_object)
            
        case 'Decode':
            stego_object = decode_get_input()
            cover_object, payload = None, None # Input stego decode function
            if cover_object and payload is not None:
                decode_display_output()

if __name__ == "__main__":
    main()