from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from .models import SupplierLogo , Certificate
from .forms import CertificateForm, SupplierLogoForm, EditSupplierLogoForm
from django.contrib.auth.decorators import permission_required
from auth_app.middlewares import auth
from django.conf import settings
import os
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from datetime import datetime
from django.core.files import File


@auth
@permission_required('doc_pdf.view_certificate', raise_exception=True)
def verification(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            form.instance.by_user = user_string
            form.save()
            try:
                form.save()
                messages.success(request, 'Certificate saved successfully.')
                return redirect('verification')  # Redirect to the supplier logo list view
            except Exception as e:
                print(f"Error saving the verification: {e}")
                messages.error(request, f'Error saving the verification. {e}')
        else:
            print(form.errors)  # Print form errors to console
            messages.error(request, 'Error saving the certificate. Please check the file.')
    else:
        form = CertificateForm()
    
    certificates = Certificate.objects.all()
    supplierLogos = SupplierLogo.objects.all()
    
    filtered_certificates = []
    for supplierLogo in supplierLogos:
        if request.user.username in supplierLogo.email:
            
            for certificate in certificates:
                if supplierLogo.supplier_name_id == certificate.supplier_name_id:
                    filtered_certificates.append(certificate)

    if not filtered_certificates:
        # If no certificates match the conditions, include all certificates
        filtered_certificates = certificates
    
    print(filtered_certificates)

    return render(request, 'doc_pdf/verification.html', {'filtered_certificates': filtered_certificates,'supplierLogos' :supplierLogos,  'form': form})


@auth  
@permission_required('doc_pdf.change_certificate', raise_exception=True)
def verify_and_edit_pdf(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)
    certificate_supplier_name_id = certificate.supplier_name_id
    
    # Step 2: Retrieve Certificate and Stamp
    edit_certificate_path = certificate.unverified_certificate.path
    supplier_logo = get_object_or_404(SupplierLogo, supplier_name_id=certificate.supplier_name_id)
    stamp_path = supplier_logo.stamp.path
    
    # Print paths for verification
    print("Edit Certificate Path:", edit_certificate_path)
    print("Supplier Logo Path:", stamp_path)

    # Step 3: Generate a New PDF
    new_pdf_directory = os.path.join(settings.MEDIA_ROOT, 'certificates', 'verified')
    new_pdf_path = os.path.join(new_pdf_directory, f'{certificate_supplier_name_id}_verified.pdf')

    # Use os.path.join for constructing paths
    new_pdf_path = os.path.normpath(new_pdf_path)

    print("New PDF Path:", new_pdf_path)

    pdf_reader = PdfReader(edit_certificate_path)
    pdf_writer = PdfWriter()

    for page_num in range(len(pdf_reader.pages)):
        existing_page = pdf_reader.pages[page_num]

        # Calculate the position to place the image on the right-middle
        page_width, page_height = letter
        image_width, image_height = 50, 50  # Adjust the image dimensions as needed
        x = 510  # Adjust the margin if needed
        y = 580

        # Create a new PDF with the same size as the original page
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.drawImage(stamp_path, x, y, width=image_width, height=image_height)
        can.save()

        # Move to the beginning of the StringIO buffer
        packet.seek(0)
        new_pdf = PdfReader(packet)

        # Merge the image PDF with the existing PDF
        existing_page.merge_page(new_pdf.pages[0])

        # Add the modified page to the new PDF
        pdf_writer.add_page(existing_page)

    # Save the modified PDF to a file
    with open(new_pdf_path, 'wb') as output_file:
        pdf_writer.write(output_file)

    # Update the Certificate model with the new PDF
    date_time_str = datetime.now().strftime("%Y%m%d%H%M%S")
    pdf_filename = f'{date_time_str}_verified.pdf'

    # Use File context manager to handle file operations
    with File(open(new_pdf_path, 'rb')) as verified_certificate_file:
        certificate.verified_certificate.save(pdf_filename, verified_certificate_file)

    certificate.save()

    return redirect('verification')


@auth
@permission_required('doc_pdf.view_supplierlogo', raise_exception=True)
def supplier_logo(request):
    if request.method == 'POST':
        form = SupplierLogoForm(request.POST, request.FILES)
        if form.is_valid():
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            form.instance.by_user = user_string

            print(form.cleaned_data)  # Print form data to console

            try:
                form.save()
                messages.success(request, 'Supplier logo saved successfully.')
                return redirect('supplier_logo')  # Redirect to the supplier logo list view
            except Exception as e:
                print(f"Error saving the supplier logo: {e}")
                messages.error(request, f'Error saving the supplier logo. {e}')
        else:
            print(form.errors)  # Print form errors to console
            messages.error(request, 'Error saving the supplier logo. Please check the form.')
    else:
        form = SupplierLogoForm()
    
    logos = SupplierLogo.objects.all()
    
    return render(request, 'doc_pdf/supplier_logo.html', {'form': form, 'logos': logos})



@auth
@permission_required('doc_pdf.change_supplierlogo', raise_exception=True)
def edit_supplier_logo(request, logo_id):
    logo = get_object_or_404(SupplierLogo, id=logo_id)

    if request.method == 'POST':
        form = EditSupplierLogoForm(request.POST, request.FILES, instance=logo)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Supplier logo updated successfully.')
                return redirect('supplier_logo')  # Redirect to the supplier logo list view
            except Exception as e:
                print(f"Error updating the supplier logo: {e}")
                messages.error(request, f'Error updating the supplier logo. {e}')
        else:
            messages.error(request, 'Error updating the supplier logo. Please check the form.')
    else:
        form = EditSupplierLogoForm(instance=logo)

    return render(request, 'doc_pdf/edit_supplier_logo.html', {'form': form, 'logo': logo})