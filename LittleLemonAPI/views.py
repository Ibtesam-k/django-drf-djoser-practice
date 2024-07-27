import datetime
import json
from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse
from rest_framework.decorators import api_view, permission_classes,throttle_classes
from rest_framework.response import Response
from rest_framework import generics
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage
from rest_framework.throttling import UserRateThrottle
# Create your views here.
def welcome(request):
    return HttpResponse( 'Hello!')

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def menu_items(request):
    isManager = request.user.groups.filter(name='Manager').exists()
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        category_name = request.query_params.get('category')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage',default=2)
        page = request.query_params.get('page',default=1)
        if category_name :
            items = items.filter(category__title = category_name)
        if ordering:
            ordering_fields = ordering.split(',')
            items = items.order_by(*ordering_fields)
        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
        serialized_items = MenuItemSerializer(items,many = True)
        return Response(serialized_items.data , status.HTTP_200_OK)
    if request.method == 'POST' and isManager:
        deserialized_item = MenuItemSerializer(data = request.data)
        print("request serializer input",request.data)
        deserialized_item.is_valid(raise_exception=True)
        deserialized_item.save()
        return Response(deserialized_item.data, status.HTTP_201_CREATED)
    return Response({"message":"You are not authorized"},status.HTTP_403_FORBIDDEN)


@api_view(['GET','PUT','PATCH','DELETE'])
@permission_classes([IsAuthenticated])
def single_item(request, id):
    isManager = request.user.groups.filter(name='Manager').exists()
    item = get_object_or_404(MenuItem,pk=id) 
    if request.method == 'GET':
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data)
    if  request.method == 'PUT' and isManager:
        deserialized_item = MenuItemSerializer(item, data=request.data) 
        deserialized_item.is_valid(raise_exception=True)
        deserialized_item.save()
        return Response(deserialized_item.data)
    if  request.method == 'PATCH' and isManager:
        deserialized_item = MenuItemSerializer(item, data=request.data, partial = True) 
        deserialized_item.is_valid(raise_exception=True)
        deserialized_item.save()
        return Response(deserialized_item.data)
    if request.method == 'DELETE' and isManager:
        item.delete()
        return Response({"details":"object has been deleted"})
    return Response({"message":"You are not authorized"},status.HTTP_403_FORBIDDEN)


from django.contrib.auth.models import Group

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def managers(request):
    isManager = request.user.groups.filter(name='Manager').exists()
    if request.method == 'GET' and isManager:
       managers = User.objects.filter(groups__name='Manager')
       serialized_items = UserSerializer(managers, many=True)
       return Response(serialized_items.data)
    if request.method == 'POST' and isManager:
       requestUsername = request.POST['username']
       my_group = Group.objects.get(name='Manager') 
       selectedUser =  get_object_or_404(User,username=requestUsername) 
       my_group.user_set.add(selectedUser)
       return Response({"message":"user assigned to group"},status.HTTP_201_CREATED)
    return Response({"message":"You are not authorized"},status.HTTP_403_FORBIDDEN)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def manager(request,id):
    isManager = request.user.groups.filter(name='Manager').exists()
    if isManager:
       my_group = Group.objects.get(name='Manager') 
       selectedUser =  get_object_or_404(User,pk=id) 
       my_group.user_set.remove(selectedUser)
       return Response({"message":"user removed from group"},status.HTTP_200_OK)
    return Response({"message":"You are not authorized"},status.HTTP_403_FORBIDDEN)

#/api/groups/delivery-crew/users

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def delivery_crew(request):
    isManager = request.user.groups.filter(name='Manager').exists()
    if request.method == 'GET' and isManager:
       delivery_crew = User.objects.filter(groups__name='Delivery Crew')
       serialized_items = UserSerializer(delivery_crew, many=True)
       return Response(serialized_items.data)
    if request.method == 'POST' and isManager:
       requestUsername = request.POST['username']
       my_group = Group.objects.get(name='Delivery Crew') 
       selectedUser =  get_object_or_404(User,username=requestUsername) 
       my_group.user_set.add(selectedUser)
       return Response({"message":"user assigned to group"},status.HTTP_201_CREATED)
    return Response({"message":"You are not authorized"},status.HTTP_403_FORBIDDEN)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delivery_person(request,id):
    isManager = request.user.groups.filter(name='Manager').exists()
    if isManager:
       my_group = Group.objects.get(name='Delivery Crew') 
       selectedUser =  get_object_or_404(User,pk=id) 
       my_group.user_set.remove(selectedUser)
       return Response({"message":"user removed from group"},status.HTTP_200_OK)
    return Response({"message":"You are not authorized"},status.HTTP_403_FORBIDDEN)


