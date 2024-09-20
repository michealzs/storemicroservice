import requests
import json
from .models import Product, ProductVariant, ProductImage, Category
from django.utils.text import slugify
from django.db import transaction

class ShopifyAPI:
    def __init__(self, shop_name, access_token, collection_id):
        self.shop_name = shop_name
        self.access_token = access_token
        self.collection_id  = collection_id 
        self.base_url = f"https://{self.shop_name}.myshopify.com/admin/api/2024-07"

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'X-Shopify-Access-Token': self.access_token
        }

    def get_products(self):
        url = f"{self.base_url}/products.json"
        response = requests.get(url, headers=self.get_headers())
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to retrieve data: {response.status_code} {response.text}")

    def create_order(self, order_data):
        url = f"{self.base_url}/orders.json"
        response = requests.post(url, headers=self.get_headers(), data=json.dumps(order_data))
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create order: {response.status_code} {response.text}")

    @transaction.atomic
    def load_products(self):
        # Securely obtain sensitive data
        shop = self.shop_name  # Ensure this is set through initialization or env variables
        access_token = self.access_token
        collection_id = self.collection_id   # Consider passing this as a parameter if dynamic

        url = f"https://{shop}.myshopify.com/admin/api/2024-07/products.json"
        params = {
            "collection_id": collection_id
        }

        response = requests.get(url, headers=self.get_headers(), params=params)

        if response.status_code == 200:
            data = response.json()

            # Extract and parse product details
            for product_data in data.get('products', []):
                shopify_id = product_data['id']
                name = product_data['title']
                vendor = product_data['vendor']
                description = product_data['body_html']
                slug = slugify(name)
                tags = product_data['tags']  # Shopify tags to be used as categories

                product, created = Product.objects.update_or_create(
                    shopify_id=shopify_id,
                    defaults={
                        'name': name,
                        'slug': slug,
                        'vendor': vendor,
                        'description': description,
                        'price': product_data['variants'][0]['price'],
                        'discount_price': product_data['variants'][0].get('compare_at_price', 0.00),
                    }
                )

                # Handle tags as categories
                tag_list = tags.split(",")
                for tag in tag_list:
                    category_name = tag.strip()
                    category_slug = slugify(category_name)

                    category, _ = Category.objects.update_or_create(
                        name=category_name,
                        defaults={
                            'slug': category_slug,
                            'description': f"Category for {category_name}",
                            'meta_keywords': category_name,
                            'meta_description': f"{category_name} meta description",
                        }
                    )

                    product.categories.add(category)

                # Extract and save variants
                for variant_data in product_data['variants']:
                    variant_id = variant_data['id']
                    variant_title = variant_data['title']
                    variant_price = variant_data['price']
                    compare_at_price = variant_data.get('compare_at_price')
                    inventory_quantity = variant_data['inventory_quantity']

                    ProductVariant.objects.update_or_create(
                        variant_id=variant_id,
                        product=product,
                        defaults={
                            'title': variant_title,
                            'price': variant_price,
                            'compare_at_price': compare_at_price,
                            'inventory_quantity': inventory_quantity,
                        }
                    )

                # Extract and save images
                for image_data in product_data['images']:
                    image_url = image_data['src']
                    variant_ids = image_data.get('variant_ids', [])

                    for variant_id in variant_ids:
                        variant = ProductVariant.objects.filter(variant_id=variant_id, product=product).first()

                        # Create image only if it doesn't already exist
                        ProductImage.objects.get_or_create(
                            product=product,
                            image_url=image_url,
                            variant=variant
                        )

                print(f"{'Created' if created else 'Updated'} product: {product.name}")

        else:
            print(f"Error: {response.status_code}, {response.text}")