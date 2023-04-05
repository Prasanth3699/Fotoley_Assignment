from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.db.models import Q

def home(request):
    return render(request, 'index.html')

def signup(request):
    if request.method != 'POST':
        return render(request, "signup.html")
    else:
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_type = request.POST.get("userType")
        try:
            if user_type == "premium":
                user = User.objects.create_user(username=username, password=password, user_type=1)
                user.save()
                messages.success(request, "Successfully Created Premium User")
                return HttpResponseRedirect(reverse("login"))
            else:
                user = User.objects.create_user(username=username, password=password, user_type=2)
                user.save()
                messages.success(request, "Successfully Created Non-Premium User")
                return HttpResponseRedirect(reverse("login"))

        except:
            messages.error(request, "Failde To Create User")
            return HttpResponseRedirect(reverse("login"))
    return render(request, "signup.html")

# User login
def user_login(request):
    if request.method != 'POST':
        return render(request, "login.html")

    else:
        name = request.POST.get("name")
        password = request.POST.get("password")
        user = authenticate(username=name,password=password)
        login(request,user)
        return HttpResponseRedirect(reverse("home"))
           
def logout_user(request):
        logout(request)
        return HttpResponseRedirect("/")

# Wallet function
def wallet(request):
    data = Wallet.objects.get(user=request.user)
    history = Transaction.objects.filter(user=request.user).order_by('-id')  
    return render(request, 'wallet.html', {'data':data, 'history':history})

@login_required
def sendMoney(request):
    userdata = User.objects.all().exclude(is_superuser=True)
    if request.method == 'POST':
        receiver_name = User.objects.get(username=request.POST['receiver'])
        amount = Decimal(request.POST['amount'])
        sender = Wallet.objects.filter(user=request.user).last()
        receiver = Wallet.objects.filter(user=receiver_name).last()

        # checking available balance
        if sender.balance >= amount:
            sender_transaction_fee = 0
            # checking user type
            if request.user.user_type == '1':
                sender_transaction_fee = amount * Decimal('0.03')
                sender.balance -= amount + sender_transaction_fee
                receiver.balance += amount
                sender.save()
                receiver.save()

            elif request.user.user_type == '2':
                sender_transaction_fee = amount * Decimal('0.05')
                sender.balance -= amount + sender_transaction_fee
                receiver.balance += amount
                sender.save()
                receiver.save()

            # update transaction
            message = f'Amount sent to {receiver_name} and the Transaction Fee is {sender_transaction_fee}'
            update_sender = Transaction.objects.create(user=request.user, sender=request.user, receiver=receiver_name, amount=amount, message=message, balance=sender.balance, transaction_type='Debit', transaction_amount = amount,transaction_fee=sender_transaction_fee, status='Success')
            update_sender.save()    

            # Receiver data update 
            receiver_transaction_fee = 0
            if receiver_name.user_type == '1':
                receiver_transaction_fee = amount * Decimal('0.01')
                receiver.balance -= receiver_transaction_fee
                receiver.save()
            elif receiver_name.user_type == '2':
                receiver_transaction_fee = amount * Decimal('0.03')
                receiver.balance -= receiver_transaction_fee
                receiver.save()

             # update transaction
            message = f'Amount Received by {request.user} and the Transaction Fee is {receiver_transaction_fee}'
            update_receiver = Transaction.objects.create(user=receiver_name, sender=request.user, receiver=receiver_name, amount=amount, message=message,balance=receiver.balance, transaction_type='Credit', transaction_amount = amount, transaction_fee=receiver_transaction_fee, status='Success')
            update_receiver.save()

            # Credit transaction fee to super user's wallet
            super_user_wallet = Wallet.objects.get(user__is_superuser=True)
            super_user_wallet.balance += sender_transaction_fee
            super_user_wallet.balance += receiver_transaction_fee
            super_user_wallet.save()

            messages.success(request, f'{amount} INR sent to {receiver_name.username} successfully.')
            return redirect('wallet')
        else:
            messages.error(request, 'Insufficient balance.')
    return render(request, 'sendMoney.html',{'userdata':userdata})


