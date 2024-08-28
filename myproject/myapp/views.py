import datetime

from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from django.db.models import Sum,Count,F
from django.http import HttpResponse
from django.views.generic import TemplateView, View, CreateView, DetailView,FormView,ListView
# import generic UpdateView
from django.views.generic.edit import DeleteView

from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import *
from .forms import *



class UserRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            pass
        else:
            return redirect('myapp:UserLoginView')
        return super().dispatch(request, *args, **kwargs)


class UserLoginView(FormView):
    template_name = 'shop/login.html'
    form_class = ULoginForm
    success_url = reverse_lazy('myapp:shopview')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data['password']
        usr = authenticate(username=username, password=password)

        if usr is not None:
            login(self.request, usr)

        else:
            # fm = RegisterForm()
            return render(self.request, self.template_name, {'form': self.form_class, 'error': 'Invalid user login!', })
        return super().form_valid(form)

class UserLogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('myapp:UserLoginView')


def register(response):
    if response.method == "POST":
	    form = RegisterForm(response.POST)
	    if form.is_valid():
	        form.save()

	        return redirect("/")
    else:
	    form = RegisterForm()
    return render(response, "shop/register.html", {"form":form})


class register_customer(View):
    def get(self, request):
        fullname = request.GET.get('fullname')
        uname = request.GET.get('uname')
        regpass = request.GET.get('regpass')
        usr = User.objects.create(username=uname, password=regpass, first_name=fullname)
        print('register_customer')
        return JsonResponse({'status':'user adding successfully'})


# Banckend

class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            pass
        else:
            return redirect('myapp:AdminLoginView')
        return super().dispatch(request, *args, **kwargs)

class AdminLoginView(FormView):
    template_name = 'shopadmin/login.html'
    form_class = ULoginForm
    success_url = reverse_lazy('myapp:DashboardView')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data['password']
        usr = authenticate(username=username, password=password)

        if usr is not None:
            login(self.request, usr)

        else:
            return render(self.request, self.template_name, {'form': self.form_class, 'error': 'Invalid user login!'})
        return super().form_valid(form)


class DashboardView(AdminRequiredMixin,View):
    def get(self, request):
        usr = User.objects.all()
        usrcount = usr.count()
        order = Order.objects.filter(status=0).count()
        visitor = Order.objects.all().count()
        queryset = Order.objects.all()
        ord_history = Order.objects.all().order_by('status')[0:10]
        sum = queryset.aggregate(Sum('total'))['total__sum']
        context = {'usr':usr, 'usrcount':usrcount, 'order':order ,'visitor':visitor, 'sum':sum, 'ord_history':ord_history}
        return render(request, 'shopadmin/dashboard.html', context)
    

class AdminTemplate(TemplateView):
    template_name = "shopadmin/base.html"

class itemcreateview(CreateView):
    # model = item
    template_name = "shopadmin/itemcreate.html"
    form_class = itemcreateform
    success_url = reverse_lazy('myapp:itemcreateview')


class color_and_size(View):
    def get(self, request):
        itm = item.objects.all()
        context = {'itm':itm}
        return render(request, 'shopadmin/color_size.html', context)

class add_color(View):
    def get(self, request):
        itm = int(request.GET.get('itm'))
        icol = request.GET.get('icol')
        itm_obj = item.objects.get(id=itm)
        addcolor = ItmColor(items=itm_obj, color=icol)
        addcolor.save()
        return JsonResponse({'status':'add color successfully'})

class add_size(View):
    def get(self, request):
        itm = int(request.GET.get('itm'))
        isize = request.GET.get('isize')
        itm_obj = item.objects.get(id=itm)
        size = ItmSize(items=itm_obj, size=isize)
        size.save()
        return JsonResponse({'status':'adding item size successfully'})


class itemview(View):
    def get(self, request):
        itm = item.objects.all()
        form = itemcreateform()
        context = {'itm':itm, 'form':form}
        return render(request, 'shopadmin/itemcreate.html', context)

    def post(self, request):
        itemname = request.POST.get('itemname')
        cat = request.POST.get('category')
        price = request.POST.get('price')
        description = request.POST.get('description')
        photo1 = request.FILES['photo1']
        photo2 = request.FILES['photo2']
        photo3 = request.FILES['photo3']
        photo4 = request.FILES['photo4']

        cate = category.objects.get(id=int(cat))

        itm = item(itemname=itemname, category=cate, price=price, description=description, photo1=photo1, photo2=photo2, photo3=photo3, photo4=photo4)
        itm.save()
        
        return redirect('myapp:itemview')


class categoryview(View):
    def get(self, request):
        ct = category.objects.all()
        form = categoryform()
        context = {'ct':ct, 'form':form}
        return render(request, 'shopadmin/categoryview.html', context)

    def post(self, request):
        categoryname = request.POST.get('categoryname')
        c = category(categoryname=categoryname)
        c.save()
        return redirect('myapp:categoryview')


