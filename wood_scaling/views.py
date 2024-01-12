from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseForbidden
from .models import WoodScaling, WoodType, Forests, Supplier
from datetime import datetime
from .wsl_utils_views import filter_wood_scaling_data, paginate_wood_scaling_data, calculate_totals
from .pdf_utils_views import generate_pdf, download_certificate
from .forms import RemarksForm, AddSupplierForm, SupplierEditForm, ForestsEditForm, AddForestForm, WoodScalingSearchForm, UploadFileForm
from django.contrib.auth.decorators import permission_required
from auth_app.middlewares import auth
import pandas as pd
import io
import csv
import chardet


@auth
def welcome(request):
    return render(request, 'wood_scaling/welcome.html')


@auth
@permission_required('wood_scaling.view_woodscaling', raise_exception=True)
def wood_scaling_list(request):
    # Retrieve all data
    all_wood_scaling_data = WoodScaling.objects.all()
    wood_type_data = WoodType.objects.all()
    forests_data = Forests.objects.all()
    supplier_data = Supplier.objects.all()

    # Retrieve search parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    vendor_name = request.GET.get('vendor_name')
    wood_source = request.GET.get('wood_source')

    # Filter data based on search parameters
    error_message = None
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        if end_date < start_date:
            error_message = "End date must be equal to or later than the start date"

    # If there's an error, display an alert and return
    if error_message:
        return render(request, 'wood_scaling/wood_scaling_list.html', {'error_message':f"{str(error_message)}: Click reset button "})

    # Filter data based on search parameters
    filtered_wood_scaling_data = filter_wood_scaling_data(all_wood_scaling_data, start_date, end_date, vendor_name, wood_source).order_by('id')

    # Download CSV file
    if request.GET.get('download') == 'csv':
        # Define the columns to be included in the CSV file
        columns = ['id', 'weighting_day', 'slip_no', 'woods_type_num', 
                    'trucks_num', 'vendor_num', 'sources_num', 'others', 
                    'total_weight_time', 'total_weight', 'empty_weight_time', 'empty_weight', 'net_weight', 'remarks', 'update_time']

        # Create a Pandas DataFrame from the filtered data with explicit columns
        df = pd.DataFrame(list(filtered_wood_scaling_data.values()), columns=columns)

        # Convert datetime columns to timezone-unaware datetimes
        df['weighting_day'] = pd.to_datetime(df['weighting_day']).dt.tz_localize(None)

        
        df['woods_type_num'] = df['woods_type_num'].map(lambda num: next((wood.name for wood in wood_type_data if wood.id == num), num))
        df['vendor_num'] = df['vendor_num'].map(lambda num: next((supplier.name for supplier in supplier_data if supplier.id == num), num))
        df['sources_num'] = df['sources_num'].map(lambda num: next((forests.location for forests in forests_data if forests.id == num), num))
        for index, value in enumerate(df['others']):
            for forest in forests_data:
                if forest.id == value:
                    df.at[index, 'others'] = forest.registration
                    break
                
        # Create an in-memory buffer for the CSV file
        csv_buffer = io.StringIO()

        # Use pandas to_csv to write the DataFrame to the buffer
        df.to_csv(csv_buffer, index=False, quoting=csv.QUOTE_NONNUMERIC)

        # Create a response with the CSV file
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=filtered_wood_scaling_data.csv'
        response.write(csv_buffer.getvalue())

        return response


    # Pagination
    wood_scaling_data = paginate_wood_scaling_data(request, filtered_wood_scaling_data)

    # Calculate totals
    total_weight_sum, empty_weight_sum, corrected_net_sum, grand_total_weight_sum, grand_empty_weight_sum, grand_corrected_net_sum = calculate_totals(all_wood_scaling_data, wood_scaling_data)
    
    #geting the search from
    wood_scaling_search_form = WoodScalingSearchForm(request.GET)

    return render(request, 'wood_scaling/wood_scaling_list.html', {
        'wood_scaling_data': wood_scaling_data,
        'total_weight_sum': total_weight_sum,
        'empty_weight_sum': empty_weight_sum,
        'corrected_net_sum': corrected_net_sum,
        'grand_total_weight_sum': grand_total_weight_sum,
        'grand_empty_weight_sum': grand_empty_weight_sum,
        'grand_corrected_net_sum': grand_corrected_net_sum,
        'wood_type_data': wood_type_data,
        'forests_data': forests_data,
        'supplier_data': supplier_data,
        'start_date': start_date,
        'end_date': end_date,
        'vendor_name': vendor_name,
        'wood_source': wood_source,
        'wood_scaling_search_form': wood_scaling_search_form ,
        'error_message': error_message ,
    })

