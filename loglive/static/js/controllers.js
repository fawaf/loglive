'use strict';

function NetworkListCtrl($scope, Network){
    $scope.networks = Network.query();
}

function NetworkDetailCtrl($scope, $routeParams, Network){
    $scope.networks = Network.query();
    $scope.network = Network.get({networkName: $routeParams.networkName});
}
