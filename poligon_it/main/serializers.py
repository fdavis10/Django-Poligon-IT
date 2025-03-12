from rest_framework import serializers
from .models import Product, Category, Subcategory_1


class CategorySerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image']
    
    def get_absolute_url(self, obj):
        return obj.get_absolute_url()

class SubcategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    absolute_url = serializers.SerializerMethodField()

    class Meta:
        model = Subcategory_1
        fields = ['id', 'name', 'slug', 'category']

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    subcategory_1 = SubcategorySerializer(read_only=True)
    absolute_url = serializers.SerializerMethodField()


    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'available', 'available_quantity',
            'image_1', 'image_2', 'image_3', 'video', 'category', 'subcategory_1',
            'specifications', 'complectation', 'certificate_diller', 'guarantee',
            'created', 'updated'
        ]
    
    def get_absolute_url(self, obj):
        return obj.get_absolute_url()
    
