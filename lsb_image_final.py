import cv2 #pip install opencv-python
import numpy as np

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

    print("input text:",secret_data) #print text to be encoded into img
    
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

# Function to decode data from an image
def decode(image_name,lsb):
    lsb=int(lsb)
    modlsb = 8%lsb
    last = ("0"*modlsb) 
    print("[+] Decoding...")
    # Read the image
    image = cv2.imread(image_name)
    binary_data = ""
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            pixel = image[i, j]  # Get the pixel at the current position
            r, g, b = to_bin(pixel)  # Convert RGB values of the pixel to binary format
            binary_data += r[-(lsb):]  # Extract the LSB of Red channel and add to binary_data
            binary_data += g[-(lsb):]  # Extract the LSB of Green channel and add to binary_data
            binary_data += b[-(lsb):]  # Extract the LSB of Blue channel and add to binary_data
            if len(binary_data) >= 16 and binary_data[-16] == "1" * 32: #idt this is working. Technically to find the terminator, but even if cant find also its ok
                break
        if len(binary_data) >= 16 and binary_data[-16:] == "1" * 32: #same
            break

    #remove padding from front, add padding back to the back so that it can be split into 8bit chunk properly
    binary_data= binary_data[modlsb:]
    binary_data = binary_data + last

    all_bytes = [binary_data[i: i + 8] for i in range(0, len(binary_data), 8)]  # Split binary into 8-bit chunks
    decoded_data = ""
    for byte in (all_bytes):
        decoded_data += chr(int(byte, 2))  # Convert each 8-bit chunk to a character
        if decoded_data[-5:] == "=====":
            print("ending found3")
            break

    return decoded_data[:-5]

# Function to encode text into an image using OpenCV
def encode_with_opencv(image_path, text, output_path,lsb):
    encoded_image = encode(image_path, text,lsb)  # Encode the text into the image
    cv2.imwrite(output_path, encoded_image)  # Save the encoded image to the specified path

# Function to decode text from an image using OpenCV
def decode_with_opencv(image_path,lsb):
    decoded_text = decode(image_path,lsb)  # Decode the text from the image
    return decoded_text



input_img= "" #path
output_img= "" #path
lsb=8 #
message ="heyeyeye"
print("lsb selected:",lsb)


# Encode using OpenCV
encode_with_opencv(input_img, message,output_img,lsb)

# Decode using OpenCV
decoded_text = decode_with_opencv(output_img,lsb)  # Decode the text from the encoded image
print("decoded text:",decoded_text)  # Print the decoded text
