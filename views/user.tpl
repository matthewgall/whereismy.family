% include('global/header.tpl', title=username)
<div class="container">
    <div class="starter-template">
        <h1>{{username}}</h1>
        <div class="well well-lg">
            {{data}}
        </div>
    </div>
</div>
% include('global/footer.tpl')