@auth
def details_page(request, entry_id):
    entry = get_object_or_404(WoodScaling, id=entry_id)
    wood_type_data = WoodType.objects.all()
    forests_data = Forests.objects.all()
    supplier_data = Supplier.objects.all()
    form = RemarksForm()

    # Pass all the data associated with the entry to the template
    context = {
        'entry': entry,
        'wood_type_data': wood_type_data,
        'forests_data': forests_data,
        'supplier_data': supplier_data,
        'form': form,
    }
    if request.method == 'POST':
        form = RemarksForm(request.POST)
        if form.is_valid():
            entry.remarks = form.cleaned_data['remarks']

            # Convert request.user to a string
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            entry.by_user = user_string

            #entry.update_time = timezone.now()
            entry.save()
            return redirect('details_page', entry_id=entry_id)
    else:
        # Pass the current value to the form
        form = RemarksForm(initial={'remarks': entry.remarks})

    return render(request, 'wood_scaling/details_page.html', context)


@auth
@permission_required('wood_scaling.view_supplier', raise_exception=True)
def supplier(request):
    supplier_data = Supplier.objects.all()

    return render(request, 'wood_scaling/supplier_list.html', {'supplier_data': supplier_data})


@auth
@permission_required('wood_scaling.change_supplier', raise_exception=True)
def edit_supplier(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == 'POST':
        form = SupplierEditForm(request.POST, instance=supplier)
        if form.is_valid():
            # Convert request.user to a string
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            
            # Set the by_user field
            form.instance.by_user = user_string
            
            # Save the form data
            form.save()

            return redirect('supplier_list')

    else:
        form = SupplierEditForm(instance=supplier)

    return render(request, 'wood_scaling/edit_supplier.html', {'form': form, 'supplier': supplier})

@auth
@permission_required('wood_scaling.add_supplier', raise_exception=True)
def add_supplier(request):
    error_message = None

    if request.method == 'POST':
        form = AddSupplierForm(request.POST)
        if form.is_valid():
            try:
                # Convert request.user to a string
                user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
                
                # Get the unsaved instance from the form and set the by_user field
                supplier_instance = form.save(commit=False)
                supplier_instance.by_user = user_string
                supplier_instance.save()

                return redirect('supplier_list')  # Replace with your actual supplier list view name
            except Exception as e:
                # Handle any errors during data save
                error_message = f"An error occurred while saving data: {str(e)}"
        else:
            # Capture form validation errors
            error_message = "Form validation error. Please correct the errors below."

    else:
        form = AddSupplierForm()

    return render(request, 'wood_scaling/add_supplier.html', {'form': form, 'error_message': error_message})


@auth
@permission_required('wood_scaling.view_forests', raise_exception=True)
def show_forests_data(request, supplier_id):
    supplier = get_object_or_404(Supplier, id=supplier_id)
    forests_data = Forests.objects.filter(supplier_id=supplier.id)
    
    return render(request, 'wood_scaling/show_forests_data.html', {
        'supplier': supplier, 
        'forests_data': forests_data, 
    })

@auth
@permission_required('wood_scaling.change_forests', raise_exception=True)
def edit_forests(request, forest_id, supplier_id,):
    forest = get_object_or_404(Forests, id=forest_id)

    if request.method == 'POST':
        form = ForestsEditForm(request.POST, instance=forest)
        if form.is_valid():
            # Convert request.user to a string
            user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
            
            # Set the by_user field
            form.instance.by_user = user_string
            form.save()
            
            return redirect('show_forests_data', supplier_id=forest.supplier_id)
    else:
        form = ForestsEditForm(instance=forest)

    return render(request, 'wood_scaling/edit_forests.html', {'form': form, 'forest': forest})

@auth
@permission_required('wood_scaling.add_forests', raise_exception=True)
def add_forest(request, supplier_id):
    error_message = None

    # Get the Supplier object
    supplier = get_object_or_404(Supplier, id=supplier_id)

    if request.method == 'POST':
        form = AddForestForm(request.POST, initial={'supplier_id': supplier.id})
        if form.is_valid():
            try:
                # Save the form data with the supplier_id

                user_string = str(request.user) if request.user.is_authenticated else 'default_by_user'
                
                forest = form.save(commit=False)
                forest.by_user = user_string
                forest.supplier_id = supplier.id
                forest.save()
                
                return redirect('show_forests_data', supplier_id=supplier.id)
            except Exception as e:
                # Handle any errors during data save
                error_message = f"An error occurred while saving data: {str(e)}"
        else:
            # Capture form validation errors
            error_message = "Form validation error. Please correct the errors below."

    else:
        # Initialize the form with supplier_id as initial data
        form = AddForestForm(initial={'supplier_id': supplier.id})

    return render(request, 'wood_scaling/add_forest.html', {'form': form, 'supplier': supplier, 'error_message': error_message})

@auth
@permission_required('wood_scaling.add_woodscaling', raise_exception=True)
@require_http_methods(["GET", "POST"])
def upload_csv(request):
    template_name = 'wood_scaling/upload.html'
    success = False
    error_message = None

    if request.method == 'GET':
        form = UploadFileForm()
    elif request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                # Handle file upload and data processing
                csv_file = request.FILES['file']

                # Automatically detect the encoding
                rawdata = csv_file.read()
                result = chardet.detect(rawdata)
                encoding = result['encoding']

                # Decode the content using the detected encoding
                decoded_content = rawdata.decode(encoding)

                # Create a StringIO object to simulate a file-like object
                from io import StringIO
                text_file = StringIO(decoded_content)

                # Read the first line to check for column names
                first_line = next(text_file)

                # Reset file pointer to the beginning of the file
                text_file.seek(0)

                # Read CSV file starting from the second line
                df = pd.read_csv(text_file, skiprows=[0])

                # Mapping between Japanese and English column names
                column_mapping = {
                    '計量日': 'weighting_day',
                    '伝票No.': 'slip_no',
                    '銘柄': 'woods_type_num',
                    '車番': 'trucks_num',
                    '業者': 'vendor_num',
                    '行先': 'sources_num',
                    'その他': 'others',
                    '総重量時間': 'total_weight_time',
                    '総重量(kg)': 'total_weight',
                    '空重量時間': 'empty_weight_time',
                    '空重量(kg)': 'empty_weight',
                    '補正正味(kg)': 'net_weight',
                    '備考': 'remarks'
                }

                # Rename columns using the mapping
                df = df.rename(columns=column_mapping)

                # Drop unnecessary columns starting with 'Unnamed'
                df = df.loc[:, ~df.columns.str.match('Unnamed')]

                # Handle empty strings in numeric fields
                numeric_columns = ['slip_no','woods_type_num','trucks_num','vendor_num','sources_num', 'total_weight', 'empty_weight', 'net_weight']
                df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

                # Specify the date format in the parse_dates parameter
                date_format = '%Y/%m/%d'

                # Check if 'weighting_day' is in the columns
                if 'weighting_day' in df.columns:
                    df['weighting_day'] = pd.to_datetime(df['weighting_day'], format=date_format)
                else:
                    raise ValueError("Column 'weighting_day' not found in the CSV file.")

                #replace the other values with sources_num in some file other field is blank and they are same 
                df['others'] = df['sources_num']


                # Check if the DataFrame has any columns
                if df.empty or df.columns.empty:
                    raise ValueError("No columns found in the CSV file. Check the file content and format.")

                # Set by_user to the current user
                df['by_user'] = request.user
                

                # Initialize lists to store duplicate and non-duplicate rows
                duplicate_rows = []
                non_duplicate_rows = []

                # Iterate through rows and check for duplicates
                for index, row in df.iterrows():
                    # Check for duplicates based on selected columns
                    existing_row = WoodScaling.objects.filter(
                        weighting_day=row['weighting_day'],
                        slip_no=row['slip_no'],
                        net_weight=row['net_weight']
                    ).first()

                    # If a match is found, add to duplicate_rows list; otherwise, add to non_duplicate_rows list
                    if existing_row:
                        duplicate_rows.append(row)
                    else:
                        non_duplicate_rows.append(row)

                # Print duplicate rows
                if duplicate_rows:
                    print("Duplicate rows:")
                    print(pd.DataFrame(duplicate_rows))

                # Print non-duplicate rows
                if non_duplicate_rows:
                    print("\nNon-duplicate rows:")
                    print(pd.DataFrame(non_duplicate_rows))

                # Insert non-duplicate rows into the database
                if non_duplicate_rows:
                    WoodScaling.objects.bulk_create(
                        [WoodScaling(**row.to_dict()) for row in non_duplicate_rows]
                    )
                    print("\nNon-duplicate rows successfully inserted into the database.")

                success = True
            except Exception as e:
                error_message = f"Error: {e}"
                print(f"Error reading or processing CSV file: {e}")

    return render(request, template_name, {'form': form, 'success': success, 'error_message': error_message})
