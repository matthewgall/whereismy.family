% include('global/header.tpl', title=username)
% include('user/map.tpl')
<div class="container">
	<div class="template">
		<h1>{{username}}</h1>
		<h3>{{data['display_name']}}</h3>
		<h4>{{data['delta']}}</h4>
		% if not args.w3w_token == "":
			<h5>{{get('w3w')}}</h5>
		% end
	</div>
</div>
% include('global/footer.tpl')