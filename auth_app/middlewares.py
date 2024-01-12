from django.shortcuts import redirect

#---------Authendication --------------------
def auth(view_function):
    def wrapped_view(request,*args,**kwarg):
        if request.user.is_authenticated == False:
            return redirect('login_user')
        return view_function(request,*args,**kwarg)
    return wrapped_view


#--------------Guest-----------------
def guest(view_function):
    def wrapped_view(request,*args,**kwarg):
        if request.user.is_authenticated:
            return redirect('wood_scaling_list')
        return view_function(request,*args,**kwarg)
    return wrapped_view