from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from .models import WoodScaling, WoodType, Forests, Supplier
from .forms import DownloadForm
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

def convert_to_japanese_date(english_date):
    if not isinstance(english_date, datetime):
        english_date = datetime.strptime(english_date, "%Y%m%d")

    # Define the era transitions
    era_transitions = [
        (datetime(2019, 5, 1), "令和"),  # Reiwa era begins
    ]

    for transition_date, era_name in reversed(era_transitions):
        if english_date >= transition_date:
            japanese_year = english_date.year - transition_date.year + 1
            return f"{era_name}{japanese_year}年{english_date.month}月{english_date.day}日"

    return f"{english_date.year}年{english_date.month}月{english_date.day}日"
    pass

def generate_pdf(selected_data):
    try:
        wood_scaling_data = WoodScaling.objects.all()
        wood_type_data = WoodType.objects.all()
        forests_data = Forests.objects.all()
        supplier_data = Supplier.objects.all()
        pdfmetrics.registerFont(TTFont("BIZUDPGothic-Regular", "static/file/BIZUDPGothic-Regular.ttf"))
        buffer = BytesIO()
        pdf_document = canvas.Canvas(buffer)

        pdf_document.setFont("BIZUDPGothic-Regular", 12)
        # Set the initial y_position

        # Loop through wood_type_data and draw strings
        for entry in selected_data:
            formatted_date = entry.weighting_day.strftime("%Y%m%d")
            slip_no = entry.slip_no
            combined_value = f"{formatted_date}-{slip_no}"
            pdf_document.drawString(400, 780, f"証明書番号:　 {combined_value}") 

            japanese_date = convert_to_japanese_date(formatted_date)
            pdf_document.drawString(400, 762, f"発行日:　 {japanese_date}")

            pdf_document.drawString(150, 690, f"発電用チップに係る間伐材等由来の木質バイオマス証明")

            pdf_document.drawString(50, 630, f"森林美化バイオマス合同会社　殿")

            supplier = supplier_data.get(id=entry.vendor_num)
            pdf_document.drawString(380, 590, f"{supplier.name} 　")
            pdf_document.drawString(530, 590, f" 　印")
            pdf_document.drawString(380, 570, f"認定番号　{supplier.registration} ")

            pdf_document.drawString(50, 520, f"下記の物件は、間伐材由来の木質バイオマスであり、")
            pdf_document.drawString(50, 500, f"適切に分別管理されていることを証明します。")

            pdf_document.drawString(300, 450, f"記")

            pdf_document.drawString(70, 420, f"1. 　間伐材等由来の木質バイオマスの種類")

            forests = forests_data.get(id=entry.sources_num)
            pdf_document.drawString(80, 400, f" 　{forests.classification} ")
            pdf_document.drawString(70, 370, f"2. 　{forests.removal}")
            
            date_string = forests.date
            date_object = datetime.strptime(date_string, '%Y-%m-%d')

            # Now you can use strftime on the datetime object
            formatted_d = date_object.strftime("%Y%m%d")
            
            japanese_d = convert_to_japanese_date(formatted_d)
            pdf_document.drawString(70, 340, f"3. 　伐採許可（届出）の年月日　{japanese_d}")
            pdf_document.drawString(80, 320, f" 　許可書発行者　{forests.authority}")
            pdf_document.drawString(80, 300, f" 　伐採許可番号　{forests.registration}")

            pdf_document.drawString(70, 270, f"4. 　物件（森林）所在地")
            pdf_document.drawString(80, 250, f" 　{forests.location}")

            pdf_document.drawString(70, 220, f"5. 　伐採面積　 {forests.area}   ヘクタール")

            wood_type = wood_type_data.get(id=entry.woods_type_num)
            pdf_document.drawString(70, 190, f"6. 　樹種　  {wood_type.name}")

            pdf_document.drawString(70, 160, f"7. 　数量　 {entry.net_weight}")

            pdf_document.drawString(490, 130, f"以上")

            forests = None
            try:
                # Attempt to get the Forests object
                forests = Forests.objects.get(id=entry.sources_num)
            except ObjectDoesNotExist:
                # Handle the DoesNotExist exception
                raise ObjectDoesNotExist("Forests object does not exist for the given ID")

        pdf_document.save()

        # Move the buffer's position to the beginning
        buffer.seek(0)
        return buffer

    except Exception as e:
        # Print the exception for debugging
        print(f"An error occurred in generate_pdf: {str(e)}")
        raise  # Re-raise the exception to see the full traceback

def download_certificate(request):
    try:
        if request.method == 'POST':
            form = DownloadForm(request.POST)
            if form.is_valid():
                selected_data = form.cleaned_data['selected_data']
                pdf_buffer = generate_pdf(selected_data)

            # Set up the HttpResponse for the PDF file
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=certificate.pdf'

            return response
    except ObjectDoesNotExist as e:
        # Render the template with the custom error message
        return render(request, 'wood_scaling/wood_scaling_list.html', {'error_message': f"{str(e)}: Go back "})
    except Exception as e:
        # Print the exception for debugging
        print(f"An error occurred in download_certificate: {str(e)}")
        raise  # Re-raise the exception to see the full traceback

        # Add appropriate response or redirect if there's no error
        return HttpResponse("Error generating PDF")