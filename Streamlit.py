import streamlit as st
import os
import tempfile
from Main import main
from io import BytesIO

# Set page configuration
st.set_page_config(page_title='QuadTree Image Compressor', layout="wide")


# Helper function to convert size in bytes to appropriate unit
def convert_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1048576:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / 1048576:.2f} MB"
    
# Define function for main application
def Main():
    # Sidebar
    st.sidebar.title('Options')
    compression_level = st.sidebar.radio("Compression Level", ("slightly less better", "slightly better",))

    # Main content
    st.title('QuadTree Image Compressor')

    st.markdown("---")

    # Image upload
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if uploaded_file and compression_level:
        st.subheader('Original Image')
        st.image(uploaded_file, caption='Original Image', use_column_width=True)
        st.write('**Original Size:** ' + convert_size(len(uploaded_file.getvalue())))

        if st.button('Start Compression'):
            st.write('**Generating compressed image...have patience, it may take a while!**')
            compressed_image = main(uploaded_file, compression_level)
            st.write('**Image Compression Complete!**')

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            compressed_image.save(temp_file.name)

            st.subheader('Compressed Image')
            st.image(temp_file.name, caption='Compressed Image', use_column_width=True)
            st.write('**Compressed Size:** ' + convert_size(os.path.getsize(temp_file.name)))

            # Convert the compressed image to binary data
            buffered = BytesIO()
            compressed_image.save(buffered, format="PNG")
            binary_data = buffered.getvalue()

            # Download button
            st.markdown("---")
            st.download_button(label="Save Compressed Image", data=binary_data, file_name='compressed_image.png', mime='image/png')

# Run the main application
if __name__ == '__main__':
    Main()