@api_view(['GET','POST','DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def cart_items(request):
    isManager = request.user.groups.filter(name = 'Manager').exists()
    isDelivey = request.user.groups.filter(name = 'Delivery Crew').exists()
    if (not isManager) and (not isDelivey):
        if request.method == 'GET':
            itemsInCart = Cart.objects.filter(user= request.user).all()
            serialized_items = CartSeriallizer(itemsInCart,many =True)
            return Response(serialized_items.data,status.HTTP_200_OK)
        if request.method == 'POST':
            menuitem_id = request.POST['menuitem_id']
            quantity = request.POST['quantity']
            menuitem =get_object_or_404(MenuItem,pk = menuitem_id)
            cartItem = Cart(user = request.user, menuitem = menuitem , unit_price = menuitem.price, quantity = quantity,price = float(menuitem.price)*int(quantity))           
            try :
                cartItem.save()
                return Response({"message":"item added to the cart"},status.HTTP_200_OK)
            except Exception as e:
                return Response({"message":str(e)},status.HTTP_400_BAD_REQUEST)
        if request.method =='DELETE':
            cuurentUser = request.user
            Cart.objects.filter(user = cuurentUser).delete()
            return Response({"message":"cart items delelted"},status.HTTP_200_OK) 
    else:
        return Response({"message":"You are not authorized"},status.HTTP_403_FORBIDDEN)
    
    
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def orders(request):
    isManager = request.user.groups.filter(name = 'Manager').exists()
    isDelivery = request.user.groups.filter(name = 'Delivery Crew').exists()
    isCustomer = False
    if (not isManager) and (not isDelivery):
        isCustomer = True
    if request.method == 'GET':
        ordering = request.query_params.get('ordering')
        to_price = request.query_params.get('to_price')
        status = request.query_params.get('status')
        perpage = request.query_params.get('perpage',default=2)
        page = request.query_params.get('page',default=1)
        if isCustomer:
            try:
                orders = Order.objects.filter(user = request.user).all()
            except:
                 raise Http404
        elif isManager:
                orders = Order.objects.all()
        elif isDelivery :
                orders = Order.objects.filter(delivery_crew = request.user).all()
        if to_price :
            orders = orders.filter(total__lte = to_price)
        if status :
            orders = orders.filter(status = status)
        if ordering:
            ordering_fields = ordering.split(',')
            orders = orders.order_by(*ordering_fields)
        paginator = Paginator(orders, per_page=perpage)
        try:
            orders = paginator.page(number=page)
        except EmptyPage:
            orders = []
        serializeredItems = OrderSerializer(orders, many = True)
        return Response(serializeredItems.data)
    if request.method == 'POST' and isCustomer:
        customerOrder = Order(user = request.user, status = 0 , total = 0, date = datetime.datetime.now())
        cartItems = Cart.objects.filter(user = request.user)
        total = 0
        orders = []        
        for item in cartItems:
            orderItem = OrderItem(menuitem = item.menuitem, quantity = item.quantity, unit_price = item.menuitem.price,price= float(item.unit_price)*int(item.quantity),order = customerOrder)
            total = total + orderItem.price
            orders.append(orderItem)
        customerOrder.total = total
        customerOrder.save()
        for o in orders:
            o.save()
        cartItems.delete()
        return Response({"message":"ok"})
    return Response({"message":"you are not authorized"},status.HTTP_403_FORBIDDEN)

@api_view(['GET','PUT','PATCH','DELETE'])
def single_order(request,id):
    isManager = request.user.groups.filter(name = 'Manager').exists()
    isDelivery = request.user.groups.filter(name = 'Delivery Crew').exists()
    isCustomer = False
    if (not isManager) and (not isDelivery):
        isCustomer = True
    if request.method == 'GET' and isCustomer:
        queryset = Order.objects.filter(user=request.user)
        cutomerOrder= get_object_or_404(queryset, pk=id)
        serializedItem = OrderSerializer(cutomerOrder )
        return Response(serializedItem.data)
    if  request.method == 'PUT'  and isManager:
        customerOrder = get_object_or_404(Order,pk = id)
        deserialized_item = OrderSerializer(customerOrder, data=request.data) 
        deserialized_item.is_valid(raise_exception=True)
        deserialized_item.save()
        return Response(deserialized_item.data)
    if  request.method == 'PATCH'  and isManager:
        customerOrder = get_object_or_404(Order,pk = id)
        deserialized_item = OrderSerializer(customerOrder, data=request.data, partial = True) 
        deserialized_item.is_valid(raise_exception=True)
        deserialized_item.save()
        return Response(deserialized_item.data)    
    if request.method == 'DELETE' and isManager :
        customerOrder = get_object_or_404(Order,pk = id)
        customerOrder.delete()
        return Response({"message":"order deleted"})
    if  request.method == 'PATCH'  and isDelivery:
        customerOrder = get_object_or_404(Order,pk = id)
        deserialized_item = OrderSerializer(customerOrder, data=request.data, partial = True) 
        deserialized_item.is_valid(raise_exception=True)
        deserialized_item.save()
        return Response(deserialized_item.data)
    return Response({"message":"You are not authorized"},status.HTTP_403_FORBIDDEN)
