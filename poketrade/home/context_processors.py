def base_context(request):
    notif_count = 0
    notif_result_count = 0
    if request.user.is_authenticated:
        from .models import TradeOffer
        notif_count = TradeOffer.objects.filter(listing__seller=request.user, status='pending').count()
        notif_result_count = TradeOffer.objects.filter(offered_by=request.user, status__in=['accepted', 'rejected'], is_result_read=False).count()
    return {
        'trade_offer_notif_count': notif_count,
        'trade_result_notif_count': notif_result_count,
    }
