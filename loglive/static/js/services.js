'use strict';

angular.module('logliveServices', ['ngResource']).
factory('Network', function($resource){
    return $resource('/api/networks/:networkName.json', {networkName: '@id'}, {
        query: {
            method: 'GET',
            isArray: true,
            transformResponse: function($data, $headersGetter){
                return angular.fromJson($data)['networks'];
            }
        }
    });
}).
factory('Channel', function($resource){
    return $resource('/api/networks/:networkName/:channelName.json', {channelName: '@id'}, {
    });
});
