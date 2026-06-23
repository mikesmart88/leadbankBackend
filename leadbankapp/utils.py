from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os, random, string, requests
from decimal import Decimal
from . import models


def resize_image(image_field, width=180, height=180):
    if not image_field:
        return None

    img = Image.open(image_field)

    # Convert to RGB if needed
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Resize image
    img = img.resize((width, height), Image.LANCZOS)

    # Save image to memory
    output = BytesIO()

    # Preserve extension if possible
    ext = os.path.splitext(image_field.name)[1].lower()

    if ext in [".jpg", ".jpeg"]:
        img.save(output, format="JPEG", quality=90)
    elif ext == ".png":
        img.save(output, format="PNG")
    else:
        img.save(output, format="JPEG", quality=90)
        ext = ".jpg"

    output.seek(0)

    filename = (
        f"{os.path.splitext(os.path.basename(image_field.name))[0]}"
        f"_{width}x{height}{ext}"
    )

    return ContentFile(output.read(), name=filename)

def generate_random_number(length):
    """
    Generate a random number string of the specified length.

    Example:
        generate_random_number(6)
        # '483920'
    """
    if length <= 0:
        raise ValueError("Length must be greater than 0")

    return ''.join(str(random.randint(0, 9)) for _ in range(length))

def rand_string_generator(size=5, chars=string.ascii_lowercase + string.digits):
     """
     used to generate random  string with a given lenght.
     """
     return ''.join(random.choice(chars) for _ in range(size))

def get_exchange_rates(base_currency="USD"):
    try:
        response = requests.get(
            f"https://open.er-api.com/v6/latest/{base_currency}",
            timeout=5
        )

        response.raise_for_status()  # Raises an exception for 4xx or 5xx responses

        data = response.json()

        return data.get("rates", {})

    except requests.exceptions.RequestException as e:
        print(f"Exchange rate request failed: {e}")
        return {}

    except ValueError:
        print("Invalid JSON response received.")
        return {}
    
def get_total_balance_usd(user):
    rates = get_exchange_rates()

    accounts = models.Account.objects.filter(user=user)

    total = Decimal("0")

    if accounts:
        for account in accounts.all():
            if account.currencyName == "USD":
                total += account.balance
            else:
                rate = Decimal(str(rates[account.currencyName]))
                total += account.balance / rate

    else:
        total = 0

    return total
