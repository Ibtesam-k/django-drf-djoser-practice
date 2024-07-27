from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','title','slug']
    
class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = serializers.SlugRelatedField(read_only = True,slug_field='title')
    title = serializers.CharField()
    class Meta:
        model = MenuItem
        fields = ['id','title','price','featured','category','category_id']


class UserSerializer(serializers.ModelSerializer):
      class Meta:
          model = User
          fields= ['id','username','email']
        
class CartSeriallizer(serializers.ModelSerializer):
    cart_item_id = serializers.IntegerField(source = 'id')
    menuitem_id = serializers.IntegerField(write_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    user = serializers.SlugRelatedField(read_only = True, slug_field="username")
    price = serializers.SerializerMethodField(method_name='calculate_price',read_only = True)
    unit_price = serializers.SerializerMethodField(method_name='get_unit_price',read_only = True)
    class Meta:
        model = Cart
        fields = ['cart_item_id','user','unit_price','quantity','price','menuitem_id','menuitem']
    def calculate_price (self,product:Cart):
        return  float(product.unit_price)* int(product.quantity)
    def get_unit_price (self,product:Cart):
        return  product.menuitem.price


class OrderItemSerializer(serializers.ModelSerializer):
    order_item_id = serializers.IntegerField(source = 'id')
    unit_price = serializers.SerializerMethodField(method_name='get_unit')
    price  = serializers.SerializerMethodField(method_name='get_price')
    menuitem = serializers.SlugRelatedField(read_only = True, slug_field="title")
    menuitem_id = serializers.IntegerField(write_only = True)
    class Meta:
        model = OrderItem
        fields =  ['order_item_id','unit_price','quantity','price','menuitem_id','menuitem']
    def get_price(self, item: OrderItem):
        return item.menuitem.price * item.quantity
    def get_unit(self, item: OrderItem):
        return item.menuitem.price 


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    order_id = serializers.IntegerField(source = 'id',read_only= True)
    user = serializers.SlugRelatedField(read_only = True, slug_field="username")
    delivery_crew = serializers.SlugRelatedField( slug_field="username",queryset=User.objects.filter(groups__name='Delivery Crew') )
    total = serializers.DecimalField(max_digits=6,decimal_places=2,read_only = True)
    date = serializers.DateField(read_only = True)
    class Meta:
        model = Order
        fields = ['order_id','user','delivery_crew','status','total','date','order_items']


