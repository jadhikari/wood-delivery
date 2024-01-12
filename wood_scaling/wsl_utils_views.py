from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def filter_wood_scaling_data(all_wood_scaling_data, start_date, end_date, vendor_name, wood_source):
    filters = {}

    if start_date and end_date:
        filters['weighting_day__range'] = [start_date, end_date]

    if vendor_name:
        filters['vendor_num'] = vendor_name

    if wood_source:
        filters['sources_num'] = wood_source

    return all_wood_scaling_data.filter(**filters).order_by('id')

def paginate_wood_scaling_data(request, all_wood_scaling_data):
    page = request.GET.get('page', 1)
    paginator = Paginator(all_wood_scaling_data, 20)  # Show 20 items per page

    try:
        wood_scaling_data = paginator.page(page)
    except PageNotAnInteger:
        wood_scaling_data = paginator.page(1)
    except EmptyPage:
        wood_scaling_data = paginator.page(paginator.num_pages)

    return wood_scaling_data

def calculate_totals(all_wood_scaling_data, wood_scaling_data):
    total_weight_sum = sum(entry.total_weight for entry in wood_scaling_data)
    empty_weight_sum = sum(entry.empty_weight for entry in wood_scaling_data)
    corrected_net_sum = sum(entry.net_weight for entry in wood_scaling_data)

    grand_total_weight_sum = all_wood_scaling_data.aggregate(Sum('total_weight'))['total_weight__sum']
    grand_empty_weight_sum = all_wood_scaling_data.aggregate(Sum('empty_weight'))['empty_weight__sum']
    grand_corrected_net_sum = all_wood_scaling_data.aggregate(Sum('net_weight'))['net_weight__sum']

    return total_weight_sum, empty_weight_sum, corrected_net_sum, grand_total_weight_sum, grand_empty_weight_sum, grand_corrected_net_sum
