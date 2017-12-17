% include('global/header.tpl', title=username)
% include('user/map.tpl')
<div class="container">
    <div class="template">
        <h1>{{username}}</h1>
        <div class="well well-lg">
            {{data['display_name']}}
        </div>
    </div>
</div>
% include('global/footer.tpl')