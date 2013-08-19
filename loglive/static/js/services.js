'use strict';

angular.module('logliveServices', ['ngResource']).
factory('Network', function($resource){
    return $resource('/networks/:networkName.json', {networkName: '@id'}, {
    });
});
