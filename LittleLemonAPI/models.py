from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255,db_index=True)
    class Meta:
        verbose_name_plural = "categories"
    def __str__(self) -> str:
        return self.title
class MenuItem(models.Model):
    title = models.CharField(max_length=256,db_index=True)
    price = models.DecimalField(max_digits=6,decimal_places=2,db_index=True)
    featured = models.BooleanField(db_index=True)
    category = models.ForeignKey(Category,on_delete=models.PROTECT)
    def __str__(self) -> str:
        return "item#"+str(self.id)+" ("+self.title+")"

class Cart(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem,on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6,decimal_places=2)
    price = models.DecimalField(max_digits=6,decimal_places=2)
    class Meta:
        unique_together = ('menuitem','user')
    def __str__(self) -> str:
        return  str(self.menuitem)+" "+self.user.username+"'s Cart"
    
    
    
class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(User,on_delete=models.SET_NULL,related_name="delivery_crew",null=True,blank=True)
    status = models.BooleanField(db_index=True,default=0)
    total = models.DecimalField(max_digits=6,decimal_places=2)
    date = models.DateField(db_index=True)
    def __str__(self) -> str:
        return "Order#"+str(self.id)+" for "+self.user.username
    
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE, related_name="order_items")
    menuitem = models.ForeignKey(MenuItem,on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2  )
    price = models.DecimalField(max_digits=6, decimal_places=2  )
    class Meta:
        unique_together = ('order','menuitem')
    def __str__(self) -> str:
        return str(self.menuitem)+" in Order#"+str(self.order.id)+" for "+self.order.user.username