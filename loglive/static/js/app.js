'use strict';

angular.module('loglive', ['logliveServices', 'ngRoute']).
    config(['$routeProvider', function($routeProvider){
    $routeProvider.
        when('/networks', {templateUrl: '/static/partials/network-list.html', controller: NetworkListCtrl}).
        otherwise({redirectTo: '/networks'});
}]);
