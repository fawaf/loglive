'use strict';

function NetworkListCtrl($scope, Network){
    $scope.networks = Network.query();
}

function NetworkDetailCtrl($scope, $routeParams, Network){
    $scope.networks = Network.query();
    $scope.network = Network.get({networkName: $routeParams.networkName});
}

function ChannelDetailCtrl($scope, $routeParams, Network, Channel, $anchorScroll, $location){
    $scope.networks = Network.query();
    $scope.network = Network.get({networkName: $routeParams.networkName});
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