class orderlistview(View):
    def get(self, request):
        ord = Order.objects.filter(status=0)
        allord = Order.objects.filter(status=1)
        context = {'ord':ord, 'allord':allord}
        return render(request, 'shopadmin/orderlistview.html', context)
        

class OrderDetailView(AdminRequiredMixin,DetailView):
    template_name = 'shopadmin/OrderDetailView.html'
    model = Order
    context_object_name = 'ord_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['allstatus'] = STATUS

        return context


class order_status_change(View):
    def get(self, request):
        ordid = int(request.GET.get('ordid'))
        upt = Order.objects.filter(id=ordid).update(status=1)
        return JsonResponse({'status':'success'})


# shop
class shopview(View):
    def get(self, request):
        itm = item.objects.all()
        cate = category.objects.all()
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            ccnt = CartProduct.objects.filter(cart=cart).count()
        else:
            cart = None
            ccnt = 0
        context = {'item': itm, 'cate': cate,'cart':cart, 'ccnt':ccnt}
        return render(request, 'shop/shopview.html', context)

    def post(self, request):
        pass


class productdetail(View):
    def get(self, request, pk):
        itm = item.objects.get(id=pk)
        icol = ItmColor.objects.filter(items=itm)
        isize = ItmSize.objects.filter(items=itm)

        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            ccnt = CartProduct.objects.filter(cart=cart).count()
        else:
            cart = None
            ccnt = 0
        
        context = {'itm':itm, 'icol':icol, 'isize':isize, 'cart':cart, 'ccnt':ccnt}
        return render(request, 'shop/product-detail.html', context)


class cartview(UserRequiredMixin,View):
    def get(self, request):
        cart_id = self.request.session.get('cart_id', None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            ccnt = CartProduct.objects.filter(cart=cart).count()
        else:
            cart = None
            ccnt = 0
        
        context = { 'cart':cart, 'ccnt':ccnt}
        return render(request, 'shop/cartview.html', context)


class cart_change_qty(View):
    def get(self, request):
        cpid = int(request.GET.get('cpid'))
        cartid = int(request.GET.get('cartid'))
        a3 = int(request.GET.get('a3'))

        cart = Cart.objects.get(id=cartid)
        cp = CartProduct.objects.get(id=cpid)

        stotal = cp.rate * a3
        cp_update = CartProduct.objects.filter(id=cpid)
        upt= cp_update.update(quantity=a3, subtotal=stotal)

        ctotal = cart.total - cp.subtotal
        upt_total = ctotal + stotal
        cart_upt = Cart.objects.filter(id=cartid).update(total=upt_total)


        
        return JsonResponse({'status':'success'})



class addtocart(View):
    def get(self, request):
        itmid = request.GET.get('itmid')
        isize = request.GET.get('isize')
        icl = request.GET.get('icl')
        qty = request.GET.get('qty')
        iid = int(itmid)
        iqty = int(qty)
        # get item 
        itm = item.objects.get(id=iid)
        itm_id = itm.id
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            # print('card id have')
            this_product_in_cart = cart_obj.cartproduct_set.filter(product=itm)
                # Product already exists in cart
            if this_product_in_cart.exists():
                
                return JsonResponse({'status':'Item Already Existed in Cart......'})    
            else:
                stotal = int(itm.price) * int(iqty)
            
                cartproduct = CartProduct.objects.create(cart=cart_obj, product=itm,
                                                         rate=itm.price,
                                                         color = icl,
                                                         size = isize,
                                                         quantity=iqty, subtotal=stotal,
                                                        )
                cart_obj.total += stotal
                cart_obj.save()
                return JsonResponse({'status':'Your Item -> Add to Cart Success'})
            
        else:
            cart_obj = Cart.objects.create(total=0, usr=request.user)
            self.request.session['cart_id'] = cart_obj.id
            stotal = int(itm.price) * int(iqty)
            
            cartproduct = CartProduct.objects.create(cart=cart_obj, product=itm,
                                                         rate=itm.price,
                                                         color = icl,
                                                         size = isize,
                                                         quantity=iqty, subtotal=stotal,
                                                        )
            # print('cart create')
            cart_obj.total += stotal
            cart_obj.save()
        # print(cart_id)
            return JsonResponse({'status':'Item Create in Your Cart....'})


class send_order_to_admin(View):
    def get(self, request):
        oid = int(request.GET.get('oid'))
        phone = request.GET.get('phone')
        caddress = request.GET.get('caddress')

        cart_obj = Cart.objects.get(id=oid)
        total = cart_obj.total
        # print(total)
        ord = Order.objects.create(cart= cart_obj, mobile=phone , shipping_address= caddress, total= total)
        del self.request.session['cart_id']
        return JsonResponse({'status':'success'})


