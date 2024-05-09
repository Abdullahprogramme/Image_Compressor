import streamlit as st
import os
import tempfile
from Main import main
from io import BytesIO
import base64
import time

# Set page configuration
st.set_page_config(page_title='QuadTree Image Compressor', layout="wide", page_icon=':camera:')

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
    if "toast_shown" not in st.session_state:
        st.toast('Welcome to QuadTree Image Compressor!')
        st.session_state.toast_shown = True
    st.error('When an image is already very small, further compression is prevented since, after split into four quadrants, the size of each quadrant will be less than the threshold value. There will thus be a problem with the compression process. Please include an image greater than 100 KB.')
    # Sidebar
    st.sidebar.image("images/QuadTree.png", use_column_width=True, width=100)

    
    st.sidebar.title('Options')
    compression_level = st.sidebar.radio("Compression Level", ("Pixelated", "Average", "Refined"), index=1)

    Thresh_Yes_OR_NO = st.sidebar.checkbox('Do you want to set a custom depth of the tree?')
    if Thresh_Yes_OR_NO:
        MAX_DEPTH = st.sidebar.slider('Set Detail Threshold', 0, 9, 8)
        Tup = (True, MAX_DEPTH) 
    else:
        Tup = (False, 0)
    
    
    set = st.sidebar.selectbox('Set Filter On Image', ('No Filter', 'Gray Scale', 'Black and White', 'Sepia', 'Inverted', 'Thresholded', 'Brightened', 'High Contrast', 'Soft Blur', 'Emboss-like'))

    # need_gif = st.sidebar.selectbox('Do you want a gif?', ('No', 'Yes'))
    need_gif = 'Yes' if st.sidebar.checkbox('Do you want a gif?') else 'No'

    st.sidebar.markdown("---")
    st.sidebar.title('About')
    expander = st.sidebar.expander('About this app', expanded=False)

    expander.write('''
    This application allows you to compress images using the QuadTree algorithm. 

    To use it, follow these steps:
    1. Upload an image using the "Upload Image" button.
    2. Select a compression level. The "slightly less better" option will result in a smaller file size but lower image quality, while the "slightly better" option will result in a larger file size but higher image quality.
    3. Click the "Start Compression" button to start the compression process. This may take a few moments, depending on the size of the image and the selected compression level.
    4. Once the compression is complete, you can download the compressed image using the "Save Compressed Image" button.

    Please note that the compressed image is generated by replacing the quadrants of the original image with a single pixel value, so some loss of detail is to be expected.
    ''')

    st.sidebar.info('''
    **About the QuadTree Algorithm**
                    
    This is a simple image compressor based on the QuadTree algorithm.
                    
    The QuadTree algorithm is a tree data structure in which each internal node has exactly four children.
                    
    The algorithm works by recursively dividing the image into four quadrants until a certain condition is met.
                    
    The compressed image is generated by replacing the quadrants with a single pixel value. 
                    
    The compression level can be adjusted to generate better or worse quality images.
    ''')

    st.sidebar.markdown("---")
    
    # Social Media Icons
    # st.sidebar.markdown('''
    #     ## Connect with me
    #     If you have any questions or if you want to see more of my projects, feel free to connect with me:

    #     [LinkedIn](https://www.linkedin.com/in/abdullahtariq78/) |
    #     [GitHub](https://github.com/Abdullahprogramme) |
    #     [Portfolio](https://abdullahtariq2004.netlify.app/)
    # ''')
    
    st.sidebar.markdown('''
        ## Connect with me
        If you have any questions or if you want to see more of my projects, feel free to connect with me:
    ''')

    col1, col2 = st.sidebar.columns([1,6])

    col1.image("images/linkedin.png", width=24)
    col2.write('<a style="text-decoration: none;" href="https://www.linkedin.com/in/abdullahtariq78/">LinkedIn</a>', unsafe_allow_html=True)

    col1.image("images/github.png", width=24)
    col2.write('<a style="text-decoration: none;" href="https://github.com/Abdullahprogramme">GitHub</a>', unsafe_allow_html=True)

    col1.image("images/briefcase.png", width=26)
    col2.write('<a style="text-decoration: none;" href="https://abdullahtariq2004.netlify.app/">Portfolio</a>', unsafe_allow_html=True)


    # Main content
    st.title('QuadTree Image Compressor')

    st.divider()

    # Image upload
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

    if uploaded_file and compression_level:
        st.subheader('Original Image')
        st.image(uploaded_file, caption='Original Image', use_column_width=True)
        original_size = len(uploaded_file.getvalue())
        st.write('**Original Size:** ' + convert_size(original_size))

        # Progress Bar
        if st.button('Start Compression'):
            with st.spinner('Generating image...have patience, it may take a while!'):
                start_time = time.time()
                if need_gif == 'Yes':
                    compressed_image, gif = main(uploaded_file, compression_level, Tup, set, True)
                    # Convert the BytesIO object to a base64 encoded string
                    gif.seek(0)
                    gif_base64 = base64.b64encode(gif.read()).decode()
                else:
                    compressed_image = main(uploaded_file, compression_level, Tup, set)
                end_time = time.time()
                st.success('Image Compression Complete!')

                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                compressed_image.save(temp_file.name)

            st.subheader('Compressed Image')
            st.image(temp_file.name, caption='Compressed Image', use_column_width=True)
            compressed_size = os.path.getsize(temp_file.name)
            st.write('**Compressed Size:** ' + convert_size(compressed_size))

            # Calculate and display the compression performance
            compression_ratio = (original_size - compressed_size) / original_size * 100
            st.success(f'**Compression Performance:** The image was compressed by {compression_ratio:.2f}%')
            st.success(f'**Time Taken:** {end_time - start_time:.2f} seconds')
            
            # Convert the compressed image to binary data
            buffered = BytesIO()
            compressed_image.save(buffered, format="PNG")
            binary_data = buffered.getvalue()

            # Download button for the compressed image
            st.download_button(label="Download Compressed Image", data=binary_data, file_name='compressed_image.png', mime='image/png')
            st.markdown("---")

            
            if need_gif == 'Yes':
                st.subheader('Gif')
                # Embed the base64 encoded string in an HTML img tag
                st.markdown(f'<img src="data:image/gif;base64,{gif_base64}" alt="Gif" style="width:50%">', unsafe_allow_html=True)
                gif_size = len(gif_base64)
                st.write('**Gif Size:** ' + convert_size(gif_size))

                # Download button for the GIF
                gif.seek(0)
                st.download_button(label="Download GIF", data=gif, file_name="compressed_gif.gif", mime="image/gif")
            
# Run the main application
if __name__ == '__main__':
    Main()