@login_required
def requestMoney(request):
    userdata = User.objects.all().exclude(is_superuser=True)
    if request.method == 'POST':
        receiver = User.objects.get(username=request.POST['receiver'])
        amount = Decimal(request.POST['amount'])
        sender_wallet = Wallet.objects.get(user=request.user)
        receiver_wallet = Wallet.objects.get(user=receiver)

        sender_transaction_fee = 0
        if request.user.user_type == '1':
            sender_transaction_fee = amount * Decimal('0.03')

        elif request.user.user_type == '2':
            sender_transaction_fee = amount * Decimal('0.05')

        # update transaction
        message = f'Requset sent to the {receiver}'
        update_sender = Transaction.objects.create(user=request.user, sender=request.user, receiver=receiver, amount=amount, message=message, balance=sender_wallet.balance, transaction_type='Request', transaction_amount = amount,transaction_fee=sender_transaction_fee, is_request=True, status='Pending')
        update_sender.save() 
      
        messages.success(request, f'{amount} INR requested from {receiver.username} successfully.')
        return redirect('wallet')
    return render(request, 'requestMoney.html',{'userdata':userdata})


@login_required
def acceptRequest(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    sender = Wallet.objects.filter(user=transaction.receiver).last()
    receiver = Wallet.objects.filter(user=transaction.sender).last()

    # verifying User
    if transaction.receiver == request.user:
        if sender.balance >= transaction.amount:
            sender_transaction_fee = 0
            transaction.is_accepted = True
            transaction.is_request =False

            if sender.user.user_type == '1':
                sender_transaction_fee = transaction.amount * Decimal('0.03')
                sender.balance -= transaction.amount + sender_transaction_fee
                receiver.balance += transaction.amount
                sender.save()
                receiver.save()  

            elif sender.user.user_type == '2':
                sender_transaction_fee = transaction.amount * Decimal('0.05')
                sender.balance -= transaction.amount + sender_transaction_fee
                receiver.balance += transaction.amount
                sender.save()
                receiver.save()

            # update transaction
            message = f'Amount sent to {receiver} and the Transaction Fee is {sender_transaction_fee}'
            update_sender = Transaction.objects.create(user=request.user, sender=transaction.sender, receiver=transaction.receiver, amount=transaction.amount, message=message, balance=sender.balance, transaction_type='Debit', transaction_amount = transaction.amount,transaction_fee=sender_transaction_fee, status='Accepted')
            update_sender.save()    

            # Receiver data update 
            receiver_transaction_fee = 0
            if transaction.receiver.user_type == '1':
                receiver_transaction_fee = transaction.amount * Decimal('0.01')
                receiver.balance -= receiver_transaction_fee
                receiver.save()
            elif transaction.receiver.user_type == '2':
                receiver_transaction_fee = transaction.amount * Decimal('0.03')
                receiver.balance -= receiver_transaction_fee
                receiver.save()
    
            # update transaction
            message = f'Amount Received by {request.user} and the Transaction Fee is {receiver_transaction_fee}'
            update_receiver = Transaction.objects.create(user=transaction.sender, sender=transaction.sender, receiver=transaction.receiver, amount=transaction.amount, message=message, balance=receiver.balance,transaction_type='Credit', transaction_amount = transaction.amount, transaction_fee=receiver_transaction_fee, status='Accepted')
            update_receiver.save()
            transaction.save()

            # Credit transaction fee to super user's wallet
            super_user_wallet = Wallet.objects.get(user__is_superuser=True)
            # super_user_wallet.balance += transaction_fee
            super_user_wallet.balance += sender_transaction_fee
            super_user_wallet.balance += receiver_transaction_fee
            super_user_wallet.save()

    return HttpResponseRedirect(reverse("wallet"))

@login_required
def rejectRequest(request, transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    if transaction.receiver == request.user:
        transaction.is_accepted = True
        transaction.is_request =False
        
        # update transaction
        message = f'Request Rejected by {request.user}'
        update_receiver = Transaction.objects.create(user=transaction.receiver, sender=transaction.sender, receiver=transaction.receiver, amount=transaction.amount, message=message, balance=transaction.amount,transaction_type='None', transaction_amount = transaction.amount, transaction_fee=0, status='Rejected')
        update_receiver.save()
        transaction.save() 
    return HttpResponseRedirect(reverse("wallet"))

def receivedRequest(request):
    data = Wallet.objects.get(user=request.user)
    requested_user = Transaction.objects.filter(Q(is_accepted = False) , receiver=request.user).order_by('-id')
    return render(request, 'receivedRequest.html',{'datas':requested_user, 'data':data})