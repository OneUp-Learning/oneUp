from Instructors.lupaQuestion import LupaRuntimeLink

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from oneUp.decorators import instructorsCheck
@login_required
@user_passes_test(instructorsCheck,login_url='/oneUp/students/StudentHome',redirect_field_name='') 
def luaTestView(request):
	context = RequestContext(request)
	context_dict = { } 
	
	lupa = LupaRuntimeLink({},0)
	
	if request.method == 'GET':
		request.session['lupaid'] = lupa.getIdentifier()
		request.session['lupadump'] = lupa.dump()
		context_dict['results'] = ''
		return render_to_response("Instructors/luatest.html",context_dict,context)
	else:
		code = request.POST['code']
		lupa = LupaRuntimeLink.getLinkFromIdAndDump(request.session['lupaid'], request.session['lupadump'])
		action = request.POST['action']
		if action == 'eval':
			results = lupa.eval(code)
		elif action == 'execute':
			lupa.execute(code)
			results = 'It ran!'
		elif action == 'reset':
			lupa.clearCache_FOR_TESTING_ONLY()
			results = 'Cache cleared!'
		context_dict['results'] = results
		request.session['lupaid'] = lupa.getIdentifier()
		request.session['lupadump'] = lupa.dump()
		return render_to_response("Instructors/luatest.html",context_dict,context)
		