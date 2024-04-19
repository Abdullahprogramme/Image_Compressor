import streamlit as st
import os
import tempfile
from Main import main
from io import BytesIO

st.set_page_config(layout="centered")

def Main():
    st.title('QuadTree Image Compressor')

    compression_level = st.radio("Select a compression level", ("slightly less better", "slightly better",))

    if not compression_level:
        st.error("Please select a compression type")
        return
    
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if uploaded_file and compression_level:
        st.subheader('Original Image:')
        st.image(uploaded_file, caption='Original Image', use_column_width=True)

        original_size = len(uploaded_file.getvalue()) / 1024  # size in KB
        st.write(f'Original size: {original_size:.2f} KB')

        if st.button('Start'):
        
            st.write('Generating image... be patient, this may take a while.')
            compressed_image = main(uploaded_file, compression_level)
            st.write('Image generation complete.')

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            compressed_image.save(temp_file.name)

            st.subheader('Compressed Image:')
            st.image(temp_file.name, caption='Compressed Image', use_column_width=True)

            compressed_size = os.path.getsize(temp_file.name) / 1024  # size in KB
            st.write(f'Compressed size: {compressed_size:.2f} KB')

            # Convert the compressed image to binary data
            buffered = BytesIO()
            compressed_image.save(buffered, format="PNG")
            binary_data = buffered.getvalue()

            # Display "Save" button
            st.download_button(label="Save Compressed Image", data=binary_data, file_name='compressed_image.png', mime='image/png')


if __name__ == '__main__':
    Main()
