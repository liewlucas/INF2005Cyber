import streamlit as st

# Allow file types: JPG, MP3, MP4, MOV
valid_extensions = ["jpg", "jpeg", "mp3", "mp4","mov"]

# Function to check if the file extension is allowed
def is_valid_file_extension(file_name, valid_extensions):
    file_extension = file_name.split(".")[-1]
    return file_extension.lower() in valid_extensions

# Function to encode data
def encode_get_input():
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
                if cover_object.type == 'audio/mpeg':
                    st.audio(cover_object, format='audio/mpeg')
                elif cover_object.type.startswith('image'):
                    st.image(cover_object, use_column_width=True)
                elif cover_object.type in ['video/QuickTime', 'video/mp4']:
                    st.video(cover_object, format=cover_object.type)
                st.write(f"Input payload: {payload_input}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                
    else:
        st.warning("Please provide Cover Object and Payload.")
    return cover_object, payload_input

def encode_display_output(stego_object):
    # Display Stego Output
    st.header('Output:')
    if stego_object.type == 'audio/mpeg':
        st.audio(stego_object, format='audio/mpeg') 
    elif stego_object.type.startswith('image'):
        st.image(stego_object, use_column_width=True)
    elif stego_object.type in ['video/QuickTime', 'video/mp4']:
        st.video(stego_object, format=stego_object.type)
    

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
                if stego_object.type == 'audio/mpeg':
                    st.audio(stego_object, format='audio/mpeg')
                elif stego_object.type.startswith('image'):
                    st.image(stego_object, use_column_width=True)
                elif stego_object.type in ['video/QuickTime', 'video/mp4']:
                    st.video(stego_object, format=stego_object.type)

            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload the Stego Object.")
    return stego_object

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
    st.markdown('<style>body{background-color: Blue;}</style>',unsafe_allow_html=True)

    st.title('ACW 1.0: LSB Replacement Steganography Program')
    switch = st.radio('Choice:', ['Encode','Decode'])

    match switch:
        case 'Encode':
            payload, cover_object = encode_get_input()

            # convert to binary function 


            stego_object = None # Input stego encode function
            st.write(f"Encoding......")
            if stego_object is not None:
                decode_display_output()
            
        case 'Decode':
            stego_object = decode_get_input()
            st.write(f"Decoding......")
            cover_object, payload = None, None # Input stego decode function
            if cover_object and payload is not None:
                decode_display_output()

if __name__ == "__main__":
    main()