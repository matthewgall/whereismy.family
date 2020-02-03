% include('global/header.tpl', title=username)
% include('user/map.tpl')
<div class="container">
	<div class="template">
		<div class="well well-sm">
			<h1>{{username}}</h1>
			<h3 id="display_name">{{data['display_name']}}</h3>
			<h4 id="delta">
				<i class="fa fa-clock-o" aria-hidden="true"></i>&nbsp;{{data['delta']}}
			</h4>
			% if not args.w3w == "":
				<h5 id="w3w">
					<a href="https://what3words.com/{{data['w3w']}}" target="_blank">{{data['w3w']}}</a>
				</h5>
			% end
		</div>
	</div>
</div>
% include('global/footer.tpl')
