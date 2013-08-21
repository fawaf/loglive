'use strict';

angular.module('loglive', ['ngRoute', 'logliveServices', 'logliveFilters', 'logliveDirectives']).
    config(['$routeProvider', function($routeProvider){
    $routeProvider.
        when('/networks', {templateUrl: '/static/partials/network-list.html', controller: NetworkListCtrl}).
        when('/networks/:networkName', {templateUrl: '/static/partials/network-detail.html', controller: NetworkDetailCtrl}).
        when('/networks/:networkName/:channelName', {templateUrl: '/static/partials/channel-detail.html', controller:ChannelDetailCtrl}).
        otherwise({redirectTo: '/networks'});
}]);
