import cv2  # pip install opencv-python
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
def encode(image_name, output, secret_data, lsb):

    image = cv2.imread(image_name)  # Read the image with cv2

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

# Function to decode data from an image


def decode(image_name, lsb):
    lsb = int(lsb)
    modlsb = 8 % lsb
    last = ("0"*modlsb)

    nullt = to_bin("=====")

    # Read the image
    image = cv2.imread(image_name)
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


input_img = "D:\\work\\cyber\\black.png"  # path
output_img = "D:\\work\cyber\\Shini1.png"  # path
lsb = 1
message = "fvd hehyeqef qe yee"
print("lsb selected:", lsb)


# encodes and saves new img
encode(input_img, output_img, message, lsb)

# Decode and return string
decoded_text = decode(output_img, lsb)
print("decoded text:", decoded_text)  # Print the decoded text
