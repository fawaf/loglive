'use strict';

function NetworkListCtrl($scope, Network){
    $scope.networks = Network.query();
}

function NetworkDetailCtrl($scope, $routeParams, Network){
    $scope.networks = Network.query();
    $scope.network = Network.get({networkName: $routeParams.networkName});
    $scope.nav_network = $routeParams.networkName;
}

function ChannelDetailCtrl($scope, $routeParams, Network, Channel){
    $scope.networks = Network.query();
    $scope.nav_network = $routeParams.networkName;
    $scope.channel = Channel.get({networkName: $routeParams.networkName,
                                  channelName: $routeParams.channelName}, function(channel){
        $scope.logs = {};
        $scope.latestLog = null;
        for(var i in channel.logs){
            var raw = channel.logs[i];
            var splitted = raw.split("-");
            var log = {raw: raw,
                       year: splitted[0],
                       month: splitted[1],
                       day: splitted[2]};
            if(log.year in $scope.logs == false){
                $scope.logs[log.year] = {};
            }
            if(log.month in $scope.logs[log.year] == false){
                $scope.logs[log.year][log.month] = [];
            }
            $scope.logs[log.year][log.month].push(log);

            // the json from the api returns a sorted list of the logs
            $scope.latestLog = log;
        }
    });
}

function LogDetailCtrl($scope, $routeParams, Network, Channel, Log){
    $scope.networks = Network.query();
    $scope.nav_network = $routeParams.networkName;
    $scope.log = Log.get({networkName: $routeParams.networkName,
                          channelName: $routeParams.channelName,
                          dateString: $routeParams.dateString});

    $scope.lineClasses = function(line){
        var classes = ['irc-line'];
        if(line.type != 'message'){
            classes.push('irc-line-' + line.type);
        }
        return classes;
    };

    $scope.fragmentStateClasses = function(state){
        var classes = [];
        if(state.bold == true){
            classes.push("irc-bold");
        }
        if(state.underline == true){
            classes.push("irc-underline");
        }
        if(state.fg_color != null){
            classes.push("irc-fg-" + state.fg_color);
        }
        if(state.bg_color != null){
            classes.push("irc-bg-" + state.bg_color);
        }
        return classes;
    };

    $scope.b64Decode = function(input){
        if(input == null){
            return '';
        }
        var result = B64.decode(input);
        return result;
    };
}
