from django.test import TestCase
from django.urls import reverse
from .models import Category, Subcategory_1, Subcategory_2, Product, Favorite

class CategoryModelTest(TestCase):
    """ Testing categories of app main """
    def setUp(self):
        self.category = Category.objects.create(name="Сетевые устройства", slug="network-devices")

    def test_category_creation(self):
        """ Testing categories of app main """
        self.assertEqual(self.category.name, 'Сетевые устройства')
        self.assertEqual(self.category.slug, 'network-devices')
    
    def test_category_url(self):
        """ Testing get_absolute_url() in categories """
        self.assertEqual(self.category.get_absolute_url(), "/category/network-devices/")

class ProductModelTest(TestCase):
    def setUp(self):
        """ Testing Product models of app main """
        self.category = Category.objects.create(name="Сетевые устройства", slug="network-devices")
        self.product = Product.objects.create(
            name="Коммутатор TP-Link",
            slug='tp-link-switch',
            category = self.category,
            price=1999.99,
            available=True
        )

    def test_product_creation(self):
        """ Test creation of the product """
        self.assertEqual(self.product.name, 'Коммутатор TP-Link')
        self.assertEqual(self.product.available, True)
    
    def test_product_absolute_url(self):
        """ Testing get_absolute_url() in products """
        self.assertEqual(self.product.get_absolute_url(), "/product/tp-link-switch/")

class ViewTest(TestCase):
    """ Testing views in app main """
    def setUp(self):
        self.category = Category.objects.create(name="Сетевые устройства", slug="network-devices")
        self.product = Product.objects.create(
            name="Коммутатор TP-Link",
            slug='tp-link-switch',
            category = self.category,
            price=1999.99,
            available=True
        )
    
    def test_index_page(self):
        """ Test index_page of app main """
        response = self.client.get(reverse('main:index_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/index/index.html')
    
    def test_product_list_by_category(self):
        """ Test page of product_list by category in app main """
        response = self.client.get(reverse('main:product_list_by_category', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)
    
    def test_detail_product(self):
        """ Test detail product page """
        response = self.client.get(reverse('main:detail_product', args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_favorite_list(self):
        """ test page of favorite list """
        response = self.client.get(reverse('main:favorite_list'))
        self.assertEqual(response.status_code, 200)