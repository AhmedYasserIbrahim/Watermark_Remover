# Watermark Remover

This is a watermark remover built by **Ahmed Yasser** as a personal project. 

## Overview
1. The program starts by receiving a **URL** from the user.
2. It retrieves the HTML of the given website using **BeautifulSoup4**, extracting the images within.
3. It then uses the **urllib** Python library to remove watermarks from these images.
4. The processed images replace the original watermarked images in the HTML.
5. Finally, the user is redirected to a website displaying the processed images.

## Approaches Explored
I experimented with several libraries and tools:
- **IOPaint**
- **Unwatermark**
- **cv2.inpaint**
- **Stable Diffusion Inpainting**
- **rembg**
- **Tesseract OCR (pytesseract)**
- **ffmpeg**

None met the quality needed, so I resorted to the code found [here](https://github.com/AhmedYasserIbrahim/Watermark_Remover/blob/main/app.py). 

## Make.com Integration
I also explored a **Make.com** approach using APIs. Two common APIs considered:

1. **[Remaker.ai](https://www.remaker.ai)**  
   - Requires manual masking for each image, making it difficult to automate.
2. **[Dewatermark.ai](https://www.dewatermark.ai)**  
   - Requires a minimum payment of \$30, which doesn’t scale well.

Below is the flow built on Make.com:

![image](https://github.com/user-attachments/assets/4a4a4970-0023-420f-ae03-31ae46e6f194)

- It receives the link from the user and fetches the images from the website’s HTML.
- Then, it creates a **GET** request using the API key for the image that needs processing.

While the initial steps work well, it currently requires:
- A workaround for masking with **Remaker.ai** (possibly via endpoints and Python libraries), or
- Payment for an API that fully automates the process.

## Demonstration
Please refer to the [video]() for a demonstration of how the program works.

## Disclaimer
This tool is intended **only for testing** and should **not** be used for commercial purposes.
