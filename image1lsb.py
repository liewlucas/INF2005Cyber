import cv2
import numpy as np

# Function to convert data to binary format as a string
def to_bin(data):
    if isinstance(data, str):
        return ''.join([format(ord(i), "08b") for i in data])  # Convert each character to 8-bit binary
    elif isinstance(data, bytes) or isinstance(data, np.ndarray):
        return [(format(i, "08b")) for i in data]  # Convert bytes or ndarray elements to 8-bit binary
    elif isinstance(data, int) or isinstance(data, np.uint8):
        return format(data, "08b")  # Convert integer or uint8 to 8-bit binary
    else:
        raise TypeError("Type not supported.")

# Function to encode data into an image
def encode(image_name, secret_data):
    print("text:",secret_data)
    image = cv2.imread(image_name)  # Read the image
    n_bytes = image.shape[0] * image.shape[1] * 3 // 8  # Calculate the maximum number of bytes that can be encoded in the image
    print("[*] Maximum bytes to encode: ", n_bytes)
    secret_data += "====="  # Add a stopping criteria for decoding
    if len(secret_data) > n_bytes:
        raise ValueError("[!] Insufficient bytes, need bigger image or less data")  # Check if there is enough space for encoding
    print("[*] Encoding data....")

    data_index = 0
    binary_secret_data = to_bin(secret_data)  # Convert the secret data to binary
    data_len = len(binary_secret_data)  # Get the size of data to hide
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            pixel = image[i, j]  # Get the pixel at the current position
            r, g, b = to_bin(pixel)  # Convert RGB values of the pixel to binary format
            if data_index < data_len:
                pixel[0] = int(r[:-1] + binary_secret_data[data_index], 2)  # Encode data into the Red channel LSB
                data_index += 1
            if data_index < data_len:
                pixel[1] = int(g[:-1] + binary_secret_data[data_index], 2)  # Encode data into the Green channel LSB
                data_index += 1
            if data_index < data_len:
                pixel[2] = int(b[:-1] + binary_secret_data[data_index], 2)  # Encode data into the Blue channel LSB
                data_index += 1
            if data_index >= data_len:
                break
        if data_index >= data_len:
            break
    return image

# Function to decode data from an image
def decode(image_name):
    print("[+] Decoding...")
    # Read the image
    image = cv2.imread(image_name)
    binary_data = ""
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            pixel = image[i, j]  # Get the pixel at the current position
            r, g, b = to_bin(pixel)  # Convert RGB values of the pixel to binary format
            binary_data += r[-1]  # Extract the LSB of Red channel and add to binary_data
            binary_data += g[-1]  # Extract the LSB of Green channel and add to binary_data
            binary_data += b[-1]  # Extract the LSB of Blue channel and add to binary_data
            if len(binary_data) >= 32 and binary_data[-32:] == "0" * 32:
                break
        if len(binary_data) >= 32 and binary_data[-32:] == "0" * 32:
            break

    # Split binary data into 8-bit chunks
    all_bytes = [binary_data[i: i + 8] for i in range(0, len(binary_data), 8)]  # Split binary into 8-bit chunks
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))  # Convert each 8-bit chunk to a character
        if decoded_data[-5:] == "=====":
            break
    return decoded_data[:-5]

# Function to encode text into an image using OpenCV
def encode_with_opencv(image_path, text, output_path):
    encoded_image = encode(image_path, text)  # Encode the text into the image
    cv2.imwrite(output_path, encoded_image)  # Save the encoded image to the specified path

# Function to decode text from an image using OpenCV
def decode_with_opencv(image_path):
    decoded_text = decode(image_path)  # Decode the text from the image
    return decoded_text

img_from= "D:\\work\\cyber\\Shini.png"
img_to= "D:\\work\\cyber\\try2.png"
message = "hihi"

# Encode using OpenCV
encode_with_opencv(img_from, message, img_to)

# Decode using OpenCV
decoded_text = decode_with_opencv('D:\\work\\cyber\\try2.png')  # Decode the text from the encoded image
print("decoded text:",decoded_text)  # Print the decoded text

