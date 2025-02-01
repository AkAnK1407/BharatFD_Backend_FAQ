from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.cache import cache
from .models import FAQ
from .serializers import FAQSerializer
import logging
from django.shortcuts import render
import requests


@api_view(['GET'])
def get_faqs(request):
    lang = request.GET.get('lang', 'en')
    cache_key = f'faqs_{lang}'

    try:
        faqs = cache.get(cache_key)
        print("cache found")
    except Exception:
        faqs = None
    logging.debug("got here ")

    if faqs is None:
        faqs = FAQ.objects.all()

        # Translate and prepare data
        for faq in faqs:
            translated_data = faq.get_translation(lang)
            faq.question = translated_data["question"]
            faq.answer = translated_data["answer"]

        # Serialize the FAQs
        serializer = FAQSerializer(faqs, many=True)
        faqs = serializer.data

        try:
            cache.set(cache_key, faqs, timeout=3600)
        except Exception:
            print("redis not found ")

    else:
        logging.debug("got cache ")
    return Response(faqs)

def faq_page(request):
    # URL to your own API endpoint
    api_url = "http://127.0.0.1:8000/api/faqs/"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raises an error for bad status codes
        faqs = response.json()
    except requests.RequestException:
        faqs = []  # Fallback if API request fails

    # Render the 'faq.html' template with fetched FAQs
    return render(request, "faq.html", {"faqs": faqs})
