# Code Crafters Certificate System

A complete, end-to-end cryptographic certificate generation and verification system built for Code Crafters. This repository contains both the Desktop Application (for generating certificates) and the Verification Portal (for validating them).

## 🚀 Features
- **Cryptographic Security:** Certificates are signed using Elliptic Curve Cryptography (ECC P-256), ensuring they cannot be forged or altered.
- **Automated QR Codes:** Every certificate gets a unique, embedded QR code that links directly to the verification portal.
- **Bulk Generation:** Upload a `.txt` or `.csv` file to generate hundreds of certificates in seconds.
- **Smart File Routing:** Automatically organizes outputs into folders based on the course or event name, and appends a random 5-digit number to prevent collisions.
- **Dark Mode Aesthetics:** Both the desktop generator and the web portal use the premium Code Crafters dark navy and vibrant blue color scheme with modern typography (`Outfit` font).

---

## 🛠️ Setup Instructions

### 1. Generate Your Cryptographic Keys
Before generating any certificates, you must create your secure ECC key pair. 
Run the following script via your terminal or command prompt:
```bash
python generate_ecc.py -s "YOUR_SECRET_SEED_PHRASE"
```
*Note: Keep your seed phrase secure! This command will generate two files:*
- `ecc_private_key.pem`: Keep this file **secret** and safe on your local computer. It is used to sign the certificates.
- `ecc_public_key.pem`: This file is public and is used by the website to verify the certificates.

### 2. Desktop Application Usage
You don't need Python installed to use the generator. Just use the provided standalone executable!

1. Double click `CodeCraftersCertificates.exe` to launch the GUI.
2. Go to the **Generation** tab.
3. Click **Upload Names File** to select your list of students (`.txt` or `.csv`).
4. Enter the **Event/Course Name** and the **Year**.
5. Click **Select PDF Template** to choose your blank Code Crafters certificate background.
6. Click **Select Private Key** and choose your `ecc_private_key.pem` file.
7. Click **Generate All Certificates**!

The system will create a new folder inside the `output/` directory named after your course, containing all the generated PDFs ready to be emailed.

### 3. Verification Portal
The Verification Portal (`index.html`) allows anyone to scan the QR code on a certificate to verify its authenticity. 
- It is hosted via GitHub Pages at `https://Code-Crafters-BM.github.io/certificates/`
- When a user scans a QR code, they are taken to a URL like `?id=PAYLOAD.SIGNATURE`
- The portal fetches `ecc_public_key.pem` from the repository and cryptographically verifies the signature in the browser. No backend server required!

---

## 🎨 Advanced Settings (GUI)
If your PDF template changes, you can adjust the exact X and Y coordinates (in points, from the bottom-left of the page) for where the Name, Course, and QR code should be placed using the **Advanced Settings** tab in the desktop application.
