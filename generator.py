import csv
import base64
import os
import re
import datetime
import qrcode
from Crypto.Hash import SHA256
from Crypto.Signature import DSS
from Crypto.PublicKey import ECC
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter
import io

import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_private_key(key_path):
    try:
        with open(key_path, "rt") as f:
            return ECC.import_key(f.read())
    except Exception as e:
        raise Exception(f"Failed to load private key from {key_path}: {e}")

def generate_cert_id(name, course, year, serial, issued_at, private_key_path):
    private_key = load_private_key(private_key_path)
    
    payload = f"{name}|{course}|{year}|{serial}|{issued_at}"
    b64_payload = base64.urlsafe_b64encode(payload.encode()).decode().rstrip("=")
    
    hashed_data = SHA256.new(payload.encode())
    signer = DSS.new(private_key, 'fips-186-3', encoding='der')
    signature = signer.sign(hashed_data)
    
    b64_signature = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{b64_payload}.{b64_signature}"

def sanitize_filename(filename):
    return re.sub(r'(?u)[^-\w.]', '_', str(filename).strip())

def generate_pdf_certificate(name, course, qr_path, output_pdf_path, cert_type, template_path, settings):
    font_path = resource_path('Satoshi-Black.ttf')
    pdfmetrics.registerFont(TTFont('Satoshi-Black', font_path))
    
    reader = PdfReader(template_path)
    page = reader.pages[0]
    
    page_width = float(page.mediabox.width)
    page_height = float(page.mediabox.height)
    
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(page_width, page_height))
    
    can.setFont("Satoshi-Black", settings.get('name_size', 30.98))
    can.drawCentredString(page_width / 2.0, settings.get('name_y', 343.37), name)

    can.setFont("Satoshi-Black", settings.get('course_size', 41.46))
    can.drawCentredString(page_width / 2.0, settings.get('course_y', 219.47), course)
    
    can.setFont("Satoshi-Black", settings.get('type_size', 16.81))
    can.drawCentredString(page_width / 2.0, settings.get('type_y', 113.69), cert_type)
    
    qr_x = settings.get('qr_x', 726)
    qr_y = settings.get('qr_y', 100)
    qr_size = settings.get('qr_size', 110)
    can.drawImage(qr_path, qr_x, qr_y, width=qr_size, height=qr_size, mask='auto')

    # Club stamp — bottom-right, mirroring the QR, tilted
    stamp_path = resource_path(os.path.join('brand', 'stamp.png'))
    if os.path.exists(stamp_path):
        st_x = settings.get('stamp_x', 650)
        st_y = settings.get('stamp_y', 52)
        st_size = settings.get('stamp_size', 122)
        st_angle = settings.get('stamp_angle', -14)
        can.saveState()
        can.translate(st_x + st_size / 2.0, st_y + st_size / 2.0)
        can.rotate(st_angle)
        can.drawImage(stamp_path, -st_size / 2.0, -st_size / 2.0, width=st_size, height=st_size, mask='auto')
        can.restoreState()

    # Officer signatures — above the two labels at the bottom-left
    sig_w = settings.get('sig_w', 135)
    sig_h = settings.get('sig_h', 46)
    for fname, kx, ky, dx, dy in [
        ('sig_president.png', 'sig_pres_x', 'sig_pres_y', 40, 54),
        ('sig_chef.png', 'sig_chef_x', 'sig_chef_y', 228, 54),
    ]:
        sig_path = resource_path(os.path.join('brand', fname))
        if os.path.exists(sig_path):
            can.drawImage(sig_path, settings.get(kx, dx), settings.get(ky, dy),
                          width=sig_w, height=sig_h, mask='auto',
                          preserveAspectRatio=True, anchor='sw')

    can.save()
    
    packet.seek(0)
    new_pdf = PdfReader(packet)
    overlay_page = new_pdf.pages[0]
    
    page.merge_page(overlay_page)
    
    writer = PdfWriter()
    writer.add_page(page)
    
    with open(output_pdf_path, "wb") as f:
        writer.write(f)

import random
import secrets

SERIAL_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # no ambiguous 0/O/1/I

def generate_serial(year):
    """Short, human-referable, non-sequential serial. Baked into the signed payload."""
    suffix = ''.join(secrets.choice(SERIAL_ALPHABET) for _ in range(6))
    return f"CC-{year}-{suffix}"

def generate_single(name, course, year, cert_type, template_path, settings, base_url, output_dir, private_key_path, is_preview=False):
    safe_course = sanitize_filename(course)
    course_dir = os.path.join(output_dir, safe_course)
    os.makedirs(course_dir, exist_ok=True)
    base_url = base_url.rstrip('/')
    issued_at = datetime.date.today().isoformat()
    serial = generate_serial(year)
    
    cert_id = generate_cert_id(name, course, year, serial, issued_at, private_key_path)
    verify_url = f"{base_url}?id={cert_id}&verify=true"

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=1)
    qr.add_data(verify_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    img.putdata(newData)

    safe_student_name = sanitize_filename(name)
    random_suffix = f"{random.randint(10000, 99999)}"
    qr_filename = f"{safe_student_name}_{year}_{random_suffix}_QR.png"
    qr_filepath = os.path.join(course_dir, qr_filename)
    img.save(qr_filepath, "PNG")

    pdf_filename = f"{safe_student_name}_{year}_{random_suffix}_Certificate.pdf"
    if is_preview:
        pdf_filename = "PREVIEW_" + pdf_filename
    pdf_filepath = os.path.join(course_dir, pdf_filename)
    
    generate_pdf_certificate(name, course, qr_filepath, pdf_filepath, cert_type, template_path, settings)
    
    # Cleanup QR Code immediately after merging
    if os.path.exists(qr_filepath):
        try:
            os.remove(qr_filepath)
        except OSError:
            pass

    return {
        'Name': name,
        'Course': course,
        'Year': year,
        'Serial': serial,
        'IssuedAt': issued_at,
        'Certificate_ID': cert_id,
        'Verification_URL': verify_url,
        'PDF_Path': pdf_filepath
    }

def process_data(names, course, year, cert_type, template_path, settings, private_key_path, base_url="https://code-crafters-bm.github.io/certificates", output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    
    output_csv = "generated_certificates.csv"
    file_exists = os.path.isfile(output_csv)

    results = []
    success_count = 0
    for name in names:
        res = generate_single(name, course, year, cert_type, template_path, settings, base_url, output_dir, private_key_path)
        results.append(res)
        success_count += 1
        
    with open(output_csv, mode='a', encoding='utf-8', newline='') as outfile:
        fieldnames = ['Name', 'Course', 'Year', 'Serial', 'IssuedAt', 'Certificate_ID', 'Verification_URL']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
            
        for res in results:
            row = {k: v for k, v in res.items() if k in fieldnames}
            writer.writerow(row)
            
    return success_count, results