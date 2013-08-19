'use strict';

function NetworkListCtrl($scope, Network){
    $scope.networks = Network.query();
}
