% include('global/header.tpl', title='Home')
<div class="container">
    <div class="starter-template">
        <h1>Welcome to whereismy.family</h1>
        <p class="lead">
            Simple privacy aware, OwnTracks powered, location tracking
        </p>
        <p>&nbsp;</p>
        % if args.enable_register:
        <div class="panel panel-primary">
            <div class="panel-heading">
                <h2 class="panel-title">Register</h3>
            </div>
            <div class="panel-body">
            </div>
        </div>
        % end
    </div>
</div>
% include('global/footer.tpl')