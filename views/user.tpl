% include('global/header.tpl', title=username)
% include('user/map.tpl')
<div class="container">
    <div class="template">
        <h1>{{username}}</h1>
        <h3>{{data['display_name']}}</h3>
        <small>{{data['delta']}}</small>
    </div>
</div>
% include('global/footer.tpl')